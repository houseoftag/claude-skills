#!/usr/bin/env python3
"""Gyroflow pre-stabilization of one clip range: trimmed project + CLI render.

Why
  Rolling-shutter "jello" (picture bends like jelly) cannot be removed by an image-based 2D stabilizer.
  Gyroflow uses the camera's own gyro data (about 2 kHz), the frame readout time and the lens profile to
  correct each sensor row. On the job this was calibrated on, it cut the band-bend jello by 69 %.

What it does
  1. Asks the Gyroflow CLI for a default project (done on a symlink in a temp dir, so nothing is written
     next to your footage).
  2. Sets one trim range = IN-MARGIN .. OUT+MARGIN (start snapped to a source frame), so smoothing and the
     auto-zoom only see the part that is used (trim_range_only = 1). Default margin 1.0 s.
  3. Sets smoothness (0.5 normal, 1.0 for a locked-off look) and the output: H.265/HEVC 10-bit by default.
     ProRes is NOT the default: it was about 80 MB/s at 60p and about 6x bigger, and Gyroflow's ProRes
     rescales the camera's full-range values to video range, while its H.265 keeps the original code values,
     so downstream tools read the file exactly like the camera file.
  4. Renders with the Gyroflow CLI. The output covers IN-MARGIN..OUT+MARGIN: trim it later to IN..OUT.

Gate value
  None (a render step). Check the result with warp_scan.py and by eye.

Usage
  gyro_render.py clip.MP4 --in 12.0 --out 15.5 stabilized.mp4
  gyro_render.py clip.MP4 --in 12.0 --out 15.5 stabilized.mp4 --smooth 1.0 --size 1920x1080 --no-gpu
  Gyroflow CLI path: --gyroflow, or env GYROFLOW; default /Applications/Gyroflow.app/Contents/MacOS/gyroflow

Needs: Gyroflow 1.6+ CLI, ffprobe on PATH. The clip must carry gyro data (Sony, GoPro, DJI, ...) and a matching
lens profile must be available to Gyroflow.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

DEFAULT_GYROFLOW = '/Applications/Gyroflow.app/Contents/MacOS/gyroflow'
MARGIN = 1.0                           # s of context each side of the used range (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)
SMOOTH = 0.5                           # smoothness of the horizon/aim (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)
SMOOTH_LOCK = 1.0                      # maximum smoothing for locked-off shots (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)
CODEC = 'H.265/HEVC'                   # not ProRes: see the docstring
BITRATE = 150                          # Mbps (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10)


def probe(src):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                          'stream=avg_frame_rate:format=duration', '-of', 'json', str(src)], capture_output=True, text=True).stdout
    try:
        d = json.loads(out)
        a, b = d['streams'][0]['avg_frame_rate'].split('/')
        return float(a) / float(b), float(d['format']['duration'])
    except (ValueError, KeyError, IndexError):
        sys.exit(f'ffprobe could not read {src}')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('clip', help='source clip with gyro data')
    ap.add_argument('output', help='output video path (.mp4 or .mov)')
    ap.add_argument('--in', dest='t_in', type=float, required=True, help='first used source second')
    ap.add_argument('--out', dest='t_out', type=float, required=True, help='last used source second')
    ap.add_argument('--margin', type=float, default=MARGIN, help=f'seconds of context each side (default {MARGIN})')
    ap.add_argument('--smooth', type=float, default=SMOOTH, help=f'smoothness (default {SMOOTH}; {SMOOTH_LOCK} = locked-off)')
    ap.add_argument('--codec', default=CODEC, help=f'Gyroflow codec name (default {CODEC!r})')
    ap.add_argument('--bitrate', type=int, default=BITRATE, help=f'Mbps (default {BITRATE})')
    ap.add_argument('--size', help='output size WxH (default: source size)')
    ap.add_argument('--no-gpu', action='store_true', help='render without the GPU')
    ap.add_argument('--audio', action='store_true', help='keep the audio (default: no audio)')
    ap.add_argument('--gyroflow', default=os.environ.get('GYROFLOW', DEFAULT_GYROFLOW), help='Gyroflow CLI path')
    ap.add_argument('--keep-project', action='store_true', help='keep <output>.gyroflow next to the output')
    a = ap.parse_args()

    src = pathlib.Path(a.clip).resolve()
    out = pathlib.Path(a.output).resolve()
    if not src.exists():
        sys.exit(f'no such clip: {src}')
    if not pathlib.Path(a.gyroflow).exists():
        sys.exit(f'Gyroflow CLI not found: {a.gyroflow} (use --gyroflow or env GYROFLOW)')
    if a.t_out <= a.t_in:
        sys.exit('--out must be greater than --in')
    out.parent.mkdir(parents=True, exist_ok=True)
    fps, dur = probe(src)
    t0 = max(0.0, a.t_in - a.margin)
    t1 = min(dur, a.t_out + a.margin)
    t0 = int(t0 * fps) / fps                                       # start on a source frame

    with tempfile.TemporaryDirectory(prefix='gyro_render_') as tmp:
        tmp = pathlib.Path(tmp)
        link = tmp / src.name
        link.symlink_to(src)
        # Gyroflow writes the default project next to the video: do it on the symlink, not in the footage folder.
        r = subprocess.run([a.gyroflow, str(link), '--export-project', '1', '-f'], capture_output=True, text=True, cwd=tmp)
        proj_default = link.with_suffix('.gyroflow')
        if not proj_default.exists():
            sys.exit('Gyroflow did not write a project (no gyro data or unsupported clip?):\n' + (r.stderr or r.stdout)[-400:])
        p = json.load(open(proj_default))
        proj_default.unlink()
        p['trim_ranges_ms'] = [[t0 * 1000.0, t1 * 1000.0]]
        for sp in p['stabilization']['smoothing_params']:
            if sp['name'] in ('smoothness', 'smoothness_pitch', 'smoothness_yaw', 'smoothness_roll'):
                sp['value'] = a.smooth
            if sp['name'] == 'trim_range_only':
                sp['value'] = 1.0
        p['output'].update(codec=a.codec, bitrate=a.bitrate, use_gpu=not a.no_gpu, audio=a.audio,
                           output_folder=out.parent.as_uri() + '/', output_filename=out.name, export_trims_separately=False)
        if a.size:
            w, h = (int(v) for v in a.size.lower().split('x'))
            p['output'].update(output_width=w, output_height=h)
        proj = tmp / f'{out.stem}.gyroflow'
        json.dump(p, open(proj, 'w'), indent=1)
        r = subprocess.run([a.gyroflow, str(proj), '-f'], capture_output=True, text=True)
        if a.keep_project:
            p['videofile'] = p['output']['input_url'] = src.as_uri()    # the temp symlink is gone after this run
            json.dump(p, open(out.parent / f'{out.name}.gyroflow', 'w'), indent=1)
        if r.returncode != 0 or not out.exists():
            sys.exit('Gyroflow render FAILED:\n' + (r.stderr or r.stdout)[-600:])
    print(f'rendered {out} : source {t0:.3f}-{t1:.3f}s of {src.name} ({fps:.3f} fps), smooth {a.smooth}, {a.codec}')


if __name__ == '__main__':
    main()
