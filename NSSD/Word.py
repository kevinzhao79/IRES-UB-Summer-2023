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
        score = float(score)

        #some scores from the fdict register as a decimal while others as PS's own log 1.0001 score, 
        #thus we have to handle the two groups differently
        if score >= 0.0:
            self.score = score 
        else:
            self.score = pow(1.0001, score)

        #turn decimal into percentage
        self.score *= 100

        #cut off after 2 decimals
        self.score = round(self.score, 2)

    def get_start(self):
        return self.start

    def get_score(self):
        return self.score

    def __repr__(self):
        return f"Word: {self.name}, Time: {self.start/100}s - {self.end/100}s, Confidence: {self.score}\n"

    
