import pocketsphinx as ps
import Setup as Setup
import Word as Word
from Word import Word


"""Completes requirements for pre-NSSD processing, including detecting basic NSS's and pauses"""
class PreNSSDProcess:

     config = None
     decoder = None
     segmenter = None
    
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

     def ps_settings(self, nss, threshold):
          self.config = ps.Config(
               fdict='nssd-dict.dict',
               silprob=1e-50,
               fillprob=1e-50,
               kws = nss,
               kws_delay=20,
               kws_threshold = threshold
          )
          self.decoder = ps.Decoder(self.config)
          self.segmenter = ps.Segmenter(sample_rate=16000, frame_length=0.01)

     def wordify(self):

          if self.decoder.hyp() != None:
               for seg in self.decoder.seg():
                    new_word = Word(seg.word, seg.start_frame, seg.end_frame, seg.prob)
                    self.nss_list.append(new_word)
            
     """determines total num of pauses within the original transcription"""
     def detect_pause(self, word_list):
        for unit in word_list:
          if unit.name == "<sil>":
               unit.name = "<pause>"
               self.nss_list.append(unit)

     #finds all potential instances of NSS in transcription, including sounds within words
     def find_all(self, file, nss, threshold):

          self.ps_settings(nss, threshold)

          self.decoder.add_kws('nssd', nss)
          self.decoder.activate_search('nssd')

          with open(file, 'rb') as f:
               self.decoder.start_utt()  # Begin utterance
               while True:
                    buf = f.read(1024)
                    if buf:
                         self.decoder.process_raw(buf, False, False)
                    else:
                         break
               self.decoder.end_utt()  # End utterance

          #self.nss_transcription = self.segmenter.segment(self.nss_transcription)

          #turns segmented output into list form
          self.wordify()

         
     #filters thru find_all() output to determine whether the NSS was found within a word    
     def nss_filter(self): 

          #first filter of three
          nss_filtered_once = filter(self.first_filter, self.nss_list)
          for nss in nss_filtered_once:
               self.nss_list.remove(nss)

          #second filter of three
          nss_filtered_twice = filter(self.second_filter, self.nss_list)
          for nss in nss_filtered_twice:
               self.nss_list.remove(nss)

          nss_filtered_thrice = filter(self.third_filter, self.nss_list)
          for nss in nss_filtered_thrice:
               self.nss_list.remove(nss)

     #1. Grab start/end times of NSS to look through (repeat for all NSS in list)
     #2. Loop through transcription list to check if any words fall into that range
     #3. If so, then the NSS is invalid, and vice versa
     #4. Output all valid NSS into the filtered list
     def first_filter(self, nss):
          start = nss.start
          end = nss.end

          for word in self.word_list:
               if abs(start - word.start) <= 10 and abs(end - word.end) <= 10:
                    return True

               elif abs(word.start - start) <= 10 and end < word.end:
                    return True
               
               elif abs(word.end - end) <= 10 and start > word.start:
                    return True

          return False

     #filters through all NSS's in the initial filtered list, and removes any 'duplicate' NSS's
     def second_filter(self, nss):
          start = nss.start
          end = nss.end

          #current threshold: .10 seconds
          for word in self.nss_list:
               if abs(word.start - start) <= 10 or abs(word.end - end) <= 10:
                    return True
          
          return False

     #filteres through all NSS's in the doubly filtered lists and removes impossibly short or unconfident ones.
     def third_filter(self, nss):
          start = nss.start
          end = nss.end
          score = nss.score

          if end - start <= 5 or score < 86:
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
          for word in self.combined_transcription:
               if word.name == '<pause>':
                    self.num_pause += 1

          
          self.num_nss = self.nss_list.__len__() - self.num_pause

     #removes all detected pauses below the time threshold (default = 0.50 seconds)
     def pause_filter(self, threshold):

          if type(threshold) != int or type(threshold) != float:
               threshold = 50

          word_list_copy = self.word_list.copy()
          for word in word_list_copy:
               if word.name == '<pause>' and word.end - word.start < threshold:
                    self.word_list.remove(word)

          nss_list_copy = self.nss_list.copy()
          for word in nss_list_copy:
               if word.name == '<pause>' and word.end - word.start < threshold:
                    self.nss_list.remove(word)
                    self.num_pause -= 1

          combined_transcription_copy = self.combined_transcription.copy()
          for word in combined_transcription_copy:
               if word.name == '<pause>' and word.end - word.start < threshold:
                    self.combined_transcription.remove(word)


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
          finaloutput += f"NSS: {nss.name}, Time: {nss.start/100}s - {nss.end/100}s Confidence: {round(nss.score, 2)}\n"
         return finaloutput

        