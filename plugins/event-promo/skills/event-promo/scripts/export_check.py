#!/usr/bin/env python3
"""Technical QC of a finished export: frames, decode, black, loudness, A/V match, per-shot flicker, cuts on the beat.

What it measures
  1. frames      decoded frame count == expected (--shots total_frames, else the last shot's f1)
  2. decode      a full decode (`ffmpeg -f null`) prints no errors
  3. black       blackdetect (d=0.1 s, pix_th=0.06): black segments are listed; any that start before
                 --allow-black-after (e.g. the final fade) fail
  4. loudness    integrated LUFS and true peak (ebur128) against the delivery target
  5. av_match    |video duration - audio duration| < one frame
  6. flicker     per shot, the largest one-frame jump in mean Y/U/V: the second difference of the
                 per-frame means from signalstats on 480x270, 8-bit units. A faulty filter once caused chroma
                 spikes up to 18 in most shots; clean shots stay near 1-2.
  7. cuts        every cut (each shot start after the first) lies within one frame of a beat of the grid

Gate values (constants below; the loudness tolerance is a choice made here, the rest were used on a delivered job)
  LUFS -14 +/- 1.0, true peak <= -1.0 dBTP, A/V gap < 1 frame, flicker <= 2.5, cuts within 1 frame of a beat.
  Exit code 1 if any gate fails.

JSON inputs (only the fields below are read; extra fields are ignored)
  --shots shots.json   shots in EXPORT frames, f0 inclusive, f1 exclusive. Either a bare list or an object:
        {"total_frames": 4579,                       <- optional; expected frame count
         "shots": [{"f0": 0, "f1": 87, "clip": "clip_a"}, {"f0": 87, "f1": 140, "clip": "clip_b"}, ...]}
        "clip" is optional (used in the report). Without --shots, only checks 2-5 run.
  --beats beats.json   either a bare list of beat times in seconds, or an object with a "beats" list
        (the grid written by beat_grid.py has this shape). Needed for check 7.

Usage
  export_check.py export.mp4
  export_check.py export.mp4 --shots shots.json --beats grid.json --allow-black-after 150 --json report.json

Needs: ffmpeg and ffprobe on PATH. Takes a few passes over the file (decode, blackdetect, loudness, signalstats).
"""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

LUFS_TARGET, LUFS_TOL = -14.0, 1.0   # social-video delivery target; tolerance chosen here
TRUE_PEAK_MAX = -1.0                 # dBTP
FLICKER_MAX = 2.5                    # 8-bit units (calibrated on a Sony A7IV 4K -> 1080p job, 2026-10: clean exports worst 1.0-2.3, faulty filter chain median 3.2, worst 18.5)
FLICKER_MIN_FRAMES = 5               # shorter shots are skipped
STATS_SIZE = '480:270'               # signalstats resolution


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def load_shots(path):
    d = json.load(open(path))
    shots = d['shots'] if isinstance(d, dict) else d
    total = d.get('total_frames') if isinstance(d, dict) else None
    return shots, (total if total is not None else (shots[-1]['f1'] if shots else None))


def load_beats(path):
    d = json.load(open(path))
    return d['beats'] if isinstance(d, dict) else d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video', help='exported video file')
    ap.add_argument('--shots', help='shots JSON (frame boundaries of the export)')
    ap.add_argument('--beats', help='beats JSON (grid)')
    ap.add_argument('--fps', type=float, help='timeline frame rate (default: probed from the file)')
    ap.add_argument('--allow-black-after', type=float, metavar='SEC', help='black segments starting at or after SEC are allowed (end fade)')
    ap.add_argument('--include-last-shot', action='store_true', help='also check flicker in the last shot (skipped by default: it holds the end-card fade)')
    ap.add_argument('--json', help='write the full report here')
    a = ap.parse_args()

    res, fails = {}, []

    def gate(name, ok, detail):
        res[name] = dict(ok=bool(ok), **detail)
        print(f"{'PASS' if ok else 'FAIL'}  {name:10s} {detail}")
        if not ok:
            fails.append(name)

    p = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                        'stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,duration',
                        '-show_entries', 'format=duration', '-of', 'json', a.video]).stdout or '{}')
    v = next((s for s in p.get('streams', []) if s['codec_type'] == 'video'), None)
    au = next((s for s in p.get('streams', []) if s['codec_type'] == 'audio'), None)
    if v is None:
        sys.exit(f'no video stream in {a.video}')
    n, d = v['r_frame_rate'].split('/')
    fps = a.fps or float(n) / float(d)
    frames = int(v['nb_read_frames'])
    shots, expected = load_shots(a.shots) if a.shots else ([], None)

    if expected is not None:
        gate('frames', frames == expected, dict(frames=frames, expected=expected))
    else:
        res['frames'] = dict(frames=frames)
        print(f'INFO  frames     {frames} (no --shots: not compared)')

    if au is not None:
        gap = abs(float(v['duration']) - float(au['duration']))
        gate('av_match', gap < 1 / fps, dict(gap_s=round(gap, 3), one_frame_s=round(1 / fps, 3)))
    else:
        print('INFO  av_match   no audio stream')

    dec = run(['ffmpeg', '-v', 'error', '-i', a.video, '-f', 'null', '-'])
    gate('decode', dec.returncode == 0 and not dec.stderr.strip(), dict(exit=dec.returncode, errors=dec.stderr.strip()[:300]))

    bd = run(['ffmpeg', '-i', a.video, '-vf', 'blackdetect=d=0.1:pix_th=0.06', '-an', '-f', 'null', '-']).stderr
    segs = [(float(s), float(e)) for s, e in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', bd)]
    bad = [s for s in segs if a.allow_black_after is None or s[0] < a.allow_black_after]
    gate('black', not bad, dict(segments=segs, unplanned=bad))

    if au is not None:
        eb = run(['ffmpeg', '-i', a.video, '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-']).stderr
        summ = eb[eb.rfind('Summary:'):]
        mi, mp = re.search(r'I:\s+(-?[\d.]+) LUFS', summ), re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ)
        if mi and mp:
            lufs, tp = float(mi.group(1)), float(mp.group(1))
            gate('loudness', abs(lufs - LUFS_TARGET) <= LUFS_TOL and tp <= TRUE_PEAK_MAX,
                 dict(integrated_lufs=lufs, true_peak_dbtp=tp, target=f'{LUFS_TARGET} +/- {LUFS_TOL} LUFS, <= {TRUE_PEAK_MAX} dBTP'))
        else:
            gate('loudness', False, dict(error='could not parse ebur128 summary'))

    if shots:
        with tempfile.TemporaryDirectory(prefix='export_check_') as tmp:
            # relative file name + cwd: a path with spaces or colons breaks the filter option
            r = run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.abspath(a.video), '-an', '-vf',
                     f'scale={STATS_SIZE},signalstats,metadata=print:file=stats.txt', '-f', 'null', '-'], cwd=tmp)
            ss = (pathlib.Path(tmp) / 'stats.txt').read_text() if (pathlib.Path(tmp) / 'stats.txt').exists() else ''
        stats = [dict(re.findall(r'lavfi\.signalstats\.(YAVG|UAVG|VAVG)=([-\d.]+)', blk)) for blk in ss.split('frame:')[1:]]
        flick = []
        for k, s in enumerate(shots if a.include_last_shot else shots[:-1]):
            seg = stats[s['f0']:s['f1']]
            if len(seg) < FLICKER_MIN_FRAMES:
                continue
            spike = max(max(abs(float(seg[i][c]) - (float(seg[i - 1][c]) + float(seg[i + 1][c])) / 2) for i in range(1, len(seg) - 1))
                        for c in ('YAVG', 'UAVG', 'VAVG'))
            flick.append((round(spike, 2), k, s.get('clip', '')))
        flick.sort(reverse=True)
        if flick:
            med = sorted(f[0] for f in flick)[len(flick) // 2]
            gate('flicker', flick[0][0] <= FLICKER_MAX, dict(worst=flick[:5], median=med, gate=FLICKER_MAX))
        else:
            print('INFO  flicker    no shot long enough')

    if a.beats:
        if not shots:
            sys.exit('--beats needs --shots')
        grid = load_beats(a.beats)
        off = [(i, s.get('clip', ''), round(s['f0'] / fps, 3)) for i, s in enumerate(shots[1:], 1)
               if min(abs(s['f0'] / fps - b) for b in grid) > 1 / fps]
        gate('cuts', not off, dict(cuts=len(shots) - 1, off_beat=off))

    res['summary'] = dict(failed=fails, shots=len(shots), fps=round(fps, 4), duration_s=round(float(v['duration']), 2))
    if a.json:
        json.dump(res, open(a.json, 'w'), indent=1)
    print('RESULT', 'FAIL: ' + ', '.join(fails) if fails else 'all gates passed')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
