import pocketsphinx as ps
from pocketsphinx import AudioFile
import Setup as Setup
import Word as Word
from Word import Word


"""Completes requirements for pre-NSSD processing, including detecting basic NSS's and pauses"""
class PreNSSDProcess:
    
     #number of detectable pauses within the original transcription
     num_pause = 0
    
     #number of detected NSS's within the original transcription
     num_nss = 0

     #all potential NSS's in segment form
     nss_transcription = []

     #all NSS's in list form
     nss_list = []

     #list of words obtained from setup containing full transcription
     word_list = []

     #combination of double_filtered_nss and word_lst
     combined_transcription = []

     def __init__(self, word_list):
         self.word_list = word_list

     def wordify(self):
          for unit in self.nss_transcription:
            new_word = Word(unit[0], unit[2], unit[3], unit[1])
            self.nss_list.append(new_word)

     """determines total num of pauses and increments numpause"""
     def detect_pause(self, word_list):
        for unit in word_list:
          if unit.name == "<sil>":
               self.num_pause += 1
               unit.name = "<pause>"
               self.nss_list.append(unit)

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
          nss_filtered_once = filter(self.nss_filter_helper, self.nss_list)
          for nss in nss_filtered_once:
               self.nss_list.remove(nss)

          #second filter of three
          nss_filtered_twice = filter(self.self_filter, self.nss_list)
          for nss in nss_filtered_twice:
               self.nss_list.remove(nss)
     
     #1. Grab start/end times of NSS to look through (repeat for all NSS in list)
     #2. Loop through transcription list to check if any words fall into that range
     #3. If so, then the NSS is invalid, and vice versa
     #4. Output all valid NSS into the filtered list
     def nss_filter_helper(self, nss):
          start = nss.start
          end = nss.end

          for word in self.word_list:
               if word.start - 3 <= start and word.end - 3 >= end: 
                    return True

          return False
         
     #calls find_all and filter to obtain final nss count
     def detect_nss(self, file, nss, threshold):
         self.find_all(file, nss, threshold)
         self.nss_filter()

     #removes duplicates from the nss and combined lists by converting to and back from a dictionary
     def remove_dups(self):
          self.nss_list = list(dict.fromkeys(self.nss_list))
          self.combined_transcription = list(dict.fromkeys(self.combined_transcription))

     #sorts nss and combined lists by start time, ascending
     def sort_lists(self):
          self.nss_list.sort(key=lambda w: w.start)
          self.combined_transcription.sort(key=lambda w: w.start)

     #Updates the number of NSS's in the combined transcription
     def update_size(self):
          self.num_nss = self.nss_list.__len__() - self.num_pause

     #filters through all NSS's in the initial filtered list, and removes any 'duplicate' NSS's
     def self_filter(self, nss):
          start = nss.start
          end = nss.end
          score = nss.score

          #current threshold: .03 seconds
          for word in self.nss_list:
               if (abs(word.start - start) <= 3 or abs(word.end - end) <= 3) and score < word.score:
                    return True
          
          return False

     #combines doubly filtered NSS list and word transcription list
     def combine(self):
          for word in self.word_list:
               self.combined_transcription.append(word)
          
          for nss in self.nss_list:
               self.combined_transcription.append(nss)
               
     #combines all pre-NSSD processed information into the desired output format
     def __repr__(self):
         finaloutput = "\n"
         for nss in self.combined_transcription:
          finaloutput += f"NSS: {nss.name}, Time: {nss.start/100}s - {nss.end/100}s Confidence: {round(nss.score, 2)}.\n"
         return finaloutput

        