#!/usr/bin/env python3
"""Wobble ("warp") and blur-swing measure for rendered or stabilized shots.

What it measures
  Per consecutive frame pair (640x360 grey): LK feature flow, RANSAC full affine, and the part of that
  affine a rigid move cannot explain (shear + uneven scale) as px of distortion at the frame edge, scaled
  to 1080p. Rolling shutter turns camera shake into exactly this distortion, and a stabilized frame makes
  it visible as wobble. Also the frame-to-frame swing in sharpness (log change in Laplacian variance:
  motion blur that pulses with shake).
  Run it on the RENDERED shot (after stabilization), not the raw clip.

Gate value
  blur_swing_p90 <= 0.35 (BLUR_SWING_GATE; calibrated on a Sony A7IV 4K -> 1080p job, 2026-10). warp_* has no
  hard gate: use it to compare renders of the same shot (lower is better) and to rank shots. On the job it
  was calibrated on, the median shot had warp_rms 1.65 px and the worst 7.8 px.

Output (one line per file; --json writes the same rows)
  {"file", "warp_rms", "warp_p90", "warp_max" (px at 1080p), "blur_swing_p90"}

Usage
  warp_scan.py shot1.mp4 shot2.mp4
  warp_scan.py shot.mp4 --max-frames 120 --json warp.json

Needs: numpy, opencv-python. Frames are held in memory (640x360 grey): trim long clips first.
"""
import argparse
import json
import os
import pathlib
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import cv2

W, H = 640, 360
SCALE = 1080 / H
BLUR_SWING_GATE = 0.35          # p90 of frame-to-frame log sharpness change (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)


def pair_distortion(a, b):
    p0 = cv2.goodFeaturesToTrack(a, 600, 0.01, 8, blockSize=7)
    if p0 is None or len(p0) < 30:
        return None
    p1, st, _ = cv2.calcOpticalFlowPyrLK(a, b, p0, None, winSize=(21, 21), maxLevel=3)
    ok = st.ravel() == 1
    pb, stb, _ = cv2.calcOpticalFlowPyrLK(b, a, p1[ok], None, winSize=(21, 21), maxLevel=3)
    good = (stb.ravel() == 1) & (np.linalg.norm((pb - p0[ok]).reshape(-1, 2), axis=1) < 0.7)
    q0, q1 = p0[ok][good].reshape(-1, 2), p1[ok][good].reshape(-1, 2)
    if len(q0) < 30:
        return None
    c = np.array([W / 2, H / 2])
    A, inl = cv2.estimateAffine2D(q0 - c, q1 - c, method=cv2.RANSAC, ransacReprojThreshold=1.0, maxIters=3000)
    if A is None or inl.sum() < 25:
        return None
    a_, b_, c_, d_ = A[0, 0], A[0, 1], A[1, 0], A[1, 1]
    # non-similarity part: uneven scale (a-d)/2 and shear (b+c)/2; edge displacement over half the height/width
    return float(np.hypot((a_ - d_) / 2 * W / 2, (b_ + c_) / 2 * H / 2) * SCALE * 2)


def scan(args):
    path, max_frames = args
    cap = cv2.VideoCapture(str(path))
    frames = []
    while max_frames is None or len(frames) < max_frames:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (W, H), interpolation=cv2.INTER_AREA))
    if len(frames) < 3:
        return dict(file=str(path), error='fewer than 3 frames decoded')
    d = [pair_distortion(frames[i], frames[i + 1]) for i in range(len(frames) - 1)]
    d = np.array([x for x in d if x is not None] or [0.0])
    sharp = np.array([cv2.Laplacian(f, cv2.CV_32F).var() for f in frames])
    swing = np.abs(np.diff(np.log(sharp + 1e-6)))           # frame-to-frame change in sharpness
    return dict(file=str(path), warp_rms=round(float(np.sqrt((d ** 2).mean())), 2), warp_p90=round(float(np.percentile(d, 90)), 2),
                warp_max=round(float(d.max()), 2), blur_swing_p90=round(float(np.percentile(swing, 90)), 3))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+', help='video file(s) to scan')
    ap.add_argument('--max-frames', type=int, help='scan only the first N frames of each file')
    ap.add_argument('--workers', type=int, default=min(4, os.cpu_count() or 1), help='parallel files (default min(4, cpus))')
    ap.add_argument('--json', help='also write the rows to this JSON file')
    a = ap.parse_args()
    jobs = [(pathlib.Path(f), a.max_frames) for f in a.files]
    if a.workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(a.workers) as ex:
            rows = list(ex.map(scan, jobs))
    else:
        rows = [scan(j) for j in jobs]
    if a.json:
        json.dump(rows, open(a.json, 'w'), indent=1)
    for r in rows:
        over = r.get('blur_swing_p90', 0) > BLUR_SWING_GATE
        print(r, '  BLUR SWING OVER GATE' if over else '')


if __name__ == '__main__':
    main()
