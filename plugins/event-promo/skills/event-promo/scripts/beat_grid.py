#!/usr/bin/env python3
"""Beat grid of a music track: constant-tempo fit, extended to the final hit, with band energy per beat.

What it measures
  1. librosa tracks the beats (tightness 200).
  2. A constant-tempo grid is fitted to the tracked beats: bpm from a least-squares line through
     (beat index, time); snapped to a whole bpm when within SNAP_BPM of it; offset = mean residual.
     The fit residual (rms and max, in ms) tells you how well the track keeps time.
  3. The grid is extended to the track's final strong hit (the tracker stops early on a reverb tail,
     so the raw beat list would cut the ending). Override with --final-hit if detection picks the wrong hit.
  4. Downbeat phase (0-3): the phase whose beats carry the most low-frequency (<150 Hz) onset energy.
  5. Per-beat low / mid / high band energy (dB) and per-bar RMS and novelty, for a section map.

Gate values (calibrated on a 115 bpm electronic track, 2026-10)
  Fit residual rms <= ~5 ms and max <= ~15 ms means the track is a clean constant-tempo grid. A larger
  residual means a tempo drift or a live-played track: do not cut on a constant grid.

Output JSON (all times in seconds)
  {"file", "duration", "tempo" (librosa estimate),
   "grid": {"bpm", "period", "offset", "residual_rms_ms", "residual_max_ms", "final_hit", "final_hit_beat", "note"},
   "beats": [grid beat times, beat 0 .. final hit]        <- the file every other tool should read
   "beats_tracked": [raw librosa beats], "downbeat_phase": 0-3, "downbeats": [...],
   "band_energy_db": {"low": [...], "mid": [...], "high": [...]}   <- one value per entry of "beats"
   "band_edges_hz": [150, 2000], "bar_rms_db": [...], "bar_novelty": [...]}

Usage
  beat_grid.py track.wav grid.json
  beat_grid.py track.mp3 grid.json --final-hit 150.29 --bpm 115

Needs: numpy, librosa.
"""
import argparse
import json
import sys

import numpy as np
import librosa

HOP = 512
SR = 44100
LOW_HZ, MID_HZ = 150.0, 2000.0      # band edges: low < 150 Hz <= mid < 2 kHz <= high
SNAP_BPM = 0.05                     # calibrated on a 115 bpm track, 2026-10: snap the fitted tempo to a whole bpm within this
FINAL_HIT_DELTA = 0.1               # calibrated on a 115 bpm track, 2026-10: onset peak must exceed this fraction of the max onset strength


def track_beats(y, sr):
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset, sr=sr, hop_length=HOP, units='time', tightness=200)
    return onset, float(np.atleast_1d(tempo)[0]), np.asarray(beats, dtype=float)


def fit_grid(tracked, bpm=None):
    """Constant-tempo grid through the tracked beats. Returns (period, offset, index, residual_s)."""
    first = tracked[0]
    if bpm is None:
        rough = 60.0 / float(np.median(np.diff(tracked)))
        idx = np.round((tracked - first) / (60.0 / rough))
        A = np.vstack([idx, np.ones_like(idx)]).T
        (period, _), *_ = np.linalg.lstsq(A, tracked, rcond=None)
        bpm = 60.0 / period
        if abs(bpm - round(bpm)) <= SNAP_BPM:
            bpm = float(round(bpm))
    period = 60.0 / bpm
    idx = np.round((tracked - first) / period)
    offset = float(np.mean(tracked - idx * period))
    residual = tracked - (offset + idx * period)
    return bpm, period, offset, idx, residual


def detect_final_hit(y, sr):
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    pk = librosa.util.peak_pick(onset, pre_max=3, post_max=3, pre_avg=10, post_avg=10,
                                delta=float(onset.max()) * FINAL_HIT_DELTA, wait=10)
    if len(pk) == 0:
        return None
    return float(librosa.frames_to_time(pk[-1], sr=sr, hop_length=HOP))


def band_energy(y, sr, times):
    """Mean STFT power (dB) in low/mid/high bands over each beat interval."""
    S = np.abs(librosa.stft(y, hop_length=HOP)) ** 2
    freqs = librosa.fft_frequencies(sr=sr)
    t = librosa.times_like(S[0], sr=sr, hop_length=HOP)
    edges = np.append(times, times[-1] + (times[-1] - times[-2]))
    masks = {'low': freqs < LOW_HZ, 'mid': (freqs >= LOW_HZ) & (freqs < MID_HZ), 'high': freqs >= MID_HZ}
    out = {k: [] for k in masks}
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (t >= a) & (t < b)
        for k, m in masks.items():
            v = float(S[m][:, sel].mean()) if sel.any() else 0.0
            out[k].append(round(10 * np.log10(v + 1e-12), 1))
    return out


def downbeat_phase(y, sr, tracked):
    S = np.abs(librosa.stft(y, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr)
    low = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[freqs < LOW_HZ]), sr=sr, hop_length=HOP)
    bf = librosa.time_to_frames(tracked, sr=sr, hop_length=HOP)
    scores = [float(np.mean(low[bf[p::4]])) for p in range(4)]
    return int(np.argmax(scores)), scores


def bar_features(y, sr, downbeats):
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    rt = librosa.times_like(rms, sr=sr, hop_length=HOP)
    bar_rms = [round(float(20 * np.log10(np.mean(rms[(rt >= a) & (rt < b)]) + 1e-9)), 1)
               for a, b in zip(downbeats[:-1], downbeats[1:])]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=HOP)
    mf = librosa.feature.mfcc(y=y, sr=sr, hop_length=HOP, n_mfcc=13)
    feat = np.vstack([librosa.util.normalize(chroma, axis=0), librosa.util.normalize(mf, axis=0)])
    dbf = librosa.time_to_frames(downbeats, sr=sr, hop_length=HOP)
    sync = librosa.util.sync(feat, dbf, aggregate=np.mean)
    R = librosa.segment.recurrence_matrix(sync, mode='affinity', sym=True)
    K = 4
    n = R.shape[0]
    nov = np.zeros(n)
    ker = np.kron(np.array([[1, -1], [-1, 1]]), np.ones((K, K)))
    Rp = np.pad(R, K)
    for i in range(n):
        nov[i] = np.sum(Rp[i:i + 2 * K, i:i + 2 * K] * ker)
    return bar_rms, [round(float(v), 2) for v in nov]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('track', help='audio file (wav, mp3, ...)')
    ap.add_argument('out', help='output JSON path')
    ap.add_argument('--bpm', type=float, help='force the grid tempo instead of fitting it')
    ap.add_argument('--final-hit', type=float, metavar='SEC', help='time of the final strong hit (default: last strong onset)')
    ap.add_argument('--no-extend', action='store_true', help='do not extend the grid past the last tracked beat')
    ap.add_argument('--quiet', action='store_true', help='do not print the per-bar table')
    a = ap.parse_args()

    y, sr = librosa.load(a.track, sr=SR, mono=True)
    dur = len(y) / sr
    _, tempo, tracked = track_beats(y, sr)
    if len(tracked) < 8:
        sys.exit('fewer than 8 beats tracked: not a beat-driven track')
    bpm, period, offset, idx, resid = fit_grid(tracked, a.bpm)
    rms_ms, max_ms = float(np.sqrt((resid ** 2).mean()) * 1000), float(np.abs(resid).max() * 1000)

    last = int(idx[-1])
    hit = None
    if not a.no_extend:
        hit = a.final_hit if a.final_hit is not None else detect_final_hit(y, sr)
        if hit is not None:
            last = max(last, int(round((hit - offset) / period)))
    n_beats = last + 1
    beats = offset + np.arange(n_beats) * period

    phase, scores = downbeat_phase(y, sr, tracked)
    downbeats = tracked[phase::4]
    bar_rms, nov = bar_features(y, sr, downbeats)
    out = dict(
        file=a.track, duration=round(dur, 4), tempo=round(tempo, 3),
        grid=dict(bpm=round(float(bpm), 3), period=float(period), offset=float(offset),
                  residual_rms_ms=round(rms_ms, 2), residual_max_ms=round(max_ms, 2),
                  final_hit=None if hit is None else round(float(hit), 4), final_hit_beat=last,
                  note='constant-tempo fit to beats_tracked; extended to the final hit'),
        beats=[round(float(b), 4) for b in beats],
        beats_tracked=[round(float(b), 4) for b in tracked],
        downbeat_phase=phase, downbeats=[round(float(b), 4) for b in downbeats],
        band_energy_db=band_energy(y, sr, beats), band_edges_hz=[LOW_HZ, MID_HZ],
        bar_rms_db=bar_rms, bar_novelty=nov)
    with open(a.out, 'w') as f:
        json.dump(out, f)
    print(f'bpm {bpm:.3f} (librosa {tempo:.2f})  beats {n_beats} (tracked {len(tracked)})  first {beats[0]:.4f}  '
          f'last {beats[-1]:.4f}  residual rms {rms_ms:.1f} ms max {max_ms:.1f} ms  phase {phase} scores {scores}')
    if not a.quiet:
        thr = np.percentile(nov, 85)
        for i, (d, r, nv) in enumerate(zip(downbeats, bar_rms + [None], nov)):
            print(f'bar {i:3d} t={d:7.2f} rms={r} nov={nv:6.2f}' + ('  <==' if nv > thr else ''))


if __name__ == '__main__':
    main()
