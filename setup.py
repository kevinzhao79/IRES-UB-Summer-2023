#imports
import pocketsphinx as ps
from pocketsphinx import AudioFile
import collections
import Word
from Word import Word

class Setup:

    #timestamped transcription in PS list
    ts_transcription = None

    #linked list of words from transcription
    word_list = collections.deque()

    #converts audio into a transcription using PocketSphinx
    def transcribe(audio):

        for phrase in audio:
            Setup.ts_transcription = phrase.segments(detailed=True)

    """ partitions transcription list to separate each sound
        creates an object for the sound (Word)
        puts each object into a linked list """
    def separate(word_list):

        for unit in Setup.ts_transcription:

            new_word = Word(unit[0], None, unit[2], unit[3], unit[1])
            Setup.word_list.append(new_word)
