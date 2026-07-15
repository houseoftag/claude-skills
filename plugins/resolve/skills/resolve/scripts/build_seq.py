#!/usr/bin/env python3
"""Build FCPXML + preview mp4 for one sequence in edl.json. Usage: build_seq.py <seq_index>"""
import json, math, subprocess, sys, os
from fractions import Fraction

SP = os.path.dirname(os.path.abspath(__file__))
e = json.load(open(f"{SP}/edl.json"))
seq = e["sequences"][int(sys.argv[1])]
FD = Fraction(1001, 60000)          # source frame duration (59.94)
FPS = 24
FOOT = e["footage_dir"]

def src_t(t):   # snap to source frame grid -> Fraction seconds
    return Fraction(round(Fraction(t) / FD)) * FD
def tl_t(t):    # snap to 24fps grid
    return Fraction(round(t * FPS), FPS)
def rs(f):      # rational seconds string
    f = Fraction(f)
    return f"{f.numerator}/{f.denominator}s" if f.denominator != 1 else f"{f.numerator}s"

def tc_base(clip):
    import subprocess as sp
    out = sp.run(["ffprobe","-v","error","-show_entries","stream_tags=timecode","-of","csv=p=0",
                  f"{FOOT}/{clip}"], capture_output=True, text=True).stdout.strip().splitlines()
    tc = next((l for l in out if l), "")
    if not tc: return Fraction(0)
    tc = tc.replace(";", ":")
    hh, mm, ss, ff = [int(x) for x in tc.split(":")]
    frames = (hh*3600 + mm*60 + ss) * 60 + ff   # 59.94 NDF counts 60 nominal fps
    return Fraction(frames) * FD

def dur(clip):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0", f"{FOOT}/{clip}"], capture_output=True, text=True).stdout.strip()
    return src_t(float(out))

clips = []
for s in seq["aroll"] + seq["broll"]:
    if s["clip"] not in clips: clips.append(s["clip"])

# --- FCPXML ---
R = []
R.append('<?xml version="1.0" encoding="UTF-8"?>')
R.append('<fcpxml version="1.9">')
R.append('  <resources>')
R.append('    <format id="r1" name="FFVideoFormat1080p24" frameDuration="1/24s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>')
R.append('    <format id="r2" name="FFVideoFormat1080p5994" frameDuration="1001/60000s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>')
rid = {}
TCB = {c: tc_base(c) for c in clips}
for i, c in enumerate(clips):
    rid[c] = f"r{i+3}"
    R.append(f'    <asset id="{rid[c]}" name="{c}" start="{rs(TCB[c])}" duration="{rs(dur(c))}" hasVideo="1" format="r2" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000">')
    R.append(f'      <media-rep kind="original-media" src="file://{FOOT.replace(" ", "%20")}/{c}"/>')
    R.append('    </asset>')
R.append('  </resources>')
R.append('  <library>')
R.append('    <event name="EDL Deliverables">')
R.append(f'      <project name="{seq["name"]}">')
R.append('        <sequence format="r1" duration="30s" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">')
R.append('          <spine>')

ar = seq["aroll"]
# assign each b-roll to the a-roll segment whose tl span contains its tl_in
spans = []
for i, a in enumerate(ar):
    tin = tl_t(a["tl_in"])
    tdur = tl_t(a["src_out"] - a["src_in"])
    spans.append((tin, tin + tdur))
for i, a in enumerate(ar):
    p_tl, p_end = spans[i]
    p_start = src_t(a["src_in"]) + TCB[a["clip"]]
    children = [b for b in seq["broll"] if p_tl <= tl_t(b["tl_in"]) < p_end or (i == len(ar)-1 and tl_t(b["tl_in"]) >= p_end)]
    open_tag = f'            <asset-clip ref="{rid[a["clip"]]}" name="{a["clip"]}" offset="{rs(p_tl)}" start="{rs(p_start)}" duration="{rs(p_end - p_tl)}" audioRole="dialogue"'
    if not children:
        R.append(open_tag + '/>')
        continue
    R.append(open_tag + '>')
    for b in children:
        off = p_start + (tl_t(b["tl_in"]) - p_tl)   # offset in parent-local time
        d = tl_t(b["tl_out"]) - tl_t(b["tl_in"])
        R.append(f'              <video ref="{rid[b["clip"]]}" name="{b["clip"]}" lane="1" offset="{rs(off)}" start="{rs(src_t(b["src_in"]) + TCB[b["clip"]])}" duration="{rs(d)}"/>')
    R.append('            </asset-clip>')
R.append('          </spine>\n        </sequence>\n      </project>\n    </event>\n  </library>\n</fcpxml>')
xml_path = f"{SP}/out/{seq['name']}.fcpxml"
open(xml_path, "w").write("\n".join(R))
import xml.etree.ElementTree as ET; ET.parse(xml_path)
print("fcpxml ok:", xml_path)

if len(sys.argv) > 2 and sys.argv[2] == "noprev":
    sys.exit(0)
# --- preview render ---
inputs, fc = [], []
for i, a in enumerate(ar):
    inputs += ["-ss", str(a["src_in"]), "-to", str(a["src_out"]), "-i", f"{FOOT}/{a['clip']}"]
    fc.append(f"[{i}:v]fps={FPS},setpts=PTS-STARTPTS[v{i}];[{i}:a]asetpts=PTS-STARTPTS[a{i}]")
n = len(ar)
fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[bv][ba]")
last = float(spans[-1][1])
fc.append(f"[bv]tpad=stop_mode=clone:stop_duration={30.0-last:.3f}[bvp];[ba]apad=whole_dur=30[bap]")
cur = "bvp"
for j, b in enumerate(seq["broll"]):
    k = n + j
    bd = b["tl_out"] - b["tl_in"]
    inputs += ["-ss", str(b["src_in"]), "-to", str(b["src_in"] + bd + 0.2), "-i", f"{FOOT}/{b['clip']}"]
    fc.append(f"[{k}:v]fps={FPS},trim=duration={bd:.3f},setpts=PTS-STARTPTS+{b['tl_in']:.3f}/TB[o{j}]")
    fc.append(f"[{cur}][o{j}]overlay=eof_action=pass[c{j}]"); cur = f"c{j}"
fc.append(f"[{cur}]trim=duration=30,setpts=PTS-STARTPTS[vout];[bap]atrim=duration=30[aout]")
mp4 = f"{SP}/out/{seq['name']}_preview.mp4"
cmd = ["ffmpeg","-y","-loglevel","error"] + inputs + ["-filter_complex", ";".join(fc),
       "-map","[vout]","-map","[aout]","-r","24","-c:v","libx264","-crf","20","-c:a","aac","-b:a","192k", mp4]
subprocess.run(cmd, check=True)
p = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height,r_frame_rate,codec_type","-of","compact", mp4], capture_output=True, text=True).stdout
print("preview:", p)
