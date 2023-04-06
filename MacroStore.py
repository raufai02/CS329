from enum import Enum
from typing import Dict, Any, List
import random
import openai
from emora_stdm import DialogueFlow, Macro, Ngrams,



class MacroStoreQuestion(Macro): #store the last response!
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        num_threads = len(user[Dialogue.DialogueList.name])  # current length of DialogueList
        num_questions = len(user[Dialogue.DialogueList[num_threads - 1]])  # number of questions in the final item in list
        vars[Dialogue.DialogueList[num_threads-1][num_questions-1].response.name] = Ngrams.text()
        vars[Dialogue.DialogueList[num_threads - 1][num_questions - 1].question.name] = vars['QUESTION']
        # vars['QUESTION'] should store the most recent Q, set in funciton GET_QUESTION

class MacroOutputDialogue(Macro): #AT THE END OF INTERVIEW + FEEDBACK PHASE!!!
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        lines = []
        for thread in vars[Dialogue.DialogueList.name]:
            for question in thread:
                lines.append("S:" + question.question)
                lines.append("U:" + question.response)

        filename = vars[Dialogue.callName] + '.txt'
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line)
                f.write('\n')
        close(filename)
        return True







