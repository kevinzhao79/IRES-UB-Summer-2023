class word:
    
    def __init__(self, name, phonemes, start, end, score):
        self.name = name
        self.phonemes = phonemes
        self.start = start
        self.end = end
        self.score = score

    def __repr__(self):
        return f"Word: {self.name}, Phonemes: {self.phonemes}, Start: {self.start}, End: {self.end}, Confidence: {self.score}.\n"

    
