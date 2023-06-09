import math
class Word:
    
    def __init__(self, name, phonemes, start, end, score):
        self.name = name
        self.phonemes = phonemes
        self.start = start
        self.end = end
        
        #converts original PS confidence score into a percentage
        self.score = pow(1.0001, score) * 100

#    def __repr__(self):
 #       return f"Word: {self.name}, Phonemes: {self.phonemes}, Start: {self.start}, End: {self.end}, Confidence: {self.score}.\n"

    
