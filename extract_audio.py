from moviepy import VideoFileClip

video = VideoFileClip("match.mp4")
video.audio.write_audiofile("match_audio.wav")