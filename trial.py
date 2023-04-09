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
globalCount = {'technical':0, 'leadership':0, 'culture':0, 'cognitive':0}
globalCounter = 0
dialogue_counter = 0 #counter



class MacroGetBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global global_var_state, bank, categories, dialogue_counter, globalCounter, globalCount
        question = "whoo! That was it!"
        # global dialogue
        # stuff to select a question to ask
        if dialogue_counter != 8 :
            # rand_index = random.randint(0, len(categories) - 1)
            # global_var_state = categories.pop(rand_index) # used for condition when it was len(categories) = 0
            global_var_state = random.choice(categories)
            globalCount[global_var_state] = (globalCount[global_var_state] + 1)
            # print("the category is: ", global_var_state, " and the counter for Q's is ", globalCount[global_var_state])

            # if(globalCount[global_var_state] == 2): 
            #     categories.remove(global_var_state)
            #     del bank[global_var_state]
            #     global_var_state = random.choice(categories)
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
            vars['stopper'] = "Go"
            dialogue_counter = dialogue_counter + 1
            return question              
            # dialogue.append('S: ' + question)
        else: 
            vars['stopper'] = "Stop"
            question = "whoo! That was it!"
            return question              

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
            '#IF($stopper=Go)' : {
                '#GET_LITTLE' : {
                    'error' : {
                        '`ok!`' : 'start'
                    }
                }
            }, 
            '#IF($stopper=Stop)' : {
                '`Bye!`' : 'end'
            }
        }
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

