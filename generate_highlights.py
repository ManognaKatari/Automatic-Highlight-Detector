from moviepy import VideoFileClip, concatenate_videoclips

# ---- Paste your top windows here (from threshold_detector.py output) ----
highlight_windows = [
    (1346.5, 1353.7),
    (1355.8, 1367.7),
    (2212.6, 2228.1),
    (5288.2, 5294.6),
    (5373.6, 5385.9),
    (5455.8, 5470.2),
    (5478.9, 5499.3),
    (5502.5, 5513.4),
    (6300.5, 6309.9),
    (7471.6, 7478.7),
    (7788.7, 7809.8),
    (7849.0, 7854.8),
    (7881.0, 7886.1),
    (7889.1, 7901.8),
    (7925.2, 7933.0),
    (8365.6, 8371.7),
    (8676.2, 8695.4),
    (9037.6, 9045.3),
    (9085.1, 9092.0),
    (9186.4, 9197.7),
]

# ---- Add a small buffer before/after each clip for context ----
buffer_before = 1.5  # seconds before the detected spike
buffer_after = 1.5   # seconds after the detected spike

print("Loading video...")
video = VideoFileClip("match.mp4")
video_duration = video.duration

clips = []
for i, (start, end) in enumerate(highlight_windows):
    padded_start = max(0, start - buffer_before)
    padded_end = min(video_duration, end + buffer_after)
    print(f"Cutting clip {i+1}/{len(highlight_windows)}: {padded_start:.1f}s -> {padded_end:.1f}s")
    clip = video.subclipped(padded_start, padded_end)
    clips.append(clip)

print("Concatenating clips...")
final = concatenate_videoclips(clips)

print("Writing final highlight reel...")
final.write_videofile("highlight_reel.mp4", codec="libx264", audio_codec="aac")

print("Done! Saved as highlight_reel.mp4")