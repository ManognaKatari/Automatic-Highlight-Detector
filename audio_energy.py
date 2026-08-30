import librosa
import matplotlib.pyplot as plt

y, sr = librosa.load("match_audio.wav")
energy = librosa.feature.rms(y=y)[0]

plt.plot(energy)
plt.savefig("audio_energy.png")