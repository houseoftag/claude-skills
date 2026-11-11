# Case log: a church fall-event recap (2026-10)

Source job: 2:33 recap, 96 shots, Sony A7IV (S-Log3, HEVC 10-bit 4:2:2, mixed
23.976p and 59.94p) + DJI drone (23.976p 4K), 1080p 29.97 export, no NLE.
Fourteen rounds of reviewer notes. Each entry: what the reviewer saw, the cause,
the QC that would have caught it, the fix, and the rule. Numbers are from that
job; treat them as starting values for other cameras.

## Reviewer notes

### 1. "Needs better music"
- Cause: the assistant cannot listen; it chose a free track by measurable
  proxies (tempo, no vocals, energy, licence).
- QC: none possible. Music is a taste call.
- Fix: cut on a beat grid so any track can be swapped.
- Rule: ask for the music (or an approved shortlist) before cutting.

### 2. "A weird color flicker"
- Cause: ffmpeg 8.1 `colorlevels` on rgb48 returned different values for
  identical input frames. Used for the per-shot exposure offset, it made 56 of
  82 shots jump in colour frame to frame (up to 18 units of mean chroma) and
  darker than planned.
- QC: a determinism test for every filter chain; a per-frame colour check on
  the export (largest one-frame jump in mean Y/U/V inside each shot: broken
  median 3.2 / worst 18.5, clean median 0.4 / worst 2.3); bisect the chain
  against a LUT-only control when a per-frame statistic looks noisy.
- Fix: `lutrgb` for the offset. (A later isolated test of `colorlevels` on
  ffmpeg 8.1.2 could not reproduce the fault, so it may have come from the
  stages around it. The lesson stands: test the exact chain.)
- Rule: never trust a filter's temporal behaviour; test it once.

### 3. "Warp stabilizer wonkiness" (three causes)
- (a) The stabilizer corrected scale; real zooms and people walking toward the
  lens became size jumps of 4-11 % per frame. QC: re-track the render; largest
  one-frame size change > ~2 % is visible. Fix: never correct scale.
- (b) 24p clips at half speed held each frame for 2-3 timeline frames (~12 fps)
  and the stabilizer slid the held frames. QC: probe fps and capture fps first;
  flag any shot where source fps × speed < timeline fps; count held frames.
  Fix: `minterpolate` after the grade; check real source frames land on output
  frames 0, 5, 10 …
- (c) In points inside a real zoom. QC: motion probe of the window ± 0.5 s.
- Self-caught: outlier rejection on tracking steps removed real jolts and made
  shake worse (1.4 → 15 px on one shot). A/B every stabilizer change.

### 4. "Drone clips cannot have mechanical movement … fluid continuous movement"
- Cause: drone windows chosen from a content log, not from camera motion.
- QC: motion profile of every drone clip and an unevenness score per window
  (largest change in camera velocity ÷ mean speed). Flagged: 1.32 and 0.88.
  Good: ≤ 0.15. Then a frame strip for content.
- Fix: all ten drone shots re-picked to ≤ 0.13.
- Caveats: a hover over a walking crowd scores as moving (the tracker follows
  people); overlays and fades inflate the score on the export.
- Rule: drone selection = motion first, content second.

### 5. "Too much shake/warp at 0:42" and "a ton of warp artifacting from 1:08"
- Cause: fast shake inside the chosen windows. 4K 24p on the A7IV reads the full
  sensor slowly (~26 ms) with a long shutter: fast shake leaves rolling-shutter
  lean and blur in each frame; stabilization pins the frame and makes both
  stand out. Whip pans of 100+ px per frame.
- Why missed: windows came from content ranges and a coarse half-second scan.
  The residual-shake metric measured the frame, not what is inside it.
- Dead ends: affine shear between frames (close-up motion inflates it); a
  rolling-shutter correction calibrated 0-40 ms (small, inconsistent gains
  against readout 0, removed); averaging 0.5 s of frames (shows intentional
  moves).
- Adopted: predicted lean = high-pass image velocity × readout. The reviewer's
  flagged shots were the top 9 of 76.
- Fix: 23 shots changed (19 calm windows in the same clip, the rest replaced).
  Render lean worst 9.7 → 3.7 px; blur swing worst 1.05 → 0.33.
- Rules: choose camera windows by measured shake first; treat 24p full-frame
  handheld as high risk; a measure must rank the flagged shots on top before it
  becomes a gate; a correction must beat its control; leave ±0.7 px margin.

### 6. "Still too much wobble" at six timestamps
- Five image measures (lean, background-only motion, foreground vs background
  parallax, slow sway and size breathing, drone size flutter) did not separate
  the flagged shots from controls. Two more (band-by-band bend, dense optical
  flow after a homography) also failed.
- Turning point: asked the reviewer what it looked like. Answer: "picture bends
  like jelly".
- Root cause: rolling-shutter bend under handheld motion (28 mm, IBIS on). A 2D
  stabilizer cannot undo it; each sensor row needs its own correction.
- Fix: the A7IV records ~2 kHz gyro data, readout time, IBIS data and the lens
  profile in every clip. Gyroflow uses them for per-row correction. On one
  flagged shot: band-bend jello −69 %, frame wobble −49 %.
- Rules: check for gyro data at intake and stabilize from gyro by default;
  after two failed hypotheses on a perceptual note, ask what it looks like.

### 7. "A clearer flow of story … no linear flow of time"
- Cause: sections built by shot type. The logger tags had the place
  information; the structure did not use it.
- QC: write the story as places and times; read a story sheet (one frame per
  shot, in order) as a viewer.
- Fix: three acts by place (the line, the line moving, the payoff zone).
- Rule: geography + time first, shot type within each place.

### 8. "The grade feels dark and noisy across the board"
- Measured: mean luma 0.32, p90 0.64, shadows 0.06. Contrast pivoted at mid-grey
  pushed shadows down; the exposure target (0.33) was too low; drone shots had
  no exposure balance.
- Fix: target 0.42 (up to +1.8 stops in log space), a tone curve that lifts mids
  and opens highlights, per-shot white balance, saturation 1.28 → 1.15, drone
  gamma per shot. Export mean 0.45, p90 0.79.
- Noise: brighter shadows show more noise. The reviewer wanted ML noise
  reduction (classic spatial/temporal NR looked muddy). Downloading a model
  needed explicit approval.
- Rule: settle NR and its approval at the start of a dusk/night job.

### 9. "Hard restart of the Mac, it froze completely"
- Cause: a worker's denoiser speed test pushed whole 1080p frames through two
  research models on the Apple GPU with no tiling and no memory cap. After the
  reboot the worker resumed the same test.
- Fix: always tile (≤ 512 px); cap MPS memory so an oversized run errors out;
  detached, cached runs; workers told to stop after a failure.

### 10. "This needs to go faster … no reason for it to take this long"
- Cause: a research model at 3.7 s per 1080p frame (~4.5 h for the edit) was
  picked for quality without a runtime budget.
- Fix: Apple's VideoToolbox temporal noise filter in a small Swift pipe tool.
  Whole build including NR: ~3 minutes (~150× faster), same look on 200 % crops,
  shadow/midtone luma noise −24 %, chroma −16 %.
- Rule: compute full-job runtime from a probe before choosing a heavy step;
  check the platform's own accelerated tools first.

### 11. "Use this song … make sure the cut lines up on the new music and the graphics look good"
- What a music swap touched (each fails silently): the beat grid (tracker's
  last beat 147.68 s, real final hit 150.29 s → fit constant tempo, 115.000 BPM,
  residual rms 4 ms, extend to the final hit); downbeat phase (two phase scores
  6.198 vs 6.202 → settled by section changes and claps on 2 and 4); section
  map; graphics (rebuilt only when PNGs were missing → old end card at the old
  frame); title keyframes; the old track's music edit; natural-sound level;
  render cache (every shot ~4 % longer).
- Rule: one beat-grid file; a swap regenerates everything downstream.

### 12. "Take out the [politician] ducks at about 1:37"
- Cause: a row of novelty rubber ducks included two showing a politician with
  campaign hats. The logger wrote "costumed rubber ducks (pirate, soldier,
  police, etc.)". Contact-sheet size made the faces unreadable. A second clip
  showed the same car.
- Fix: both clips out; 20 new shots screened at full frame; two judgment items
  (a skull decoration, a culturally styled costume) passed to the reviewer.
- Rule: loggers flag public figures, political imagery, brands, readable text;
  screen at full resolution; political = cut for a church or client promo.

### 13. "Still showing the line at 1:04; by then it should be all exhibits"
- Cause: the order was right but the proportions were wrong. The line acts ran
  to 1:05 (~45 %); the payoff started too late.
- Fix: line ends at 0:50 on a phrase boundary; the payoff zone gets ~60 %.
  About 15 new payoff shots, each gated for shake and content.
- Rule: an act-timing table in the story sheet, checked against the emphasis.

### 14. "Change the ending title to 'See you next year!'"
- A copy preference. The end card led with the thanks.
- Rule: list every on-screen word in the delivery report.

## Self-caught issues

- Silent end card: music ended 3.5 s before the picture. Extend by a tail; fade
  the last 0.8 s.
- A review sheet showed the wrong frame (seek to f + 0.5 returned the next
  frame). Seek to f − 0.3, or select by frame index.
- Blur or shake on a shot's first frame. Use a first/middle/last frame sheet.
- Title unreadable on a new, busy aerial. Add a soft dark pool behind the text;
  re-check graphics whenever the shot under them changes.
- A build overwrote the export the reviewer had seen. New name per delivery.
- A false "repeated frame" from an ffmpeg seek. Verify surprising numbers with a
  second method.
- Calm windows lost the moment (subject out of frame, turned away, too small).
  5-frame strip check against the shot's note for every window change.
- A high-five window ended before the hands met. Find the action frame first.
- Inserting one shot re-rendered 70 (cache keyed by index). Key by content hash.
- A frame-match check reported all frames equal because ffmpeg filled gaps with
  repeats. Use `-fps_mode passthrough`.
- Two exports looked out of step on a dancing shot: `-ss` lands on different
  frames in differently encoded files. Compare shot renders by frame index.
- Two new shots passed 3-frame strips but were weak on the export (only a hand
  visible; a blurry head in the foreground). The subject must be readable in
  every frame; anything in the foreground fails.
- A Gyroflow ProRes 60p batch nearly filled the disk (5.7 GB with 13 GB free).
  Estimate size per codec and frame rate; watch `du` during the run.
