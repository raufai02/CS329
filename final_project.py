from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
from enum import Enum

import pickle
import time
import json
import requests

import random
import openai

#import utils
from utils import MacroGPTJSON, MacroNLG
from evaluation import transitions_evaluate, transitions_emotion, transitions_context, transitions_requirements
from transitions_intro import transitions_intro, transition_greetings, transitions_feeling,transitions_field, transitions_job
from transitions_intro import MacroEncourage

def load():
    with open('question_bank.json', "r") as f:
        stuff = json.load(f)
    return stuff

dialogue = [] #GLOBAL VARIABLE
dialogue_counter = 0 #counter
categories = ['technical', 'leadership', 'culture', 'cognitive']
global_var_state = random.choice(categories)
bank = load() #key category, value dictionary with question, list pairs
globalCount = {'technical':0, 'leadership':0, 'culture':0, 'cognitive':0}
globalCounter = 0
counter = 0

PATH_API_KEY = 'openai_api.txt'
openai.api_key_path = PATH_API_KEY

class V(Enum):
    call_name = 0,  # str

class MacroPersona(Macro): 
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        names = ['Maya', 'Ethan', 'Jenna', 'Charlie', 'Kattie', 'Adam', 'Luca', 'Jasmine', 'Omar', 'Jessica']
        chosenName = random.choice(names)
        field = vars['USER_FIELD']
        return f"Hi there! My name is {chosenName} working in {field} and I will be conducting the interview with you! I want to you to know that I am on your side throughout this process, just do your best when answering the questions. So let's start!"

class MacroSetBool(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        if len(args) != 2:
            return False

        variable = args[0]
        if variable[0] == '$':
            variable = variable[1:]

        boolean = args[1].lower()
        if boolean not in {'true', 'false'}:
            return False

        vars[variable] = bool(boolean)
        return True

class MacroWhatElse(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        strlist = []
        if 'requirements' not in vars: #not yet covered
            strlist.append("job requirements")
        if 'context' not in vars:
            strlist.append("context appropriateness")
        if 'emotion' not in vars:
            strlist.append("emotional appropriateness")

        output = "What area would you like feedback on? " + '[' + ', '.join(strlist) + ']'
        return output


class MacroLoadScores(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        filename = "scoring/" + vars["user_name"] + '.json'
        with open(filename, 'r') as f:
            data = json.load(f) #load the scoring file into the workspace!

        vars["TOTAL_SCORE"] = data["Total Score"]
        vars["EMOTION_SCORE"] = data["Emotion Score"]
        vars["CONTEXT_SCORE"] = data["Context Score"]
        vars["REQUIREMENT_SCORE"] = data["Requirement Score"]

class MacroGetExample(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        #filename = "scoring/" + vars["user_name"] + '.json'
        filename = 'IBM_goodScore.json'
        with open(filename, 'r') as f:
            data = json.load(f)  # load the scoring file into the workspace!

        positive = data["Positive Examples"][1] # should return an index

        negative = data["Negative Examples"][2].Reason #returns a sentence reasoning
        return negative

class MacroStoreResponse(Macro): #store the last response!
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        # num_threads = len(vars[Dialogue.DialogueList])  # current length of DialogueList
        # num_questions = len(user[Dialogue.DialogueList[num_threads - 1]])  # number of questions in the final item in list
        # vars[Dialogue.DialogueList[num_threads-1][num_questions-1].response.name] = Ngrams.text()
       # print(dialogue)
        global dialogue, dialogue_counter

        dialogue_counter = dialogue_counter + 1
        dialogue.append(str(dialogue_counter) +  ' U: ' + ngrams.text())
        return True
        # vars[Dialogue.DialogueList[num_threads - 1][num_questions - 1].question.name] = vars['QUESTION']


class MacroGetBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global global_var_state, bank, categories, dialogue, counter, globalCounter, globalCount, dialogue_counter
        if len(categories) != 0: 
            # stuff to select a question to ask
            question = "whoo! That was it!"
            # rand_index = random.randint(0, len(categories) - 1)
            # global_var_state = categories.pop(rand_index) # used for condition when it was len(categories) = 0
            global_var_state = random.choice(categories) #technical, leadership, culture, cognitive
            dict = bank[global_var_state]  # dict of {Big_Question:Follow-ups}
            categories.remove(global_var_state)
            key_list = list(dict.keys())
            qs = random.sample(key_list, 2) # Big_Questions at least two
            question = random.choice(qs)
            follow_ups = [v for v in dict[question]]
            dict.pop(question) #removes the big question
            vars["follow_ups"] = follow_ups
            vars['stopper'] = "Go"
            counter = counter + 1
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + ' S: ' + question)
            return question    
        else: 
            vars['stopper'] = "Stop"
            question = "whoo! That was it!"
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + ' S: ' + question)
            return question  
        
class MacroGetLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global dialogue, dialogue_counter
        if len(vars["follow_ups"]) == 0:
            vars["Q_REMAIN"] = False
            vars["NO_FOLLOWUP"] = True
            #str = 'That should be good enough to cover $CURR STATE
            str= 'OK. All of that is good to hear'
            dialogue.append('S: ' + str)
            return str
        else:
            res = random.choice(vars["follow_ups"])
            idx= vars["follow_ups"].index(res)
            vars["follow_ups"].pop(idx)
            vars["Q_REMAIN"] = True
            vars["NO_FOLLOWUP"] = False
            dialogue.append('S: ' + res)
            return res

def interviewBuddy() -> DialogueFlow:
    transitions = { #classification state
    'state' : 'interview',
    '#PERSONA' : { # insert persona macro - Ameer
        '#STORE' : {
        'state': 'big_q',
        '#GET_BIG': {
            '#IF($stopper=Go) #STORE': {
                'state': 'follow_up',
                '#GET_LITTLE': {
                    'error' : {
                        '`ok!`' : 'big_q'
                    }
                    # 'state': 'store_follow_up',
                    # '#IF($Q_REMAIN) #STORE':'follow_up',
                    # '#IF($NO_FOLLOWUP)': 'no_follow_up'
                },
            }, 
            '#IF($stopper=Stop)': {
                '#STORE `Thanks for chatting`#GET_NAME': 'start_evaluate'
            }
            }
        }
    }

    }
                
            # }
    transitions_no_follow = {
        'state': 'no_follow_up',
        '`Thanks for chatting ` #GET_NAME': {
            '#STORE': 'start_evaluate'
        }
    }

    macros = {
        'STORE': MacroStoreResponse(),
        'SET_CALL_NAMES': MacroGPTJSON(
            'How does the speaker want to be called?',
            {V.call_name.name: ["Mike", "Michael"]}),
        'GET_NAME': MacroNLG(get_call_name),
        'GET_BIG': MacroGetBigQuestion(),
        'GET_LITTLE' : MacroGetLittleQuestion(),
        'GET_CALL_NAME': MacroNLG(get_call_name),
        'LOAD_SCORES' : MacroLoadScores(),
        'GET_EXAMPLE' : MacroGetExample(),
        'WHAT_ELSE': MacroWhatElse(),
        'SETBOOL': MacroSetBool(),
        'ENCOURAGEMENT': MacroEncourage(), 
        'PERSONA' : MacroPersona(),
        'RUN_EVAL' : MacroLoadScores()

    }

    df = DialogueFlow('start', end_state='end')
    df.knowledge_base().load_json_file('cognitive_ontology.json')
    df.knowledge_base().load_json_file('cul_fit_ontology.json')
    df.knowledge_base().load_json_file('leadership_ontology.json')
    df.knowledge_base().load_json_file('tech_ontology.json')
    df.knowledge_base().load_json_file('major_ontology.json')
    df.load_transitions(transitions)
    df.load_transitions(transitions_no_follow)
    df.load_transitions(transitions_intro)
    df.load_transitions(transition_greetings)
    df.load_transitions(transitions_field)
    df.load_transitions(transitions_job)
    df.load_transitions(transitions_feeling)
    df.load_transitions(transitions_evaluate)
    df.load_transitions(transitions_context)
    df.load_transitions(transitions_requirements)
    df.load_transitions(transitions_emotion)
    df.add_macros(macros)

    return df

def get_call_name(vars: Dict[str, Any]):
    ls = vars[V.call_name.name]
    return ls[random.randrange(len(ls))]

def save(df: DialogueFlow, d: List[Any]): #d is the dialogue list
    df.run()
    vars = {k: v for k, v in df.vars().items() if not k.startswith('_')} #df vars (?)
    filename = vars["user_name"] + '.txt'
    fout = open(filename, 'w')
    fout.write('\n'.join(d))


if __name__ == '__main__':
    interviewBuddy().run()
    # save(interviewBuddy(),dialogue)