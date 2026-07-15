#!/usr/bin/env python3
"""Generate .otio timeline from edl.json. Usage: gen_otio.py <seq_index>
Times: source_range in media rate (59.94) relative to FILE START (no TC).
Gaps/track layout at timeline rate 24."""
import json, sys, os, subprocess

SP = os.path.dirname(os.path.abspath(__file__))
e = json.load(open(f"{SP}/edl.json"))
seq = e["sequences"][int(sys.argv[1])]
FOOT = e["footage_dir"]
MRATE = 60000 / 1001.0
TRATE = 24.0

def rt(v, r):   return {"OTIO_SCHEMA": "RationalTime.1", "rate": r, "value": v}
def tr(s, d, r): return {"OTIO_SCHEMA": "TimeRange.1", "start_time": rt(s, r), "duration": rt(d, r)}

def tc_frames(clip):
    # Resolve's convention: file start frame index = wall-clock seconds of TC label x 59.94
    out = subprocess.run(["ffprobe","-v","error","-show_entries","stream_tags=timecode","-of","csv=p=0",
                          f"{FOOT}/{clip}"], capture_output=True, text=True).stdout.strip().splitlines()
    tc = next((l for l in out if l), "")
    if not tc: return 0
    hh, mm, ss, ff = [int(x) for x in tc.replace(";", ":").split(":")]
    wall = hh*3600 + mm*60 + ss + ff/60.0
    return round(wall * MRATE)

def dur_s(clip):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",
                          f"{FOOT}/{clip}"], capture_output=True, text=True).stdout.strip()
    return float(out)

def media_ref(clip):
    return {"OTIO_SCHEMA": "ExternalReference.1",
            "target_url": f"{FOOT}/{clip}",
            "available_range": tr(tc_frames(clip), round(dur_s(clip) * MRATE), MRATE)}

def make_clip(clip, src_in, dur_sec, name):
    return {"OTIO_SCHEMA": "Clip.2", "name": name,
            "source_range": tr(tc_frames(clip) + round(src_in * MRATE), round(dur_sec * MRATE), MRATE),
            "media_references": {"DEFAULT_MEDIA": media_ref(clip)},
            "active_media_reference_key": "DEFAULT_MEDIA"}

def gap(dur_sec):
    return {"OTIO_SCHEMA": "Gap.1", "name": "", "source_range": tr(0, round(dur_sec * TRATE), TRATE)}

def track(name, kind, items):
    return {"OTIO_SCHEMA": "Track.1", "name": name, "kind": kind, "children": items}

def seg_items(segs, video=True):
    items, cursor = [], 0.0
    for s in segs:
        tl_in = s["tl_in"]
        d = (s["src_out"] - s["src_in"]) if "src_out" in s else (s["tl_out"] - s["tl_in"])
        if tl_in - cursor > 1e-6: items.append(gap(tl_in - cursor))
        items.append(make_clip(s["clip"], s["src_in"], d, s["clip"].replace(".MP4","")))
        cursor = tl_in + d
    return items

v1 = seg_items(seq["aroll"])
v2 = seg_items(seq["broll"])
a1 = seg_items(seq["aroll"])

otio = {"OTIO_SCHEMA": "Timeline.1", "name": seq["name"],
        "global_start_time": rt(0, TRATE),
        "tracks": {"OTIO_SCHEMA": "Stack.1", "name": "tracks",
                   "children": [t for t in [track("V1", "Video", v1), track("V2", "Video", v2),
                                track("A1", "Audio", a1)] if t["children"]]}}
path = f"{SP}/out/{seq['name']}.otio"
json.dump(otio, open(path, "w"), indent=1)
print("wrote", path)
