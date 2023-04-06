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

global_var_state = 'techincal'

def load():
    with open('question_bank.json', "r") as f:
        stuff = json.load(f)
    return stuff

class MacroGetBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global global_var_state
        #stuff to select a question to ask
        question = "No question selected"
        bank  = load()
        if global_var_state == 'techincal':
            dict = bank["technical"] #dict of {Big_Question:Follow-ups}
            qs = list(dict.keys()) #Big_Questions at least two
            question = random.choice(qs)
            # print("question", question)
            follow_ups = [v for v in dict[question]]
            # print("follow-ups", follow_ups)
            vars["follow_ups"] = follow_ups
        return question

class MacroGetLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        return random.choice(vars["follow_ups"]) 
    
def interviewBuddy() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '`Hello, how can I help you?`': {
            '#GET_BIG': {
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
