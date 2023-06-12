import math
class Word:

    name = ""
    start = 0
    end = 0
    score = 0
    
    def __init__(self, name, start, end, score):
        self.name = name
        self.start = start
        self.end = end
        
        #converts original PS confidence score into a percentage
        self.score = pow(1.0001, score) * 100

    def get_start(self):
        return self.start

    def get_score(self):
        return self.score

    def __repr__(self):
        return f"Word: {self.name}, Time: {self.start/100}s - {self.end/100}s, Confidence: {round(self.score, 2)}.\n"

    
