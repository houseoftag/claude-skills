# ffmpeg and pipeline traps

Each of these produced a wrong number or a wrong frame on a real job.

## Frames and seeking

- **Seeking to a frame's exact time can return the next frame.** `-ss f+0.5`
  (in frame units) returned frame f+1. For a single grab, seek to `f - 0.3`
  frames, or better, select by index:
  `-vf "select=eq(n\,123)" -fps_mode passthrough -frames:v 1`.
- **Frame selection fills gaps with repeats** unless you pass
  `-fps_mode passthrough` (old name `-vsync 0`). A frame-match check reported
  every frame as equal because of this.
- **`-ss` lands on different frames in two differently encoded files.** Compare
  per-shot renders by frame index, not two exports by seek time.
- **A seek can duplicate a frame** and fake a "held frame". Check the shot
  render directly before you act on a surprising count.

## Frame rates

- One camera card can mix 23.976p and 59.94p. Probe every clip; read Sony XML
  `captureFps` for slow-motion clips.
- 24p at 1× on a 29.97 timeline repeats every 5th frame. That is normal. A
  59.94 export would show standard 3:2 cadence instead.
- Slow motion where source fps × speed < timeline fps holds frames.
  `minterpolate` (after the grade) fixes it; check real source frames land on
  output frames 0, 5, 10 …
- Drone speed-ups: pick factors that map exactly onto the timeline rate (for
  example 2.5× and 1.25× from 23.976 to 29.97) so motion does not judder.

## Colour and range

- A `colorlevels`-on-rgb48 chain (ffmpeg 8.1) flickered on the source job;
  `lutrgb` fixed it. A later isolated test of `colorlevels` stayed clean, so the
  cause may sit in the stages around it. Test the exact chain with
  `determinism_check.py` before a full render.
- Full vs video range: know which one the decoder assumed. Gyroflow ProRes
  rescaled to video range; H.265 kept full range. Compare raw code values.
- Hardware and software HEVC decoders both decoded the Sony files cleanly; when
  flicker appears, test the filter chain first (`determinism_check.py`).

## Builds and caches

- Key render caches by a hash of the shot's content and parameters, not by shot
  index.
- Regenerate graphics from the current EDL on every build. "Only if missing"
  leaves old overlays at old frames after a re-cut or music swap.
- Never overwrite a reviewed export. New version name per delivery.
- Two-pass `loudnorm` for the final mix (measure, then apply with the measured
  values).

## Measurement hygiene

- Overlays, fades, and end-card darkening inflate motion scores on the export.
  Measure the shot render without overlays.
- Re-measure lean on renders; it moves ±0.7 px between renders of the same shot.
- Run a known-good control through any new check before you believe it.
