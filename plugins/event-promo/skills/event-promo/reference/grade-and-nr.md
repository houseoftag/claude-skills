# Grade and noise reduction

## S-Log3 input

- Confirm the profile from metadata (`exiftool`), not by eye. Sony S-Log3 /
  S-Gamut3.Cine → Sony's `SLog3SGamut3.CineToLC_709.cube`. DaVinci Resolve ships
  Sony's LUTs in its LUT folder; copy the file into the project.
- Sony files are flagged full range. Decoding them as video range adds about
  17 % contrast around mid-grey. That can be useful, but write it down: anyone
  who re-grades must know which range the pipeline assumed.
- Do exposure in log space, before the LUT, with `lutrgb`. A chain that used
  `colorlevels` on rgb48 flickered on the source job (see
  `ffmpeg-gotchas.md`); test any chain with `determinism_check.py`.

## Look and targets (evening event promo)

- Exposure target: mean luma ~0.42 per shot, up to +1.8 stops of lift.
- Tone curve: lift mids, open highlights, keep blacks. Contrast pivoted at
  mid-grey pushes shadows down and reads as "dark".
- White balance per shot: remove ~60 % of the midtone cast, cap ±12 %.
- Saturation ~1.15 (down from 1.28 in the darker first grade).
- Drone: its own exposure balance and per-shot gamma (late-dusk flights came in
  at 0.25).
- Export targets: **mean luma 0.40-0.45, p90 ≥ 0.75.** Check on an old/new
  sheet of representative shots: bright, golden hour, dusk, dark subjects, drone.

## Noise reduction

Brighter shadows show more noise, so a brighter grade needs NR. Classic
spatial/temporal NR (`hqdn3d`, `nlmeans`, `bm3d`) looked muddy to the reviewer.

### Default: Apple VideoToolbox temporal filter (macOS 26+)

`scripts/vtnr/main.swift` wraps `VTTemporalNoiseFilter` (1 previous + 2 next
reference frames) as a pipe: ffmpeg NV12 in, NV12 out, one shot per call so
references never cross a cut. Build:

```bash
xcrun swiftc -O scripts/vtnr/main.swift -o vt_denoise
```

- Strength 0.85 (1.0 removed no more noise, measured).
- The filter only accepts Apple's compressed pixel formats; frames go in and out
  through a `VTPixelTransferSession`.
- **Tag every buffer Rec.709.** Untagged buffers made VideoToolbox convert
  colour (0.8-1.5 levels darker). Tagged, pass-through is exact (+0.04).
- Speed: the whole 2:33 build including NR took ~3 minutes.
- Results on that job: luma noise −24 %, chroma −16 % in shadow/midtone blocks;
  file size 446 → 300 MB; frame alignment exact; no ghosting at 100 % on fast
  motion.

### Fallback: heavy per-frame models

Only when the platform filter falls short and the runtime fits the budget.
SCUNet real-noise models (Apache-2.0): the GAN variant kept edges and hair; the
PSNR variant softened lettering. 3.7 s per 1080p frame on the Apple GPU (~4.5 h
for the edit). Restormer: non-commercial licence and memory-heavy, so not used.
Any such run: tiles ≤ 512 px, MPS memory cap, probe first, detached and cached.
Downloading a model needs the client's or owner's approval.

## Measuring noise

- Use flat, still patches in **shadow/midtone blocks (mean 30-150 of 255)**.
  "Flattest block" picks clipped sky with zero noise; patches with print or
  moving people measure texture or motion.
- Look at 100-200 % crops of flat dark areas, old vs new, on the same frame.
- Check frame count, timing, and colour on one real shot after NR (each
  denoised frame must match its own source frame).
- The 4K → 1080p downscale already removes much of the noise; measure after it.
