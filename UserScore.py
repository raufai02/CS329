class UserScore:
    def __init__(self, name: string):
        self.name = name;
        self.emotionScore = 0;
        self.responseScore = 0;
        self.jobScore = 0;

#A score given to the user based on whether or not their emotions were appropriate in the interview context
    def add_emotionalScore(self, ePoints: float):
        self.emotionScore+=ePoints;

#Score given to user based on quality of response
    def add_responseScore(self, rPoints: int):
        self.responseScore+=rPoints;

# A score given to the user based on whether or not the response they gave matched a certain number of elements from the job description
    def add_jobScore(self, jPoints: int):
        self.jobScore += jPoints;



#@TODO
##NEED METHODS TO CALCULATE EACH OF THESE SCORES
# calculateResponseQ()
# 	calculateWordEfficiency()   return float 0->1
# 	calculateUniqueWords()    return float 0->1
# 	calculateAvPronounPref()  return float -1->1
# calculateEmotionScore()
# 	numPositiveEmotions() return int pos_emotions
# 	numNegativeEmotions() return int negative_emotions
# 	score_emotionalvalence()  return float -1 -> 1
# calculateJobScore()
# correctContext() return float 0->1 representing %of times user responses were context appropriate
# Q_skillMatched() return percentage of skills matched in a single response
# Av_skillMatched() return percentage of skills matched in the entire transcript of responses