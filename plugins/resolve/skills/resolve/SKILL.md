---
name: resolve
description: >
  Use when assembling video edits for DaVinci Resolve: building timelines
  programmatically (OTIO import), cutting a-roll from raw interview footage by
  transcript, generating preview renders with ffmpeg, or troubleshooting
  Resolve timeline-import errors. Triggers on: DaVinci Resolve, OTIO, FCPXML
  import, timeline import, media offline, timecode mismatch, "file not found
  in search directories", cutdown, rough cut, assembly edit, a-roll sequencing,
  whisper-based editing, EDL, 30-second cut, social cutdown.
---

# Programmatic edit assembly for DaVinci Resolve

Build rough assemblies as data (an EDL JSON), deliver two artifacts per sequence:
a **preview MP4** (rendered with ffmpeg — the source of truth for what the edit
sounds/looks like) and an **OTIO timeline** the editor opens in Resolve to refine.

Proven pipeline scripts live in `scripts/`: `gen_otio.py` (EDL → .otio) and
`build_seq.py` (EDL → preview render). Copy them into the project, point them at
an `edl.json`, done. EDL format:

```json
{
  "footage_dir": "/abs/path/to/Footage",
  "timeline": {"width": 1920, "height": 1080, "fps": 24, "duration": 30.0},
  "sequences": [{
    "name": "SEQ_NAME_v1",
    "aroll": [{"clip": "C3723.MP4", "src_in": 10.05, "src_out": 20.76, "tl_in": 0.0}],
    "broll": [{"clip": "C3731.MP4", "src_in": 20.0, "tl_in": 3.5, "tl_out": 6.0}]
  }]
}
```

All times are plain seconds from file start. A-roll goes to V1+A1; b-roll becomes
video-only connected clips on V2. **Default to `"broll": []`** — assemble a-roll
only and let the editor place b-roll unless they explicitly ask otherwise.

## Timeline format: OTIO, never hand-rolled FCPXML

Resolve imports `.otio` via File → Import Timeline. Requirements learned the hard
way (each was a real failure):

1. **`target_url` must be a plain filesystem path** (`/Users/x/My Folder/C1.MP4`).
   URL-encoding (`%20`) or `file://` prefixes break Resolve's file discovery →
   "File not found in search directories".
2. **Camera media with embedded timecode must declare it.** Resolve links clips by
   filename + timecode-range overlap. If `available_range` starts at 0 but the file
   carries embedded TC, video refuses to link (audio links anyway — audio has no TC
   check). Read TC with `ffprobe -show_entries stream_tags=timecode` (it lives on
   the tmcd data track).
3. **Resolve's TC→frame conversion is wall-clock, not NDF label counting.** For a
   59.94 file with TC `11:40:52:52`: `frames = (hh*3600+mm*60+ss + ff/60) × 60000/1001`.
   Counting NDF label frames (`(hh*3600+mm*60+ss)*60 + ff`) lands ~0.1% off — a
   42-second in-point error at an 11-hour TC base. `gen_otio.py` implements the
   correct convention.
4. Express `source_range`/`available_range` in the **media's native frame rate**
   (e.g. 59.94 for 60p camera files) even when the timeline is 24fps. In-points are
   `available_start + src_in×rate`, so content position survives a ±1 frame TC
   disagreement.

Do NOT hand-generate FCPXML for Resolve: three separate failure layers (connected
clips use parent-local offsets; TC-overlap link rejection; the NDF conversion
mismatch above shifting every in-point). OTIO has none of these.

## Cutting a-roll by transcript

Raw interview clips contain takes, flubs, and director chatter. Workflow:

1. Extract 16k mono WAVs (`ffmpeg -ar 16000 -ac 1`), transcribe with
   `whisper-cli -m ggml-small.bin -l auto -osrt` (binary is `whisper-cli`, not
   `whisper-cpp`; model from HF `ggerganov/whisper.cpp`). Transcribe the reference
   cut too if one exists, then align its lines to raw takes (delegable analysis).
2. **Never cut on full-file SRT cue times** — they drift up to ~1s on takes that
   follow long pauses. For every cut boundary, re-probe a narrow window with
   word-level timestamps: `whisper-cli -ml 1` on a 4–6s extract. Start the window
   mid-speech before the boundary — a window starting in silence snap-aligns the
   first word to t=0 and lies about onset.
3. Cross-check with energy: `silencedetect` needs `highpass=f=120` and roughly
   `n=-18dB` on room-toned interview audio; `-25dB` and below often detects
   nothing. Word gaps ≥0.2s are safe cut points; pad ~0.1s before onsets,
   ~0.2–0.3s after ends.
4. Speakers sometimes restart with **zero gap** after a false start — expect to cut
   into continuous audio; note it for the editor.
5. Maximize the deliverable: a 30s cut should carry a-roll to ~29–30s. Prefer
   dropping a redundant middle sentence over leaving >2s of dead tail. Whole
   sentences only — clauses fused by <100ms gaps don't split cleanly.

## Verify before shipping (every time)

- **Transcribe the rendered preview** with whisper and read the result: clipped
  first/last words, director bleed-through, and bad joins all show up as text.
  This end-to-end check catches everything the EDL math can't.
- Frame-sample the preview at shot boundaries (one tiled contact sheet, not
  per-frame reads) to confirm placement.
- `ffprobe` the deliverable: exact duration, resolution, fps, audio present.
- Editor-side checkpoint after import: tell them what the first V1 clip should
  say; wrong content means a time-interpretation bug, not a linking bug.

## Alpha overlays and logo animations

For overlay deliverables (logo reveals etc.): render frames headless with
transparent background, assemble with
`ffmpeg -framerate 60 -i f%04d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le out.mov`
— ProRes 4444 with alpha drops straight onto a Resolve timeline. Always ship an
H.264 preview alongside (composite over white) since ProRes alpha won't QuickLook.

## Resolve import-log decoder

| Log message | Meaning | Fix |
|---|---|---|
| "File not found in search directories" | Path discovery failed | Plain paths in target_url; or Timeline → Reconform from Bins (filename match) |
| "Mismatch/No overlap between specified target timecodes and located file timecodes" | Declared range doesn't overlap file's embedded TC | Declare TC per rules 2–3 above |
| "Trimming item on V1 because it overlaps" (FCPXML) | Connected-clip offsets computed parent-relative | Regenerate as OTIO |
| Links but wrong content at in-points | TC base conversion mismatch | Use wall-clock TC→frame formula (rule 3) |

Reconform from Bins (filename-only matching) is the editor-side rescue when
linking fails but timeline structure is right — safe with OTIO because its
in-points are file-relative; risky with TC-shifted FCPXML.
