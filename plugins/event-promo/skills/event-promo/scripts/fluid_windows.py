#!/usr/bin/env python3
"""Find clip windows with one fluid, continuous camera move (no start/stop, no re-aim).

What it measures
  Input: motion profiles from motion_profile.py (a directory of <clip>.json). Each source frame gets a
  velocity vector [pan x, pan y, roll, zoom] in px/frame at 640x360 (roll and zoom as the motion they
  cause at the frame corner), smoothed over 0.25 s. A window's UNEVENNESS is the largest distance of its
  velocity from the window's mean velocity, divided by its mean speed (with a floor, so near-hovers do
  not blow up). 0 = perfectly constant move; mechanical stop-and-go moves score high.

Gate value
  unevenness <= 0.35 (MAX_UNEVEN); the `windows` command only returns windows under it. Shots in the
  finished promo were all <= 0.15 once picked with this tool.

Usage
  fluid_windows.py PROFILE_DIR score CLIP T0 T1          unevenness and speed of source seconds T0..T1
  fluid_windows.py PROFILE_DIR timeline CLIP [T0 T1]     velocity every 0.5 s
  fluid_windows.py PROFILE_DIR windows SECONDS [CLIP..]  best fluid windows of that source length
  fluid_windows.py PROFILE_DIR check SHOTS.json          score every shot in a JSON list
      SHOTS.json minimal shape: [{"clip": "clip", "src_in": 3.0, "src_out": 6.5}, ...]
  CLIP is the profile file stem (clip.MP4 -> clip). Example:
  fluid_windows.py profiles/ windows 3.0 drone_clip

Needs: numpy.
"""
import argparse
import json
import pathlib
import sys

import numpy as np

R = float(np.hypot(320, 180))      # corner radius at 640x360
SPEED_FLOOR = 0.6                  # px/frame; below this a move reads as a hover  (calibrated on a 4K drone job, 2026-10)
SMOOTH_S = 0.25                    # s, velocity smoothing                           (calibrated on a 4K drone job, 2026-10)
MAX_UNEVEN = 0.35                  # gate for `windows`                              (calibrated on a 4K drone job, 2026-10)
MIN_INLIERS = 10                   # fewer RANSAC inliers = failed track


def gsmooth1(x, sigma):
    p = int(3 * sigma + 0.5)
    k = np.exp(-0.5 * (np.arange(-p, p + 1) / sigma) ** 2)
    k /= k.sum()
    xp = np.pad(x, ((p, p), (0, 0)), mode='edge')
    return np.stack([np.convolve(xp[:, j], k, mode='valid') for j in range(x.shape[1])], 1)


def load_profile(pdir, clip):
    """-> steps (n,4), inliers (n,), fps, t0. Reads <clip>.json (motion_profile.py) or a legacy <clip>.npz."""
    j = pathlib.Path(pdir) / f'{clip}.json'
    if j.exists():
        d = json.load(open(j))
        return np.array(d['steps'], dtype=float), np.array(d['inliers']), float(d['fps']), float(d.get('t0', 0.0))
    z = pathlib.Path(pdir) / f'{clip}.npz'
    if z.exists():
        d = np.load(z)
        return d['steps'].astype(float), d['inliers'], float(d['fps']), 0.0
    sys.exit(f'no profile {j} (run motion_profile.py first)')


def velocity(pdir, clip):
    st, inl, fps, t0 = load_profile(pdir, clip)
    st = st.copy()
    bad = inl < MIN_INLIERS                         # failed track: borrow the neighbours' motion
    if bad.any() and (~bad).any():
        idx = np.arange(len(st))
        for c in range(4):
            st[bad, c] = np.interp(idx[bad], idx[~bad], st[~bad, c])
    v = np.stack([st[:, 0], st[:, 1], st[:, 2] * R, st[:, 3] * R], 1)
    return gsmooth1(v, SMOOTH_S * fps), fps, t0


def unevenness(v):
    m = v.mean(0)
    return float(np.linalg.norm(v - m, axis=1).max() / max(np.linalg.norm(m), SPEED_FLOOR)), float(np.linalg.norm(m))


def score(pdir, clip, t0, t1):
    v, fps, p0 = velocity(pdir, clip)
    a, b = int(round((t0 - p0) * fps)), int(round((t1 - p0) * fps))
    return unevenness(v[max(0, a):min(len(v), b)])


def windows(pdir, length, clips=None, step=0.5, top=4, max_uneven=MAX_UNEVEN):
    """Per clip, the best non-overlapping windows of `length` source seconds: (clip, start_s, unevenness, speed)."""
    clips = clips or sorted(p.stem for p in pathlib.Path(pdir).glob('*.json'))
    rows = []
    for c in clips:
        v, fps, p0 = velocity(pdir, c)
        n = int(round(length * fps))
        cand = []
        for a in range(0, len(v) - n, int(step * fps)):
            u, sp = unevenness(v[a:a + n])
            if u <= max_uneven:
                cand.append((u, p0 + a / fps, sp))
        cand.sort()
        taken = []
        for u, t, sp in cand:
            if all(abs(t - t2) >= length for _, t2, _ in taken):
                taken.append((u, t, sp))
            if len(taken) == top:
                break
        rows += [(c, t, u, sp) for u, t, sp in taken]
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('profiles', help='directory of motion profiles from motion_profile.py')
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('score', help='unevenness of one window')
    s.add_argument('clip'); s.add_argument('t0', type=float); s.add_argument('t1', type=float)
    s = sub.add_parser('timeline', help='motion of one clip every 0.5 s')
    s.add_argument('clip'); s.add_argument('t0', type=float, nargs='?', default=0.0); s.add_argument('t1', type=float, nargs='?')
    s = sub.add_parser('windows', help='best fluid windows of a given length')
    s.add_argument('seconds', type=float); s.add_argument('clips', nargs='*')
    s.add_argument('--top', type=int, default=4, help='windows per clip (default 4)')
    s.add_argument('--max-uneven', type=float, default=MAX_UNEVEN, help=f'unevenness gate (default {MAX_UNEVEN})')
    s = sub.add_parser('check', help='score every shot in a JSON list')
    s.add_argument('shots', help='JSON list of {"clip", "src_in", "src_out"}')
    a = ap.parse_args()

    if a.cmd == 'score':
        u, sp = score(a.profiles, a.clip, a.t0, a.t1)
        print(f'{a.clip} {a.t0:.2f}-{a.t1:.2f}s  unevenness {u:.2f}  speed {sp:.2f}' + ('  OVER' if u > MAX_UNEVEN else ''))
    elif a.cmd == 'timeline':
        v, fps, p0 = velocity(a.profiles, a.clip)
        t1 = a.t1 or p0 + len(v) / fps
        for t in np.arange(a.t0, t1, 0.5):
            i = int(round((t - p0) * fps))
            if i < 0 or i >= len(v):
                continue
            x = v[i]
            print(f'{a.clip} {t:6.1f}s  speed {np.linalg.norm(x):5.2f}  pan {x[0]:+5.2f},{x[1]:+5.2f}  roll {x[2]:+5.2f}  zoom {x[3]:+5.2f}')
    elif a.cmd == 'windows':
        for c, t, u, sp in windows(a.profiles, a.seconds, a.clips or None, top=a.top, max_uneven=a.max_uneven):
            print(f'{c} {t:6.1f}-{t + a.seconds:6.1f}s  unevenness {u:.2f}  speed {sp:.2f}')
    elif a.cmd == 'check':
        for k, s in enumerate(json.load(open(a.shots))):
            u, sp = score(a.profiles, s['clip'], s['src_in'], s['src_out'])
            print(f"{k:2d} {s['clip']}  src {s['src_in']:6.2f}-{s['src_out']:6.2f}  unevenness {u:5.2f}  speed {sp:4.2f}"
                  + ('  OVER' if u > MAX_UNEVEN else ''))


if __name__ == '__main__':
    main()
