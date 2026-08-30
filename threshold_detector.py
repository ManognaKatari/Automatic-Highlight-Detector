import librosa
import numpy as np

# ---- Load audio ----
y, sr = librosa.load("match_audio.wav")

# ---- Compute energy ----
energy = librosa.feature.rms(y=y)[0]
times = librosa.frames_to_time(np.arange(len(energy)), sr=sr)

# ---- Threshold ----
threshold = energy.mean() + 1.5 * energy.std()
highlight_frames = energy > threshold

print(f"Total frames: {len(energy)}")
print(f"Frames above threshold: {highlight_frames.sum()}")
print(f"Threshold value: {threshold:.4f}")
print(f"Energy min/mean/max: {energy.min():.4f} / {energy.mean():.4f} / {energy.max():.4f}")

# ---- Sustained window settings ----
frame_duration = 512 / sr
min_duration_frames = int(1.0 / frame_duration)  # ~1 second sustained
print(f"frame_duration: {frame_duration:.4f}s, min_duration_frames: {min_duration_frames}")

def rolling_mostly_true(arr, window, min_fraction=0.6):
    result = np.zeros(len(arr), dtype=bool)
    for i in range(len(arr) - window + 1):
        if arr[i:i+window].mean() >= min_fraction:
            result[i:i+window] = True
    return result

smoothed = rolling_mostly_true(highlight_frames, min_duration_frames, min_fraction=0.6)
print(f"Frames marked highlight after smoothing: {smoothed.sum()}")

# ---- Group into raw windows ----
highlight_windows = []
in_highlight = False
start_time = None

for i, is_hl in enumerate(smoothed):
    if is_hl and not in_highlight:
        in_highlight = True
        start_time = times[i]
    elif not is_hl and in_highlight:
        in_highlight = False
        end_time = times[i]
        highlight_windows.append((start_time, end_time))

if in_highlight:
    highlight_windows.append((start_time, times[-1]))

print(f"\nRaw candidate windows: {len(highlight_windows)}")

# ---- Merge windows that are close together ----
merged_windows = []
gap_threshold = 2.0  # seconds - merge windows closer than this

for start, end in highlight_windows:
    if merged_windows and start - merged_windows[-1][1] <= gap_threshold:
        prev_start, prev_end = merged_windows[-1]
        merged_windows[-1] = (prev_start, end)
    else:
        merged_windows.append((start, end))

print(f"After merging: {len(merged_windows)} windows")

# ---- Filter out anything shorter than 5 seconds ----
min_highlight_duration = 5.0  # seconds

filtered_windows = [(start, end) for start, end in merged_windows
                     if (end - start) >= min_highlight_duration]

print(f"After filtering (>= {min_highlight_duration}s): {len(filtered_windows)} windows\n")

# ---- Score each remaining window by peak energy ----
def window_peak_energy(start, end):
    mask = (times >= start) & (times <= end)
    return energy[mask].max() if mask.any() else 0

scored_windows = [(start, end, window_peak_energy(start, end)) for start, end in filtered_windows]

# sort by intensity, strongest first
scored_windows.sort(key=lambda w: w[2], reverse=True)

# ---- Keep only the top N most intense moments ----
top_n = 20
top_windows = scored_windows[:top_n]

# re-sort by time for readability
top_windows.sort(key=lambda w: w[0])

print(f"Top {min(top_n, len(top_windows))} highlight candidates (by intensity):\n")
for start, end, score in top_windows:
    duration = end - start
    print(f"  {start:.1f}s -> {end:.1f}s  (duration: {duration:.1f}s, peak energy: {score:.4f})")