import sys

import pocketsphinx as ps
from pocketsphinx import AudioFile

import Setup as Setup
from Setup import Setup
import Word as Word
import PreNSSDProcess as PreNSSDProcess
from PreNSSDProcess import PreNSSDProcess

"""
The Driver class, responsible for initializing the backend classes (Setup, PreNSSDPRocess),
checking user-inputted arguments, outputting one of several text outputs (defined below).

The Command Line Arguments for this program are detailed as follows:

python3 Driver.py [relative path of audio file] [file with keywords] [keyword_threshold]
"""

class Driver:

    align_text = "i don't really know about that one i will get back to you regarding that sometime late today"
    #PocketSphinx Decoder class object
    dc = ps.Decoder

    setup_dc = None

    config = None

    #Setup class object
    setup = None

    #PreNSSDProcess class object
    pre = None

    #Audio file relative path
    file = None

    #List of NSS keywords to check
    nss = None

    #NSS threshold to check for
    threshold = None

    def __init__(self, setup, pre):
        self.setup = setup
        self.pre = pre

    #checks to ensure that there are the correct number of CLA
    def check_argv(self):
        if len(sys.argv) < 4:
            print("Error: Incorrect number of Command-Line Arguments: Should be 4, but was " + str(len(sys.argv)))
            return

    #convert CMA into local vars
    def update_argv(self):
        self.file = sys.argv[1]
        self.nss = sys.argv[2]
        self.threshold = sys.argv[3]
        self.config = ps.Config(
               fdict='nssd-dict.dict',
               frate=100,
               silprob=.001,
               fillprob=.001,
               kws = self.nss,
               kws_delay=100,
               kws_plp=1,
               kws_threshold = self.threshold
          )

    #see if the file path is valid
    def check_audio(self):

        self.setup_dc = ps.Decoder(self.config)

        with open(self.file, 'rb') as f:
               self.setup_dc.set_align_text(self.align_text)
               self.setup_dc.start_utt()  # Begin utterance
               while True:
                    buf = f.read(1024)
                    if buf:
                         self.setup_dc.process_raw(buf, False, False)
                    else:
                         break
               self.setup_dc.end_utt()  # End utterance

        self.setup.transcribe(self.setup_dc.seg())

    #see if the keywords are parseable as a str
    def check_kw(self):
        if not type(self.nss) == str:
            print("Error: keyword file is not a parseable string.\n")
            return


    #see if the keyword threshold is a number and between 1e-1 and 1e-50
    def check_threshold(self):
        try:
            self.threshold = float(self.threshold)
            if self.threshold > 1e-1 or self.threshold < 1e-50:
                print("Error: keyword threshold must be between 1e-1 and 1e-50.")
                return
        except:
            print("Error: keyword threshold not parseable as an int.")
            return

    #Initializes the PreNSSDProcess object needed to run the program
    def init_pre(self):
        self.pre = PreNSSDProcess(self.setup.word_list)
        self.pre.detect_pause(self.setup.word_list)

        #Run separate NSS detection tests for each NSS
        self.pre.detect_nss(self.file, self.nss, self.threshold)
        #print(self.pre.nss_list)

        self.pre.pause_filter(50)
        self.pre.combine()
        self.pre.remove_dups()
        self.pre.sort_lists()
        self.pre.update_size()

    #adds more dictionary definitions for NSS's for them to be more easily recognized
    #defect, for now
    def add_defs(self):
        #self.dc.add_word('mm', 'M HH')
        #self.dc.add_word("uh", "AH HH")
        #self.dc.add_word("uh", "AO")
        #self.dc.add_word("uh", "AO HH")
        #self.dc.add_word("um", "AO M")
        pass

    def output(self):
        print("Number of NSS sounds detected: " + str(self.pre.num_nss))
        print("Number of pauses detected: " + str(self.pre.num_pause))

        #prints just the words of the combined transcription
        string = "\n"
        for word in self.pre.combined_transcription:
            string += word.name
            string += " "
        string += "\n"
        print(string)

    def __repr__(self):
        string = "\n"
        for word in self.pre.combined_transcription:
            string += word.__repr__()
        
        return string

    #Handler function that calls all other driver functions
    def driver_handler(self):
        self.check_argv()
        self.update_argv()
        self.check_audio()
        self.check_kw()
        self.check_threshold()
        self.add_defs()
        self.init_pre()
        print(self.__repr__())        #prints full combined transcription data
        #self.output()                 #prints readable combined transcription
        #print(self.pre.nss_list)      #prints out all nss data

def main():

    driver = Driver(Setup, PreNSSDProcess)
    driver.driver_handler()

main()                                                                                                                #first pass
#pocketsphinx align [relative path of audio file] [first pass transcription] | jq '.w[]|.t' > [output text file]      #second pass