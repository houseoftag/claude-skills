---
name: event-promo
description: >
  Use when cutting a music-driven event recap, promo, highlight reel, or montage
  from raw camera and drone footage with ffmpeg and Python, without an NLE
  (non-linear editor). Covers intake, shot selection by measured camera motion,
  gyro-based stabilization (Gyroflow) for rolling-shutter jello and warp, drone
  shot selection for fluid moves, story structure by place and time, beat-grid
  cutting and music swaps, S-Log3 grading, fast ML noise reduction on macOS,
  content screening, and a QC gate before every delivery. Triggers on: event
  recap, promo video, sizzle reel, highlight video, b-roll montage, drone
  footage, cut to the beat, beat sync, warp stabilizer wobble, jello, rolling
  shutter, shaky footage, color flicker, S-Log3, noisy grade, swap the music,
  "the video feels dark", client video notes.
---

# Event recap / promo from raw footage

A music-driven montage (no dialogue) built as data: an EDL (edit decision list)
JSON → per-shot renders with ffmpeg → join, graphics, loudness → export. For
interview a-roll cut by transcript, or a timeline the editor finishes in
DaVinci Resolve, use the `resolve` skill instead.

The process below comes from one real job (a church fall-event recap, 2:33,
96 shots, Sony A7IV + DJI drone, 14 rounds of client notes). Every rule here
cost at least one round of notes. The case log with causes, the dead ends, and
the measured numbers is in `reference/lessons.md`. Read it before you build a
new measure or argue with a note.

## The four costliest mistakes (read first)

1. **Picking shots by content alone.** A logger's "best range" says what is in
   frame, not how the camera moves. Stop-and-go drone moves and fast handheld
   shake each cost two rounds. **Pick by measured motion first, then content.**
2. **Using an image stabilizer on rolling-shutter footage.** A 2D stabilizer
   pins the frame, so the per-row bend (jello) and the motion-blur pulse inside
   the frame stand out more. If the camera recorded gyro data, stabilize with
   Gyroflow from the start.
3. **Building sections by shot type.** "Costumes, then trunks, then waves"
   reads as random to a viewer. **Build by place and time**, then by shot type
   inside each place, and check how much runtime each act gets.
4. **Choosing heavy tools without a budget.** A research denoiser needed 4.5 h
   and a GPU test froze the Mac. Apple's built-in filter did the same job in
   minutes. Probe, compute the full-job time, and cap memory before any heavy
   step.

## 1. Intake: ask before cutting

Ask for these in the first message. Each one, when skipped, came back as a note.

- **Music.** You cannot listen, so the choice is the client's. Ask for the
  track, or a shortlist of 2-3 the client approves, and its licence. If none
  arrives, cut on a beat grid to a placeholder and say so plainly.
- **On-screen words.** Title, date, end card. Lead with the invitation ("See you
  next year!") rather than the thanks when the recap also promotes the next
  event.
- **Story emphasis.** What is the payoff (the exhibits, the speaker, the
  crowd)? The payoff must start before the midpoint and get the largest share.
- **Noise reduction (NR).** Dusk or night footage needs it. Settle the tool,
  and approval to download any model, now and not at the end. Default:
  Apple's VideoToolbox temporal filter (`scripts/vtnr/`).
- **Content limits.** For church, school, or client promos: no political or
  campaign imagery, no public figures, and brands only when allowed.
- **Runtime and delivery spec.** Length, aspect ratio, frame rate, platform
  loudness target (default −14 LUFS integrated, −1 dBTP).

## 2. Inventory and review

- `ffprobe` every source: codec, frame rate, duration, colour tags. Sony XML
  sidecars give `captureFps` (S&Q / high-frame-rate clips). One card often mixes
  23.976p and 59.94p.
- Check colour profile from metadata (`exiftool`): S-Log3 / S-Gamut3.Cine needs
  Sony's `SLog3SGamut3.CineToLC_709` LUT (Resolve ships it in its LUT folder).
- **Check for gyro data now:** `exiftool -ee -G3 clip.MP4 | grep -i gyro`, or
  open one clip in Gyroflow. Sony A7-series, GoPro, DJI action cameras, and many
  phones record it. If present, every handheld shot goes through Gyroflow.
- Make proxies and contact sheets per clip. Loggers (Sonnet workers) write a
  per-clip log: content, tags, best ranges, **and flags for public figures,
  political or campaign imagery, brands, and readable text.**
- Whisper the camera audio only if natural sound might be used.
- Profile motion for every clip you might use: `scripts/motion_profile.py`.
  This is cheap and it drives selection.

## 3. Story before shots

Write the story as a sequence of **places and times** before you pick a shot:
where the viewer is, and what time of day it is. Example that worked:

| Act | Place | Content | Share |
|-----|-------|---------|-------|
| 1 | The line | How long it is (drone + ground), life in the line | ~15 % |
| 2 | The line moving | Costumes in line, the line winding around the building | ~20 % |
| 3 | The payoff zone | Exhibits and costumes intercut, candy, dusk, end card | ~60 % |

- Inside each place, vary shot type (wide, detail, people, aerial).
- Map acts onto music sections (drop, breakdown, second drop) at phrase
  boundaries.
- **Act-timing table** (act, start, end, share) goes in the plan and the
  delivery report. Check it against the brief's emphasis, not only the order.
- An action beat (a high five, a handoff): find the action frame first, then
  fit the window around it. End on the contact, not before.

## 4. Shot selection: motion first, content second

### Drone

Prefer **one constant move per shot**. Cut before any change of direction or
speed: hovers, gimbal tilts, starts, speed-ups, and turns that stop mid-shot all
read as "mechanical".

```bash
python scripts/motion_profile.py drone.MP4 --out-dir profiles/
python scripts/fluid_windows.py profiles/ windows 7.5 drone      # best 7.5 s windows
python scripts/fluid_windows.py profiles/ timeline drone 100 115 # velocity every 0.5 s
python scripts/fluid_windows.py profiles/ check shots.json       # gate the whole cut
```

Gate: **unevenness ≤ 0.15** (largest change in camera velocity inside the
window ÷ mean speed). Client-flagged shots scored 0.88 and 1.32.

Caveats:
- A hover over a moving crowd can score as "moving", because the tracker
  follows the people. Check a frame strip: a hover is not a move.
- Overlays and fades inflate the score on the export. Measure the shot render.

### Handheld camera

The A7IV in 4K 24p reads the full sensor slowly (~26 ms) with a long shutter.
Fast shake leaves rolling-shutter lean and blur **inside** each frame, and no
stabilizer can remove them. Gate on predicted lean (high-pass image velocity ×
readout) on the source window:

```bash
python scripts/motion_profile.py clip.MP4 --out-dir profiles/
python scripts/shake_gate.py profiles/ best clip 2.5 3     # calmest three 2.5 s windows
python scripts/shake_gate.py profiles/ check shots.json    # gate every shot in the cut
```

Gate: **lean rms ≤ 3.0 px and max ≤ 8 px**. The measure moves ±0.7 px between
renders, so leave margin. The default readout table covers only the A7IV
(26 ms at 24p, the value the gate was calibrated on; 15 ms at 60p). For other
cameras pass `--readout-ms`. Any exception is a written content call ("keeps the
only moment of X").

- When a clip has no calm second, replace the shot. Do not keep the moment and
  hope the stabilizer saves it.
- Avoid in points that start or end in a real zoom (probe 0.5 s either side).

### Every window change

Check a 5-frame strip against the shot's note: the subject is readable in every
frame, and anything in the foreground is a fail. Calm windows often lose the
moment (the subject turns away or leaves frame).

### Content screen (separate pass)

View every used shot at **full frame (1920 px)**, not contact-sheet size, for
public figures, political or campaign imagery, brand logos, and readable signs.
Novelty items with a politician's face and a campaign hat passed a thumbnail
review and a logger's description. Political = cut. Pass judgment items
(skulls, culturally sensitive costumes) to the client by name.

## 5. Per-shot render pipeline

Order matters. Cache each shot by a hash of its parameters (content, not shot
index: inserting one shot must not re-render seventy).

1. **Stabilize from gyro** (handheld): `scripts/gyro_render.py` writes a trimmed
   Gyroflow project per clip and renders it. Render only the used window + 1 s,
   with "trim range only" smoothing, so the crop fits the part you use. H.265
   10-bit 4:2:2 output keeps the camera's full-range values (ProRes rescales them
   to video range and is ~6× bigger). Detail: `reference/stabilization.md`.
2. **Exposure offset in log space** with `lutrgb`. On the source job, a chain
   that used `colorlevels` on rgb48 flickered (identical input frames gave
   different output) and `lutrgb` fixed it. An isolated test of `colorlevels`
   later stayed clean, so the trigger may have been the stages around it. Either
   way: test your exact chain with `determinism_check.py`.
3. **LUT** (S-Log3 → Rec.709).
4. **Grade:** tone curve that lifts mids and opens highlights (keep blacks),
   per-shot white balance (remove ~60 % of the midtone cast, cap ±12 %),
   saturation ~1.15. Drone footage gets its own exposure and gamma balance.
5. **Speed changes:** if source fps × speed < timeline fps, use
   `minterpolate` (after the grade) and check that real source frames land
   exactly on output frames.
6. **NR after the grade,** per shot so temporal references never cross a cut:
   `scripts/vtnr/` (VideoToolbox `VTTemporalNoiseFilter`, macOS 26), strength
   0.85. Detail: `reference/grade-and-nr.md`.
7. Encode the shot (x264, high quality) for the join.

If you use an image stabilizer instead (no gyro data): never correct scale (real
zooms become rubber-band jumps), and A/B every stabilizer change on the same
shots with the same residual measure before you adopt it.

**Before the first full render:** run `scripts/determinism_check.py` on the
filter chain. Identical input frames must give identical output frames.

## 6. Music and the beat grid

One beat-grid file feeds everything timed to music: cuts, title keyframes, end
card start, fades, natural-sound inserts.

```bash
python scripts/beat_grid.py track.wav music/beats.json
```

- Fit a **constant-tempo grid** to the tracked beats and extend it to the final
  hit. Tracker output often stops seconds early; an EDL that ends at the last
  tracked beat cuts off the ending.
- Settle the **downbeat phase** from structure: section changes (drops,
  breakdowns) fall on the same beat of the bar, and claps fall on 2 and 4. Do
  not trust one close phase score.
- Build a **section map** from per-beat band energy (intro, build, drop,
  breakdown, second drop, tail) and check for vocals with Whisper.
- Every cut on a grid beat. Long holds on phrase boundaries.

**Music swap = regenerate the grid, then regenerate everything downstream.**
Each item below failed silently on a real swap:
- picture end (re-derive from the final hit + tail),
- graphics (rebuild overlays whenever the cut or grid changes; a build that
  only makes missing PNGs keeps the old end card at the old frame),
- title animation keyed to the new intro hits,
- any music edit (jumps, crossfades) the old track needed,
- natural-sound level (the old track stopped for a moment; the new one only
  gets quieter, so the crowd sound must sit lower),
- render cache (a tempo change alters every shot's length).

## 7. Finish

- Join shots, overlay title and end-card PNGs (rebuilt from the current EDL),
  two-pass `loudnorm` to the target, final encode.
- Graphics legibility: when the shot under a title changes, re-check the title
  frames. A busy, bright aerial needs a soft dark pool behind the text.
- The music must run to the end of the picture: extend by a tail, fade the
  audio over the last ~0.8 s.
- Grade targets for an evening event promo (measured on the export): **mean
  luma 0.40-0.45, p90 ≥ 0.75.** A first pass at mean 0.32 was "dark and noisy".

## 8. QC gate (run before every delivery)

| # | Check | Tool / pass mark |
|---|-------|------------------|
| 1 | Sources: fps and capture fps of every used clip; flag shots that need interpolation | `ffprobe`, Sony XML |
| 2 | Filter determinism: identical input → identical output | `determinism_check.py` |
| 3 | Gyro data present → Gyroflow; levels and frame alignment verified on one clip before the batch | `gyro_render.py` |
| 4 | Handheld windows: lean rms ≤ 3.0, max ≤ 8 px (exceptions written down) | `shake_gate.py check` |
| 5 | Renders: largest one-frame scale and roll change, held frames, blur swing p90 ≤ ~0.35 | `motion_profile.py` on the render, `warp_scan.py` |
| 6 | Drone windows: unevenness ≤ 0.15, source and render | `fluid_windows.py` |
| 7 | Export: frame count, full decode, black frames only where planned, −14 LUFS / −1 dBTP, A/V duration match, flicker (largest in-shot jump in mean Y/U/V ≤ 2.5; clean exports measured median 0.3-0.4, worst 1.0-2.3) | `export_check.py` (exit 1 on any fail) |
| 8 | Every cut within one frame of a grid beat | `export_check.py` |
| 9 | Grade: luma mean 0.40-0.45, p90 ≥ 0.75; old/new sheet on bright, golden-hour, dusk, dark, and drone shots | `signalstats`, sheets |
| 10 | NR checked on 100-200 % crops of flat shadow/midtone areas; frame count, timing, colour verified on one real shot | crops |
| 11 | Story sheet: one frame per shot in order, read as a viewer (does each section stay in one place; does the place advance) + act-timing table vs the brief | `story_sheet.py` |
| 12 | Content screen at full frame | manual, full res |
| 13 | Title and end-card frames over their real backgrounds | frame grabs |
| 14 | Runtime and resources: full-job time computed from a probe; GPU/ML steps tiled and memory-capped; disk use estimated before batch renders | — |
| 15 | Versioning: new file name per delivery; README records what changed and why | — |

## 9. Delivery report

- Link the new export (never overwrite a version the client reviewed).
- What changed, per client note.
- **Every on-screen word**, so the client approves the copy with the cut.
- Act-timing table.
- Exceptions to the gates, with the reason.
- **What was not checked:** listening, real-time playback.
- Shoot advice if the footage caused problems (for example: handheld event
  coverage on an A7IV should be 60p or on a gimbal).

## 10. When a note does not match your measures

- A measure must earn its place as a gate: it has to rank the client-flagged
  shots above the unflagged ones. If it does not, it does not explain the note.
- A correction must beat its control (for example readout 0, or LUT only).
  If it does not, remove it.
- **After two measured hypotheses fail on a perceptual note, ask the client
  what it looks like** (sway, jelly, shimmer, stutter, flicker) before you build
  a third. "Bends like jelly" ended five failed measures.
- Verify a surprising number with a second, independent method before you act
  on it (ffmpeg seeks and frame selection lie; see `reference/ffmpeg-gotchas.md`).

## 11. Resource safety (Apple Silicon)

GPU and system share memory. A full-frame ML test with no tiling froze the Mac.

- Any GPU/ML step: tiles ≤ 512 px, `PYTORCH_MPS_HIGH_WATERMARK_RATIO` (with a
  matching low mark) so an oversized run errors out instead of freezing, and a
  probe of a few frames that reports peak memory first.
- One heavy process at a time. Long runs are detached (`nohup`) and cached per
  shot, so a restart costs one shot.
- Brief workers with explicit limits and "stop after a failure; do not retry
  the same heavy test". After a crash, check what restarted before resuming.
- Estimate disk use per codec and frame rate before a batch render (ProRes HQ
  60p ≈ 80 MB/s) and check free space during it.

## Delegation

- Loggers, motion profiling, gate runs, and export checks: Sonnet workers.
  Give them the resource limits above in the brief.
- Story, shot choice, grade look, graphics, and reading the story sheet:
  the coordinator. Graphics code (titles, end cards) is visual work: Opus.
- Keep a `PROCESS_LOG.md` in the project: for every client note, record what
  they saw, the root cause, the QC that would have caught it, the fix, and the
  rule. Fold new rules back into this skill.

## Files

- `scripts/` — standalone tools; each has `--help` and a docstring with its
  gate value and the JSON shapes it reads. Python deps: numpy, opencv-python,
  librosa, Pillow; plus ffmpeg, ffprobe, exiftool, and Gyroflow. Make a venv
  in the project and run them from there.

  | Script | Does |
  |--------|------|
  | `motion_profile.py` | per-frame camera motion of a clip or range → JSON (feeds the next two) |
  | `fluid_windows.py` | drone unevenness per window; best fluid windows; `check` a cut |
  | `shake_gate.py` | predicted rolling-shutter lean; calmest windows; `check` a cut |
  | `warp_scan.py` | warp and blur swing on a rendered shot |
  | `gyro_render.py` | trimmed Gyroflow project + render (H.265 10-bit, trim-only smoothing) |
  | `vtnr/main.swift` | VideoToolbox temporal NR pipe (build line in its header) |
  | `beat_grid.py` | constant-tempo beat grid to the final hit, downbeat phase, band energy |
  | `determinism_check.py` | same frames twice + one frame repeated → max pixel difference |
  | `export_check.py` | frames, decode, black, loudness, A/V gap, flicker, cuts on beats |
  | `story_sheet.py` | one labelled frame per shot, in order, as JPEG sheets |
- `reference/lessons.md` — the case log: every client note, cause, QC, fix.
- `reference/stabilization.md` — Gyroflow setup and gotchas, measures that
  failed, rolling-shutter background.
- `reference/grade-and-nr.md` — S-Log3 handling, grade targets, noise
  reduction options and how to measure noise.
- `reference/ffmpeg-gotchas.md` — seeks, frame selection, range flags, and
  other traps found on this job.
