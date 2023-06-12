import os, sys

import pocketsphinx as ps
from pocketsphinx import AudioFile

import Setup as Setup
from Setup import Setup
import Word as Word
from Word import Word
import PreNSSDProcess as PreNSSDProcess
from PreNSSDProcess import PreNSSDProcess

"""
The driver class for the baseline NSSD program. The CLA for this program are as follows:

python3 Driver.py [relative path of audio file] [keyword 1] [keyword 2] ... [keyword <n>] [keyword_threshold]
"""
def main():

    if len(sys.argv) < 4:
        print("Error: Incorrect number of Command-Line Arguments: Should be at least 4, but was " + str(len(sys.argv)))
        return

    #convert CMA into local vars
    file = sys.argv[1]
    nss = []
    for i in range(2, len(sys.argv) - 1):
        nss.append(sys.argv[i])
    threshold = sys.argv[len(sys.argv) - 1]


    #see if the file path is valid
    try:
        audio = AudioFile(file)
        Setup.transcribe(audio)
        Setup.separate(Setup.ts_transcription)
    except:
        print("Error: audio file path invalid.\n")

    #see if the keywords are parseable as a str
    for i in range(0, nss.__len__()):
        if not isinstance(nss[i], str):
            print("Error: keyword " + str(i) + " is not of type string.\n")
            return

    #see if the keyword threshold is a number and between 1e-1 and 1e-50
    try:
        num_threshold = float(threshold)
        if num_threshold > 1e-1 or num_threshold < 1e-50:
            print("Error: keyword threshold must be between 1e-1 and 1e-50.")
            print(threshold)
            return
    except:
        print("Error: keyword threshold not parseable as an int.")
        print(type(num_threshold))
        return

    process = PreNSSDProcess(Setup.word_list)
    process.detect_pause(Setup.word_list)
    for i in range(0, nss.__len__()):
        process.detect_nss(file, nss[i], num_threshold)
    
    process.sort_nss()
    process.combination_transcription()

    print("Number of NSS sounds detected: " + str(process.num_nss))
    print("Number of pauses detected: " + str(process.num_pause))

    string = "\n"
    for word in process.combined_transcription:
        string += word.name
        string += " "
    string += "\n"
    print(string)

     
main()