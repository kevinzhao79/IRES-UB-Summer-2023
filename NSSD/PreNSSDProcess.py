import pocketsphinx as ps
from pocketsphinx import AudioFile
import Setup as Setup
from Setup import Setup
import collections
import Word as Word
from Word import Word


"""Completes requirements for pre-NSSD processing, including detecting basic NSS ('uh') and pauses (Setup)"""
class PreNSSDProcess:
    
     #number of detectable pauses within the original transcription
     num_pause = 0
    
     #number of detected NSS's within the original transcription
     num_nss = 0

     #all potential NSS's in segment form
     nss_transcription = None

     #all potential NSS's in list form
     potential_nss = collections.deque()

     #all NSS's that were picked up after the first filter
     filtered_nss = collections.deque()

     #list of words obtained from setup containing full transcription
     word_lst = collections.deque()

     def __init__(self, word_lst):
         self.word_lst = word_lst

     def wordify(self):
          for unit in self.nss_transcription:
            new_word = Word(unit[0], None, unit[2], unit[3], unit[1])
            self.potential_nss.append(new_word)

     """determines total num of pauses and increments numpause"""
     def detect_pause(self, word_lst):
        for unit in word_lst:
          #if PS marks unit as silence, increment numpause 
          if unit.name == "<sil>":
               self.num_pause += 1

        return self.num_pause

     #finds all potential instances of NSS in transcription, including sounds within words
     def find_all(self, file, nss, threshold):
         audio = AudioFile(file, keyphrase=nss, kws_threshold=threshold)
         for phrase in audio:
          self.nss_transcription = phrase.segments(detailed=True)

         #turns segmented output into list form
         self.wordify()

         
     #filters thru find_all() output to determine whether the NSS was found within a word    
     def nss_filter(self): 
          nss_filtered_iterable = filter(self.nss_filter_helper, self.potential_nss)
          for nss in nss_filtered_iterable:
               self.filtered_nss.append(nss)
     
     #1. Grab start/end times of NSS to look through (repeat for all NSS in list)
     #2. Loop through transcription list to check if any words fall into that range
     #3. If so, then the NSS is invalid, and vice versa
     #4. Output all valid NSS into the filtered list
     def nss_filter_helper(self, potential_nss):
          starttime = potential_nss.start
          endtime = potential_nss.end

          for word in self.word_lst:
               if word.start <= starttime and word.end >= endtime: return False

          return True
         
     #calls find_all and filter to obtain final nss count
     def detect_nss(self, file, nss, threshold):
         self.find_all(file, nss, threshold)
         self.nss_filter()
               
     #combines all pre-NSSD processed information into the desired output format
     def __repr__(self):
         finaloutput = "\n"
         for nss in self.filtered_nss:
          finaloutput += f"NSS: {nss.name}, Phonemes: {nss.phonemes}, Start: {nss.start}, End: {nss.end}, Confidence: {nss.score}.\n"
         return finaloutput


def main():
     file = "../audio/1.wav"
     nss = "uh"
     threshold = "1e-20"
     audio = AudioFile(file)
     Setup.transcribe(audio)
     Setup.separate(Setup.ts_transcription)
     process = PreNSSDProcess(Setup.word_list)
     process.detect_nss(file, nss, threshold)
     print(process.detect_pause(Setup.word_list))
     print(process.__repr__)
     
main()
        