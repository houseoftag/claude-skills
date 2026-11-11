#!/usr/bin/env python3
"""Story sheet: one frame per shot, in order, labelled with shot id and timecode -> JPEG contact sheet(s).

What it is for
  Read the cut as a viewer would, for place, time and story order, and spot weak shots (wrong subject, blur
  in the foreground, a repeated place). Frames are chosen by FRAME INDEX with `select=eq(n,...)` and
  `-fps_mode passthrough`, never by seek time: seeking by time lands on the wrong frame in long-GOP and
  mixed-frame-rate files, and a duplicated or dropped frame shifts every later tile.

Gate value
  None (a review aid). Check that every shot's subject is readable and that nothing in the foreground is blurred.

Shots JSON (minimal shape; frames of the EXPORT, f0 inclusive, f1 exclusive; "clip"/"id" optional)
  {"shots": [{"f0": 0, "f1": 87, "clip": "clip_a"}, {"f0": 87, "f1": 140, "clip": "clip_b"}]}
  or a bare list of the same objects.

Usage
  story_sheet.py export.mp4 --shots shots.json --out review/story
      -> review/story_0.jpg, review/story_1.jpg ... (24 shots per sheet by default)
  story_sheet.py export.mp4 --shots shots.json --out story --at first --cols 6 --width 320

Needs: Pillow, ffmpeg and ffprobe on PATH.
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = ['/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf', '/System/Library/Fonts/Helvetica.ttc',
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'Arial.ttf']


def font(size):
    for f in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def probe(video):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,nb_frames,width,height',
                          '-of', 'json', video], capture_output=True, text=True).stdout
    try:
        s = json.loads(out)['streams'][0]
    except (ValueError, KeyError, IndexError):
        sys.exit(f'ffprobe could not read {video}')
    n, d = s['r_frame_rate'].split('/')
    return float(n) / float(d), s


def timecode(frame, fps):
    base = int(round(fps))
    s, f = divmod(frame, base)
    return f'{s // 3600:02d}:{s // 60 % 60:02d}:{s % 60:02d}:{f:02d}' if s >= 3600 else f'{s // 60:02d}:{s % 60:02d}:{f:02d}'


def pick(shot, at):
    f0, f1 = shot['f0'], shot['f1']
    return {'first': f0, 'mid': (f0 + f1) // 2, 'last': f1 - 1}[at]


def grab_frames(video, frames, width, height, tmp):
    """Decode once, keep exactly the given frame indices (ascending), in order."""
    idx = sorted(set(frames))
    # a long select expression goes in a filter script file: no shell or command-line length limits
    script = pathlib.Path(tmp) / 'sel.txt'
    script.write_text("select='" + '+'.join(f'eq(n\\,{n})' for n in idx) + f"',scale={width}:{height}")
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-an', '-filter_script:v', str(script),
                        '-fps_mode', 'passthrough', str(pathlib.Path(tmp) / 'f_%05d.png')], capture_output=True, text=True)
    files = sorted(pathlib.Path(tmp).glob('f_*.png'))
    if r.returncode != 0 or len(files) != len(idx):
        sys.exit(f'expected {len(idx)} frames, got {len(files)} (shots past the end of the file?)\n{r.stderr[-300:]}')
    return {n: Image.open(f).convert('RGB') for n, f in zip(idx, files)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', help='exported video')
    ap.add_argument('--shots', required=True, help='shots JSON (frame boundaries of the export)')
    ap.add_argument('--out', required=True, help='output prefix: <prefix>_0.jpg, <prefix>_1.jpg, ...')
    ap.add_argument('--at', choices=['first', 'mid', 'last'], default='mid', help='which frame of each shot (default mid)')
    ap.add_argument('--cols', type=int, default=4, help='tiles per row (default 4)')
    ap.add_argument('--width', type=int, default=480, help='tile width in px (default 480; height keeps the video aspect)')
    ap.add_argument('--per-sheet', type=int, default=24, help='shots per sheet (default 24)')
    ap.add_argument('--fps', type=float, help='timeline frame rate for timecodes (default: probed)')
    ap.add_argument('--quality', type=int, default=82, help='JPEG quality (default 82)')
    a = ap.parse_args()

    fps, s = probe(a.video)
    fps = a.fps or fps
    d = json.load(open(a.shots))
    shots = d['shots'] if isinstance(d, dict) else d
    if not shots:
        sys.exit('no shots in the shots JSON')
    w = a.width
    h = int(round(w * int(s['height']) / int(s['width']) / 2)) * 2
    frames = [pick(sh, a.at) for sh in shots]
    with tempfile.TemporaryDirectory(prefix='story_sheet_') as tmp:
        imgs = grab_frames(a.video, frames, w, h, tmp)
        F, pad = font(max(12, w // 28)), max(18, w // 22)
        out = pathlib.Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        for part in range(0, len(shots), a.per_sheet):
            chunk = list(range(part, min(part + a.per_sheet, len(shots))))
            rows = (len(chunk) + a.cols - 1) // a.cols
            im = Image.new('RGB', (a.cols * w, rows * (h + pad)), (12, 12, 12))
            dr = ImageDraw.Draw(im)
            for k, i in enumerate(chunk):
                x, y = (k % a.cols) * w, (k // a.cols) * (h + pad)
                im.paste(imgs[frames[i]], (x, y))
                sh = shots[i]
                label = f"#{sh.get('id', i)} {sh.get('clip', '')}".rstrip() + f'  {timecode(sh["f0"], fps)}'
                dr.text((x + 3, y + h + 2), label, font=F, fill=(255, 220, 90))
            name = f'{out}_{part // a.per_sheet}.jpg'
            im.save(name, quality=a.quality)
            print(name, f'{len(chunk)} shots')


if __name__ == '__main__':
    main()
