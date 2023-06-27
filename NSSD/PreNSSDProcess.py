import pocketsphinx as ps
import Setup as Setup
import Word as Word
from Word import Word


"""Completes requirements for pre-NSSD processing, including detecting basic NSS's and pauses"""
class PreNSSDProcess:

     #PocketSphinx Config class object
     config = None

     #PocketSphinx Decoder class object
     decoder = None

     #PocketSphinx Segmenter class object
     segmenter = None

     # "../audio/1.wav"'s manual transcription for alignment
     align_text = "uh i don't uh really know about that one i will get back to you regarding that uh sometime late today"
    
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

     #Takes word list from NSSD.Setup class
     def __init__(self, word_list):
         self.word_list = word_list

     #initializes the necessary PocketSphinx classes to perform STT
     def ps_settings(self, nss, threshold):
          self.config = ps.Config(
               fdict='nssd-dict.dict',
               frate=100,
               silprob=.001,
               fillprob=.001,
               kws = nss,
               kws_delay=100,
               kws_plp=1,
               kws_threshold = threshold
          )
          self.decoder = ps.Decoder(self.config)
          self.segmenter = ps.Segmenter(sample_rate=16000, frame_length=0.01)

     #Converts segments created by ps.Decoder into NSSD.Word objects usable by the class
     def wordify(self):

          if self.decoder.hyp() != None:
               for seg in self.decoder.seg():
                    new_word = Word(seg.word, seg.start_frame, seg.end_frame, seg.prob)
                    self.nss_list.append(new_word)

          self.word_list_filter()

     #Gets rid of unnecessary items from the initial PS transcription
     def word_list_filter(self):

          to_remove = []

          for word in self.word_list:
               if word.name == "<s>" or word.name == "[SPEECH]" or word.name == "[NOISE]" or word.name == "</s>":
                    to_remove.append(word)

          for word in to_remove:
               self.word_list.remove(word)

     #determines total num of pauses within the original transcription
     def detect_pause(self, word_list):
        for unit in word_list:
          if unit.name == "<sil>":
               unit.name = "<pause>"
               self.nss_list.append(unit)

     #finds all potential instances of NSS in transcription, including sounds within words
     def find_all(self, file, nss, threshold):

          self.ps_settings(nss, threshold)

          with open(file, 'rb') as f:
               self.decoder.set_align_text(self.align_text)
               self.decoder.start_utt()  # Begin utterance
               while True:
                    buf = f.read(1024)
                    if buf:
                         self.decoder.process_raw(buf, False, False)
                    else:
                         break
               self.decoder.end_utt()  # End utterance

          #turns segmented output into list form
          self.wordify()

         
     #filters through find_all() output to determine whether detected NSS's were true/false positives
     def nss_filter(self): 

          #after each filter, add all elements to be removed
          #to this set and remove them at the end
          to_remove = set()

          print(self.nss_list)

          nss_filtered_once = filter(self.first_filter, self.nss_list)
          for nss in nss_filtered_once:
               to_remove.add(nss)

          print(to_remove.__len__())

          nss_filtered_twice = filter(self.second_filter, self.nss_list)
          for nss in nss_filtered_twice:
               to_remove.add(nss)

          print(to_remove.__len__())

          nss_filtered_thrice = filter(self.third_filter, self.nss_list)
          for nss in nss_filtered_thrice:
               to_remove.add(nss)

          print(to_remove.__len__())

          for nss in to_remove:
               self.nss_list.remove(nss)

     #filters through and removes NSS's that were detected within other words
     def first_filter(self, nss):
          start = nss.start
          end = nss.end

          return False         #essentially disables this filter

          for word in self.word_list:
               if abs(start - word.start) <= 1 and abs(end - word.end) <= 1:
                    return True

               elif abs(word.start - start) <= 1 and end < word.end:
                    return True
               
               elif abs(word.end - end) <= 1 and start > word.start:
                    return True

          return False

     #filters through all NSS's in the initial filtered list, and removes any 'duplicate' NSS's
     #a.k.a. sounds that were recognized as multiple NSS's by the program will only be recognized
     #as the NSS with the best accuracy over the sound's time frame
     def second_filter(self, nss):
          start = nss.start
          end = nss.end
          score = nss.score

          #return False

          #current threshold: .10 seconds
          for word in self.nss_list:
               if (abs(word.start - start) <= 3 and abs(word.end - end) <= 3) and score < word.score:
                    return True

          return False

     #filteres through all NSS's and removes impossibly short or low confidence ones.
     def third_filter(self, nss):

          start = nss.start
          end = nss.end
          score = nss.score
          if score < 86.5:
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
          self.nss_list.sort(key=lambda w: (w.start + w.end)/2)
          self.combined_transcription.sort(key=lambda w: (w.start + w.end)/2)

     #Updates the number of NSS's in the combined transcription
     def update_size(self):
          for word in self.combined_transcription:
               if word.name == '<pause>':
                    self.num_pause += 1
          
          self.num_nss = self.nss_list.__len__()

     #removes all detected pauses below the time threshold (default = 0.50 seconds)
     def pause_filter(self, threshold):

          if type(threshold) != int or type(threshold) != float:
               threshold = 25

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
          finaloutput += f"NSS: {nss.name}, Time: {nss.start/100}s - {nss.end/100}s Score: {round(nss.score, 2)}\n"
         return finaloutput

        