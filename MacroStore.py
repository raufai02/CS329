from enum import Enum
from typing import Dict, Any, List
import random
import openai
from emora_stdm import DialogueFlow, Macro, Ngrams,

class Dialogue(Enum):
    call_names = 0,  # str
    JobDescription = 1  # str (?)
    DialogueList = 2 # a list of Thread objects

class Thread(Enum): #a list of questions with responses (1 main question and follow ups)
    list_questions = 1

class Question(Enum):
    question = 1 #str
    response = 2 #str


class MacroStoreQuestion(Macro): #store the last response!
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        num_threads = len(user[Dialogue.DialogueList])  # current length of DialogueList
        num_questions = len(user[Dialogue.DialogueList[num_threads - 1]])  # number of questions in the final item in list
        vars[Dialogue.DialogueList[num_threads-1][num_questions-1].response.name] = Ngrams.text()
        vars[Dialogue.DialogueList[num_threads - 1][num_questions - 1].question.name] = vars['QUESTION']
        # vars['QUESTION'] should store the most recent Q, set in funciton GET_QUESTION




