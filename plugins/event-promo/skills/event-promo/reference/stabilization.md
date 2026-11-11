# Stabilization

## Decide the method at intake

| Footage | Method |
|---------|--------|
| Camera recorded gyro data (Sony A7-series, GoPro, DJI action cams, many phones) | **Gyroflow**, per-row rolling-shutter + lens correction |
| Drone (gimbal) | Usually none. Select fluid windows instead (`fluid_windows.py`) |
| No gyro data, handheld | Image stabilizer, translation + roll only, never scale |
| Fast shake baked into the frame (lean, blur) | No method fixes it. Pick another window |

Check: `exiftool -ee -G3 clip.MP4 | grep -i -m5 gyro`, or load one clip in
Gyroflow and look for the gyro graph. Gyroflow:
`brew install --cask gyroflow`; the CLI is
`/Applications/Gyroflow.app/Contents/MacOS/gyroflow`.

## Why a 2D stabilizer fails on rolling shutter

A rolling-shutter sensor exposes rows one after another (A7IV 4K 24p: 26.8 ms
top to bottom). Under handheld motion, each row sees the scene from a slightly
different position, so verticals lean and the picture bends ("jelly"). A 2D
stabilizer moves the whole frame as one rigid piece. It pins the average
position, so the leftover bend inside the frame stands out more than before.
Only a per-row correction from real motion data (gyro) can undo it.

Motion blur is the same story: a long shutter bakes the shake into each frame.
When the frame is pinned, the blur pulses. Gate on the source window instead.

## Gyroflow gotchas (verified)

- **Range:** ProRes output rescaled full-range camera values to video range.
  H.265 output kept the original values. Compare raw code values of the same
  frame before you trust either.
- **Size:** ProRes HQ at 60p ≈ 80 MB/s and nearly filled the disk mid-batch.
  H.265 10-bit 4:2:2 at 150 Mbps is ~6× smaller.
- **Frame alignment:** trimmed renders start exactly on the trim's first source
  frame (verified by matching pixels against candidate source frames).
- **Trim + smoothing:** render only the used window + 1 s, with "trim range only"
  smoothing, so the auto-crop fits the part you use and not the shakiest moment
  of the whole clip.
- **Reuse:** when a window moves, reuse an existing render if its trim range
  already covers the new window.
- Turn the pipeline's own stabilizer off for gyro-rendered shots.

## Measures: what worked and what did not

Adopted:
- **Predicted lean** (`shake_gate.py`): high-pass image velocity × readout.
  Ranked the reviewer's flagged shots as the top 9 of 76. Gate rms ≤ 3.0 px,
  max ≤ 8 px on the source window. Readout values: A7IV ~26 ms at 24p (Gyroflow
  measures 26.8 ms; the gate was calibrated at 26), ~15 ms
  at 60p; look up or measure other cameras.
- **Blur swing** (`warp_scan.py`): p90 ≤ ~0.35 on the render.
- **Band-bend jello**: confirmed the Gyroflow improvement (median 0.51 → 0.28),
  but did not rank the flagged shots on its own.
- **Largest one-frame scale and roll change** on the render (re-track the
  output): > ~2 % scale per frame is visible.

Failed to explain a "wobble" note (do not rebuild them first next time):
affine shear between frames; background-only motion; foreground vs background
parallax; slow sway and size breathing after removing the straight-line move;
drone size flutter; band-by-band bend; dense optical-flow bend after a
homography; a rolling-shutter correction calibrated 0-40 ms (did not beat
readout 0). The answer came from asking the reviewer what it looked like.

## Image stabilizer rules (fallback)

- Correct translation and roll only. Scale correction turns real zooms and
  people walking toward the lens into rubber-band jumps.
- Do not reject "outlier" tracking steps: they are often real jolts, and removing
  them made shake worse.
- Cap the crop (≤ 20 %) and work from an oversized frame (for example 2304 px
  wide from 4K) so the crop never upscales.
- A/B every change on the same shots with the same residual measure.

## Shoot advice

Handheld event coverage on the A7IV should be 60p (faster readout, shorter
shutter) or on a gimbal. At 24p it caused most of the shake and warp notes.
