import pocketsphinx as ps
from pocketsphinx import AudioFile

"""Completes requirements for pre-NSSD processing, including detecting basic NSS ('uh') and pauses (Setup)"""
class PreNSSDProcess:
    
    num_pause = 0
    num_nss = 0
    potential_nss = None
    word_lst = None

    def __init__(self, word_lst):
         self.word_lst = word_lst

    """determines total num of pauses and increments numpause"""
    def detect_pause(word_lst):
        for unit in word_lst: 
          if unit.name == "<sil>":
               PreNSSDProcess.num_pause += 1

    #counts total num of instances of NSS on transcription and increments num_nss as so
    def detect_nss():
         print("hi")
    #finds all potential instances of NSS in transcription, including sounds within words
    def find_all(file, nss, threshold):
         audio = AudioFile(file, keyphrase=nss, kws_threshold=threshold)
         for phrase in audio:
          PreNSSDProcess.potential_nss = phrase.segments(detailed=True)
         
    #filters thru find_all() output to determine whether the NSS was found within a word    
    def filter(nss, nss_lst): 
         for pot_nss in nss_lst:
          if pot_nss.name == nss:
               pass
               
    #combines all pre-NSSD processed information into the desired output format
    def __repr__(self):
         print("hi")
        