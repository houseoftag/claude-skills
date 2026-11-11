#!/usr/bin/env python3
"""Per-frame camera motion of a clip (or a time range of it) -> JSON profile.

What it measures
  Image motion between consecutive source frames, from a global similarity fit (LK feature tracks,
  backward check, RANSAC) on 640x360 grey frames. Each step is
      [dx, dy (px at 640x360, about the image centre), roll (rad), log scale]
  plus the RANSAC inlier count per step (0-9 = failed track) and the clip frame rate.
  Works for drone and camera clips alike (the original kept two folders; here you choose the output dir).
  fluid_windows.py (unevenness / fluid windows) and shake_gate.py (predicted rolling-shutter lean)
  both read these profiles.

Gate value
  None: this is a measurement. Downstream tools treat steps with inliers < 10 as failed tracks and
  borrow the neighbours' motion.

Output  <out-dir>/<clip stem>.json
  {"clip", "fps", "t0" (range start, s), "width": 640, "height": 360,
   "steps": [[dx, dy, roll, logscale], ...]  (n_frames - 1 rows),  "inliers": [...]}

Usage
  motion_profile.py clip.MP4 --out-dir profiles/
  motion_profile.py clip.MP4 --out-dir profiles/ --start 12.5 --duration 4    # a few seconds only
  motion_profile.py a.MP4 b.MP4 --out-dir profiles/ --hwaccel videotoolbox

Needs: numpy, opencv-python, ffmpeg/ffprobe on PATH.
"""
import argparse
import json
import pathlib
import subprocess
import sys

import numpy as np
import cv2

W, H = 640, 360                       # analysis frame size


class Tracker:
    """Frame-to-frame global motion (similarity) on ~640 px grayscale frames."""

    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.c = np.array([(w - 1) / 2, (h - 1) / 2])
        self.prev = None
        self.cum = np.zeros(4)
        self.rows = []
        self.inliers = []
        self.dups = []             # True where the frame repeats the previous one (24p source on a 30p timeline)

    def _detect(self, g):
        return cv2.goodFeaturesToTrack(g, maxCorners=500, qualityLevel=0.01, minDistance=10, blockSize=7)

    def update(self, g):
        if self.prev is None:
            self.prev = g
            self.rows.append(self.cum.copy())
            self.inliers.append(0)
            self.dups.append(False)
            return
        step = np.zeros(4)
        n_in = 0
        dup = float(cv2.absdiff(self.prev, g).mean()) < 0.35
        # features are re-detected on the previous frame every step (cheap at 640 px; always enough points)
        p0 = None if dup else self._detect(self.prev)
        if p0 is not None and len(p0) >= 12:
            p1, st, _ = cv2.calcOpticalFlowPyrLK(self.prev, g, p0, None, winSize=(21, 21), maxLevel=3,
                                                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
            ok = st.ravel() == 1
            # backward check rejects unreliable tracks
            if ok.sum() >= 12:
                p0g, p1g = p0[ok], p1[ok]
                pb, stb, _ = cv2.calcOpticalFlowPyrLK(g, self.prev, p1g, None, winSize=(21, 21), maxLevel=3)
                fb = np.linalg.norm((pb - p0g).reshape(-1, 2), axis=1)
                good = (stb.ravel() == 1) & (fb < 1.0)
                if good.sum() >= 12:
                    A, inl = cv2.estimateAffinePartial2D(p0g[good], p1g[good], method=cv2.RANSAC,
                                                         ransacReprojThreshold=1.5, maxIters=2000, confidence=0.995)
                    if A is not None and inl is not None and inl.sum() >= 10:
                        n_in = int(inl.sum())
                        a, b = A[0, 0], A[1, 0]
                        s = float(np.hypot(a, b))
                        th = float(np.arctan2(b, a))
                        R = np.array([[A[0, 0], A[0, 1]], [A[1, 0], A[1, 1]]])
                        tc = R @ self.c + A[:, 2] - self.c      # translation about the image centre
                        step = np.array([tc[0], tc[1], th, np.log(max(s, 1e-3))])
        self.cum = self.cum + step
        self.rows.append(self.cum.copy())
        self.inliers.append(n_in)
        self.dups.append(dup)
        self.prev = g

    def params(self):
        return np.array(self.rows)


def probe_fps(src):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate',
                          '-of', 'csv=p=0', str(src)], capture_output=True, text=True).stdout.strip().split('\n')[0].split(',')[0]
    a, _, b = out.partition('/')
    if not out:
        sys.exit(f'ffprobe could not read {src}')
    return float(a) / float(b or 1)


def profile(path, start=None, duration=None, hwaccel=None):
    fps = probe_fps(path)
    cmd = ['ffmpeg', '-v', 'error', '-nostdin']
    if hwaccel:
        cmd += ['-hwaccel', hwaccel]
    if start:
        cmd += ['-ss', f'{start:.4f}']
    cmd += ['-i', str(path)]
    if duration:
        cmd += ['-t', f'{duration:.4f}']
    cmd += ['-an', '-vf', f'scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 8)
    tr = Tracker()
    while True:
        buf = p.stdout.read(W * H)
        if len(buf) < W * H:
            break
        tr.update(np.frombuffer(buf, np.uint8).reshape(H, W))
    p.wait()
    if len(tr.rows) < 2:
        sys.exit(f'{path}: fewer than 2 frames decoded')
    steps = np.diff(tr.params(), axis=0)
    return dict(clip=pathlib.Path(path).stem, fps=fps, t0=float(start or 0.0), width=W, height=H,
                steps=[[round(float(v), 6) for v in r] for r in steps], inliers=[int(i) for i in tr.inliers[1:]])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('clips', nargs='+', help='video file(s)')
    ap.add_argument('--out-dir', required=True, help='directory for <clip stem>.json profiles')
    ap.add_argument('--start', type=float, help='range start, seconds')
    ap.add_argument('--duration', type=float, help='range length, seconds')
    ap.add_argument('--hwaccel', help='ffmpeg -hwaccel value, e.g. videotoolbox (default: software decode)')
    ap.add_argument('--force', action='store_true', help='overwrite an existing profile (default: skip)')
    a = ap.parse_args()
    out_dir = pathlib.Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for c in a.clips:
        out = out_dir / f'{pathlib.Path(c).stem}.json'
        if out.exists() and not a.force:
            print(out.name, 'cached (use --force to redo)')
            continue
        d = profile(c, a.start, a.duration, a.hwaccel)
        json.dump(d, open(out, 'w'))
        bad = sum(1 for i in d['inliers'] if i < 10)
        print(f"{out.name}: {len(d['steps']) + 1} frames, fps {d['fps']:.3f}, t0 {d['t0']}, failed tracks {bad}")


if __name__ == '__main__':
    main()
