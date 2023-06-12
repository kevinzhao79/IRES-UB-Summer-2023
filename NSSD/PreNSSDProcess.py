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
     potential_nss = []

     #all NSS's that were picked up after the first filter
     filtered_nss = []

     #all NSS's that were picked up after the second filter
     double_filtered_nss = []

     #list of words obtained from setup containing full transcription
     word_lst = []

     #combination of double_filtered_nss and word_lst
     combined_transcription = []

     def __init__(self, word_lst):
         self.word_lst = word_lst

     def wordify(self):
          for unit in self.nss_transcription:
            new_word = Word(unit[0], unit[2], unit[3], unit[1])
            self.potential_nss.append(new_word)

     """determines total num of pauses and increments numpause"""
     def detect_pause(self, word_lst):
        for unit in word_lst:
          #if PS marks unit as silence, increment numpause 
          if unit.name == "<sil>":
               self.num_pause += 1
               unit.name = "<pause>"
               self.filtered_nss.append(unit)

     #finds all potential instances of NSS in transcription, including sounds within words
     def find_all(self, file, nss, threshold):
         audio = AudioFile(file, keyphrase=nss, kws_threshold=threshold)
         for phrase in audio:
          self.nss_transcription = phrase.segments(detailed=True)

         #turns segmented output into list form
         self.wordify()

         
     #filters thru find_all() output to determine whether the NSS was found within a word    
     def nss_filter(self): 

          #first filter of three
          nss_filtered_once = filter(self.nss_filter_helper, self.potential_nss)
          for nss in nss_filtered_once:
               self.filtered_nss.append(nss)

          #second filter of three
          nss_filtered_twice = filter(self.self_filter, self.filtered_nss)
          for nss in nss_filtered_twice:
               self.double_filtered_nss.append(nss)
     
     #1. Grab start/end times of NSS to look through (repeat for all NSS in list)
     #2. Loop through transcription list to check if any words fall into that range
     #3. If so, then the NSS is invalid, and vice versa
     #4. Output all valid NSS into the filtered list
     def nss_filter_helper(self, potential_nss):
          start = potential_nss.start
          end = potential_nss.end

          for word in self.word_lst:
               if word.start - 3 <= start and word.end - 3 >= end: 
                    return False

          return True
         
     #calls find_all and filter to obtain final nss count
     def detect_nss(self, file, nss, threshold):
         self.find_all(file, nss, threshold)
         self.nss_filter()

     #sorts filtered_nss list by start time, ascending
     def sort_nss(self):
          #removes duplicates from the list by converting to and back from a dictionary
          self.double_filtered_nss = list(dict.fromkeys(self.double_filtered_nss))

          #sorts the filtered list based on start times
          self.double_filtered_nss.sort(key=lambda w: w.start)

          self.num_nss = self.double_filtered_nss.__len__() - self.num_pause

     #filters through all NSS's in the initial filtered list, and removes any 'duplicate' NSS's
     def self_filter(self, filtered_nss):
          start = filtered_nss.start
          end = filtered_nss.end
          score = filtered_nss.score

          #threshold: .03 seconds
          for word in self.filtered_nss:
               if (abs(word.start - start) <= 3 or abs(word.end - end) <= 3) and score < word.score:
                    return False
          
          return True

     #combines doubly filtered NSS list and word transcription list
     def combination_transcription(self):
          for word in self.word_lst:
               self.combined_transcription.append(word)
          
          for nss in self.double_filtered_nss:
               self.combined_transcription.append(nss)
          
          self.combined_transcription = list(dict.fromkeys(self.combined_transcription))
          self.combined_transcription.sort(key=lambda w: w.start)

               
     #combines all pre-NSSD processed information into the desired output format
     def __repr__(self):
         finaloutput = "\n"
         for nss in self.combined_transcription:
          finaloutput += f"NSS: {nss.name}, Time: {nss.start/100}s - {nss.end/100}s Confidence: {round(nss.score, 2)}.\n"
         return finaloutput

        