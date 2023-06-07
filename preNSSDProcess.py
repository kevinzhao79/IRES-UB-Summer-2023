import pocketsphinx as ps

"""Completes requirements for pre-NSSD processing, including detecting basic NSS ('uh') and pauses (Setup)"""
class PreNSSDProcess:
    
    num_pause = 0
    num_nss = 0

    """determines total num of pauses and increments numpause"""
    def detect_pause():
        print("hi")

    #counts total num of instances of NSS on transcription and increments num_nss as so
    def detect_nss():
         print("hi")
    #finds all potential instances of NSS in transcription, including sounds within words
    def find_all():
         print("hi")
    #filters thu find_all() output to determine whether the NSS was found within a word    
    def filter(): 
         print("hi")
    #combines all pre-NSSD processed information into the desired output format
    def __repr__(self):
         print("hi")
        