#imports
import pocketsphinx as ps
from pocketsphinx import AudioFile
import collections
import Word as Word
from Word import Word

class Setup:

    #timestamped transcription in PS list
    ts_transcription = None

    #linked list of words from transcription
    word_list = collections.deque()

    #converts audio into a transcription using PocketSphinx
    def transcribe(transcription):

        for phrase in transcription:
            new_word = Word(phrase.word, phrase.start_frame, phrase.end_frame, phrase.prob)
            Setup.word_list.append(new_word)
            
    """ partitions transcription list to separate each sound
        creates an object for the sound (Word)
        puts each object into a linked list """
    def separate(word_list):

        for unit in Setup.ts_transcription:

            new_word = Word(unit[0], unit[2], unit[3], unit[1])
            Setup.word_list.append(new_word)
