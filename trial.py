from emora_stdm import DialogueFlow, Macro, Ngrams
import re
from typing import Dict, Any, List
from enum import Enum

import pickle
import time
import json
import requests

import random
import openai

import utils
from utils import MacroGPTJSON, MacroNLG

def load():
    with open('question_bank.json', "r") as f:
        stuff = json.load(f)
    return stuff

categories = ['technical', 'leadership', 'culture', 'cognitive']
global_var_state = random.choice(categories)
bank = load() #key category, value dictionary with question, list pairs


class MacroGetBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global global_var_state
        global bank
        global categories
        # global dialogue
        # stuff to select a question to ask
        if len(categories) > 0:
            rand_index = random.randint(0, len(categories) - 1)
            global_var_state = categories.pop(rand_index)
            question = "No question selected"
            dict = bank[global_var_state]  # dict of {Big_Question:Follow-ups}
            qs = list(dict.keys())  # Big_Questions at least two
            question = random.choice(qs)
            #print(dict)
            follow_ups = [v for v in dict[question]]
            dict.pop(question) #removes the big question
            # print(dict)
            # print("question", question)
            # print("follow-ups", follow_ups)
            vars["follow_ups"] = follow_ups
            # dialogue.append('S: ' + question)
            return question   
        else: 
            return "whoo! That was it!"               

class MacroGetLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        # global dialogue

        if len(vars["follow_ups"]) == 0:
            vars["Q_REMAIN"] = False
            vars["NO_FOLLOWUP"] = True


        #str = 'That should be good enough to cover $CURR STATE
            str= 'OK. All of that is good to hear'
            # dialogue.append('S: ' + str)
            return str
        else:
            res = random.choice(vars["follow_ups"])
            idx= vars["follow_ups"].index(res)
            vars["follow_ups"].pop(idx)
            vars["Q_REMAIN"] = True
            vars["NO_FOLLOWUP"] = False
            # dialogue.append('S: ' + res)
            return res
    
def interviewBuddy() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '#GET_BIG': {
            'error' : {
                '#GET_LITTLE' : {
                    'error' : {
                        '`ok!`' : 'start'
                    }
                }
            }
        }, 
        'error' : {
            '`BYE`' : 'end'
        },
    }

    macros = {
        'GET_BIG' : MacroGetBigQuestion(),
        'GET_LITTLE' : MacroGetLittleQuestion()
    }

    df = DialogueFlow('start', end_state='end')
    df.load_transitions(transitions)
    df.add_macros(macros)
    return df

if __name__ == '__main__':
    interviewBuddy().run()

