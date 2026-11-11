#!/usr/bin/env python3
"""Is an ffmpeg filter chain deterministic? Identical input frames must give identical output frames.

Why
  In ffmpeg 8.1 the `colorlevels` filter on 16-bit RGB (rgb48) returned DIFFERENT values for identical
  input frames. Used for a per-shot exposure offset, it made the colour of most shots flicker from frame to
  frame (up to 18 units of mean chroma, 8-bit scale) and shifted the exposure. `lutrgb` is clean. Test every
  new chain once, before you render the edit.

What it measures (two tests, both on a few real frames)
  A. RUN TWICE: the same N frames through the chain in two separate ffmpeg runs; max absolute pixel difference.
  B. REPEAT ONE FRAME: one decoded frame repeated N times through the chain (a 24p clip on a 30p timeline
     repeats frames in just this way); number of distinct output frames and the max difference from frame 0.

Gate value
  Max difference must be 0 in both tests (bit-identical). Anything else prints NOT DETERMINISTIC and exits 1.
  Differences are reported in output units (16-bit for rgb48le, 8-bit for rgb24) and on an 8-bit scale.

Usage
  determinism_check.py clip.MP4 --vf "format=rgb48le,lutrgb=r=clip(val+0.04*maxval\\,minval\\,maxval):g=val:b=val"
  determinism_check.py clip.MP4 --vf "format=rgb48le,colorlevels=rimin=0.04:gimin=0.04:bimin=0.04" --pre scale=960:540
  Include the format conversions the real chain uses, and test the chain exactly as you will render it.
  Escape a comma inside a filter option with a backslash. Options: --frames N, --start SECONDS, --out-pix-fmt.

Needs: numpy, ffmpeg and ffprobe on PATH. Frames are written to a temp dir: 1080p rgb48 is 12 MB a frame, so use
--pre scale=... or fewer --frames for 4K input.
"""
import argparse
import hashlib
import os
import subprocess
import sys
import tempfile

import numpy as np


def run_chain(video, vf, out, start, frames, out_pix_fmt, ffmpeg_extra=()):
    cmd = ['ffmpeg', '-v', 'error', '-y', '-nostdin', '-ss', f'{start:.4f}', '-i', video, '-an', '-vf', vf,
           '-frames:v', str(frames), '-fps_mode', 'passthrough', '-pix_fmt', out_pix_fmt, '-f', 'rawvideo', *ffmpeg_extra, out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'ffmpeg failed:\n{r.stderr[-600:]}\ncommand: {" ".join(cmd)}')


def load(path, n, dtype):
    raw = np.fromfile(path, dtype=dtype)
    if n == 0 or raw.size % n:
        sys.exit(f'{path}: {raw.size} samples do not split into {n} frames (fewer frames decoded than requested?)')
    return raw.reshape(n, -1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', help='input video (a few frames of it are used)')
    ap.add_argument('--vf', required=True, help='the filter chain to test, as for ffmpeg -vf')
    ap.add_argument('--pre', default='', help='filter applied before the chain on both tests, e.g. scale=960:540 (default: none)')
    ap.add_argument('--frames', type=int, default=12, help='frames per test (default 12)')
    ap.add_argument('--start', type=float, default=1.0, help='start time in seconds (default 1.0)')
    ap.add_argument('--out-pix-fmt', default='rgb48le', help='pixel format of the compared output (default rgb48le: 16-bit, hides nothing)')
    a = ap.parse_args()
    dtype = np.uint16 if ('16' in a.out_pix_fmt or '48' in a.out_pix_fmt) else np.uint8
    scale8 = 257.0 if dtype == np.uint16 else 1.0
    pre = (a.pre + ',') if a.pre else ''
    N = a.frames
    bad = []

    with tempfile.TemporaryDirectory(prefix='determinism_') as tmp:
        p1, p2 = os.path.join(tmp, 'run1.raw'), os.path.join(tmp, 'run2.raw')
        run_chain(a.video, pre + a.vf, p1, a.start, N, a.out_pix_fmt)
        run_chain(a.video, pre + a.vf, p2, a.start, N, a.out_pix_fmt)
        x, y = load(p1, N, dtype), load(p2, N, dtype)
        d = np.abs(x.astype(np.int64) - y.astype(np.int64))
        per_frame = d.max(axis=1)
        mx = int(per_frame.max())
        print(f'A  run twice          : {N} frames, max pixel difference {mx} ({mx / scale8:.3f} on an 8-bit scale), '
              f'{int((per_frame > 0).sum())} frames differ')
        if mx:
            bad.append('run twice')
        os.remove(p2)

        # B: one decoded frame repeated N times, through the same chain. trim + loop reproduce the exact decoded frame.
        rep = f'trim=start_frame=0:end_frame=1,loop=loop={N - 1}:size=1,setpts=N/FRAME_RATE/TB,'
        p3 = os.path.join(tmp, 'rep.raw')
        run_chain(a.video, pre + rep + a.vf, p3, a.start, N, a.out_pix_fmt)
        z = load(p3, N, dtype)
        hashes = [hashlib.md5(f.tobytes()).hexdigest() for f in z]
        distinct = len(set(hashes))
        dz = np.abs(z.astype(np.int64) - z[0].astype(np.int64)).max(axis=1)
        print(f'B  one frame x {N:<3d}     : {distinct} distinct output frame(s), max difference from frame 0 {int(dz.max())} '
              f'({dz.max() / scale8:.3f} on an 8-bit scale)')
        if distinct != 1:
            bad.append('repeated frame')
            print('   frames that differ from frame 0:', [int(i) for i in np.nonzero(dz)[0]])

    if bad:
        print('RESULT NOT DETERMINISTIC: ' + ', '.join(bad))
        sys.exit(1)
    print('RESULT deterministic (bit-identical in both tests)')


if __name__ == '__main__':
    main()
