#import os
#from pocketsphinx import LiveSpeech, get_model_path

#speech = LiveSpeech(
#    sampling_rate=16000,
#)

#for phrase in speech:
#    print(phrase)

from pocketsphinx import AudioFile
audio = AudioFile("audio/1.wav", keyphrase='uh', kws_threshold=1e-1)
for phrase in audio: 
    print(phrase.segments(detailed=True))
    print(audio.prob)