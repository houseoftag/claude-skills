#!/usr/bin/env python3
"""Pick camera windows a stabilizer can clean: low FAST shake, so no rolling-shutter wobble or blur pulse.

What it measures
  Predicted rolling-shutter lean, in 1080p px: the fast (shake) part of the image velocity (velocity minus
  its 0.25 s Gaussian smoothing, so intentional moves drop out) times the sensor readout time. A
  stabilizer removes frame shake but not this lean or the matching motion blur, so a stabilized frame shows
  them as "warp". Input: motion profiles from motion_profile.py (directory of <clip>.json).

Gate value
  window lean rms <= 3.0 px and max <= 8.0 px (GATE_RMS, GATE_MAX). On the job it was calibrated on, the 9
  shots a reviewer flagged were the 9 highest-scoring of the cut; the first shot he did not flag scored 3.9 px.

Sensor readout time (the one camera-specific input)
  READOUT_S below is CALIBRATED FOR THE SONY A7IV (4K full-frame 24p, oversampled: ~26 ms; 4K S35 60p: ~15 ms).
  Any other camera: measure its readout time and pass --readout-ms. A frame rate with no table entry stops
  with an error instead of guessing. (Gyroflow reports a 26.8 ms readout for the A7IV at 24p; the gate was
  calibrated with 26 ms.)

Usage
  shake_gate.py PROFILE_DIR check SHOTS.json              score every shot in a JSON list
      SHOTS.json minimal shape: [{"clip": "clip", "src_in": 3.0, "src_out": 6.5}, ...]
  shake_gate.py PROFILE_DIR best CLIP SECONDS [N]         calmest N windows of that length in one clip
  shake_gate.py PROFILE_DIR series CLIP                   lean every 0.25 s across a clip
  shake_gate.py PROFILE_DIR check shots.json --readout-ms 18    other camera

Needs: numpy.
"""
import argparse
import json
import pathlib
import sys

import numpy as np

# Sensor readout time by frame rate, seconds. CALIBRATED FOR THE SONY A7IV (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10).
READOUT_S = {23.976: 0.026, 59.94: 0.015}
TO_1080 = 1920 / 640               # profiles are measured at 640 px wide
GATE_RMS, GATE_MAX = 3.0, 8.0      # px of predicted lean (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)
SMOOTH_S = 0.25                    # s, split between intentional move and shake (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)
MIN_INLIERS = 10                   # fewer RANSAC inliers = failed track


def readout_for(fps, override_ms=None):
    if override_ms is not None:
        return override_ms / 1000.0
    k = min(READOUT_S, key=lambda f: abs(f - fps))
    if abs(k - fps) > 0.5:
        sys.exit(f'no default readout time for {fps:.3f} fps (table: {sorted(READOUT_S)}, Sony A7IV only); pass --readout-ms')
    return READOUT_S[k]


def _smooth(x, sigma):
    p = int(3 * sigma + 0.5)
    k = np.exp(-0.5 * (np.arange(-p, p + 1) / sigma) ** 2)
    k /= k.sum()
    xp = np.pad(x, ((p, p), (0, 0)), mode='edge')
    return np.stack([np.convolve(xp[:, j], k, mode='valid') for j in range(x.shape[1])], 1)


def load_profile(pdir, clip):
    j = pathlib.Path(pdir) / f'{clip}.json'
    if j.exists():
        d = json.load(open(j))
        return np.array(d['steps'], dtype=float), np.array(d['inliers']), float(d['fps']), float(d.get('t0', 0.0))
    z = pathlib.Path(pdir) / f'{clip}.npz'
    if z.exists():
        d = np.load(z)
        return d['steps'].astype(float), d['inliers'], float(d['fps']), 0.0
    sys.exit(f'no profile {j} (run motion_profile.py first)')


def lean_series(pdir, clip, readout_ms=None):
    """Predicted lean (px) per source frame, the clip fps, and the profile start time."""
    steps, inl, fps, t0 = load_profile(pdir, clip)
    st = steps[:, :2].copy()
    bad = inl < MIN_INLIERS
    if bad.any() and (~bad).any():
        idx = np.arange(len(st))
        for c in range(2):
            st[bad, c] = np.interp(idx[bad], idx[~bad], st[~bad, c])
    v = st * fps * TO_1080                           # px/s at 1080p
    hv = v - _smooth(v, SMOOTH_S * fps)              # keep the shake, drop intentional moves
    return np.linalg.norm(hv, axis=1) * readout_for(fps, readout_ms), fps, t0


def score(pdir, clip, t0, t1, readout_ms=None):
    s, fps, p0 = lean_series(pdir, clip, readout_ms)
    a = int((t0 - p0) * fps)
    w = s[max(0, a):max(a + 1, int((t1 - p0) * fps))]
    return float(np.sqrt((w ** 2).mean())), float(w.max())


def best(pdir, clip, length, n=3, step=0.1, readout_ms=None):
    s, fps, p0 = lean_series(pdir, clip, readout_ms)
    L = int(round(length * fps))
    rows = []
    for a in range(0, max(1, len(s) - L + 1), max(1, int(step * fps))):
        w = s[a:a + L]
        rows.append((float(np.sqrt((w ** 2).mean())), float(w.max()), p0 + a / fps))
    rows.sort()
    picked = []
    for r in rows:
        if all(abs(r[2] - p[2]) >= length / 2 for p in picked):
            picked.append(r)
        if len(picked) == n:
            break
    return picked


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('profiles', help='directory of motion profiles from motion_profile.py')
    ap.add_argument('--readout-ms', type=float, help='sensor readout time in ms (default: Sony A7IV table by frame rate)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('check', help='score every shot in a JSON list')
    s.add_argument('shots', help='JSON list of {"clip", "src_in", "src_out"}')
    s = sub.add_parser('best', help='calmest windows of a given length in one clip')
    s.add_argument('clip'); s.add_argument('seconds', type=float); s.add_argument('n', type=int, nargs='?', default=3)
    s = sub.add_parser('series', help='lean every 0.25 s across a clip')
    s.add_argument('clip')
    a = ap.parse_args()

    if a.cmd == 'check':
        for k, s in enumerate(json.load(open(a.shots))):
            rms, mx = score(a.profiles, s['clip'], s['src_in'], s['src_out'], a.readout_ms)
            bad = 'OVER' if rms > GATE_RMS or mx > GATE_MAX else ''
            print(f"{k:2d} {s['clip']}  src {s['src_in']:5.2f}-{s['src_out']:5.2f}  lean rms {rms:4.1f} max {mx:5.1f}  {bad}")
    elif a.cmd == 'best':
        for rms, mx, t in best(a.profiles, a.clip, a.seconds, a.n, readout_ms=a.readout_ms):
            print(f'{a.clip} {t:5.2f}-{t + a.seconds:5.2f}  lean rms {rms:4.1f} max {mx:5.1f}')
    elif a.cmd == 'series':
        s, fps, p0 = lean_series(a.profiles, a.clip, a.readout_ms)
        q = max(1, int(0.25 * fps))
        for i in range(0, len(s), q):
            print(f'{p0 + i / fps:5.2f}s  lean {s[i:i + q].mean():5.1f} px  ' + '#' * int(s[i:i + q].mean()))


if __name__ == '__main__':
    main()
