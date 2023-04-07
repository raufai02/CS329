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

dialogue = [] #GLOBAL VARIABLE

PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

class V(Enum):
    call_name = 0,  # str


class MacroStoreResponse(Macro): #store the last response!
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        # num_threads = len(vars[Dialogue.DialogueList])  # current length of DialogueList
        # num_questions = len(user[Dialogue.DialogueList[num_threads - 1]])  # number of questions in the final item in list
        # vars[Dialogue.DialogueList[num_threads-1][num_questions-1].response.name] = Ngrams.text()
        print(dialogue)
        dialogue.append('U: ' + ngrams.text())
        return True
        # vars[Dialogue.DialogueList[num_threads - 1][num_questions - 1].question.name] = vars['QUESTION']

class MacroGetBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        #stuff to select a question to ask
        question = "No question selected"
        bank  = load()
        if global_var_state == 'techincal':
            dict = bank["technical"]
            qs = list(dict.keys())
            question = random.choice(qs)
            follow_ups = [v for v in question.values()]
            vars["follow_ups"] = follow_ups

        dialogue.append('S: ' + question) #append to store!
        return question

class MacroGetLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        return random.choice(vars["follow_ups"]) 



class MacroGreet(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):

        url = 'https://api.weather.gov/gridpoints/FFC/52,88/forecast'
        r = requests.get(url)
        d = json.loads(r.text)
        periods = d['properties']['periods']
        today = periods[0]
        #return today['detailedForecast']
        forecast = today['detailedForecast']
        if 'sunny' in forecast.lower():
            weather= 'sunny'
        elif 'cloudy' in forecast.lower():
            weather = 'cloudy'
        elif 'rain' in forecast.lower() or 'shower' in forecast.lower():
            weather = 'rainy'
        else:
            weather = 'nice'

        # ^Note you could just use the shortform forecast instead of casting everything with if statements
        # See shortForecast in API call. Can be called; today[shortForecast] will return one line forecast
        #--Noah

        current_time = time.localtime()
        time_str = "day" #default ..?
        if current_time.tm_hour < 12:
            time_str = "morning"
        elif current_time.tm_hour < 17:
            time_str =  "afternoon"
        else:
            time_str = "evening"

        greetings = ["What should I call you?", "What is your name?", "What do you go by?", "How should I refer to you?"]
        random_str = random.choice(greetings)
        return "Good " + time_str + "; It's " + weather + " today! " + random_str #What should I call you?"


def interviewBuddy() -> DialogueFlow:
    transitions = { #classification state
        'state': 'start',
        '#GREETING': { #return a custom greeting
            '#SET_NAME': { #user input something, save their name!
                'state':'intro',
                '`Nice to meet you` #GET_NAME `. Can you tell me a little about yourself?`' : { #first broad Q
                    '#STORE': { #STORE WHATEVER THEY SAY!!
                        '`Why do you want to join XYZ company?`': 'end'
                        }
                    }
                }
            },
            'error': {
                '`I\'m sorry, I did not get your name.`' : 'start'
            }
        }
    # transitions_classify = {
    #     'state': 'classify',
    #     '#GATE': 'cognitive',
    #     '#GATE': 'technical',
    #     '#GATE' : 'leadership',
    #     '#GATE': 'cultural',
    #     '`That\'s all I can talk about.`': {
    #         'state': 'end',
    #         'score': 0.1
    #     }
    # }
    # transitions_cultural = {
    #     'state': 'cultural',
    #     '`What type of work environment do you usually prefer?`':{
    #         '#ONT(cultural)':'end'
    #     }
    # }
    # transitions_leadership = {
    #     'state': 'leadership',
    #     '`What kinds of leadership experience do you have?`': {
    #         '#ONT(leadership)' :'end'
    #     }
    # }
    #
    # transitions_cognitive = {
    #     'state': 'cognitive',
    #     '`Tell me about a time you had to adapt or change`': {
    #         '#ONT(cognitive)' :'end'
    #     }
    # }
    # transitions_technical = {
    #     'state':'technical',
    #     '`Tell me about a past project you have worked on and are proud of`': {
    #         '$SKILLS = #ONT(technical)' : 'end'
    #     }
    # }
    global_transitions = {
        '[{leadership}]': {
            'score': 0.5,
            '``': 'leadership'
        },
        '[{programming}]': {
            'score': 0.5,
            '``': 'technical'
        }
    }

    macros = {
        'GREETING': MacroGreet(),
        'GET_NAME' : MacroNLG(get_call_name),
        'STORE': MacroStoreResponse(),
        # 'OUTPUT' : MacroOutputDialogue(),
        'SET_NAME': MacroGPTJSON(
            'How does the speaker want to be called?',
            {V.call_name.name: ["Mike", "Michael"]})
    }

    df = DialogueFlow('start', end_state='end')
    df.knowledge_base().load_json_file('cognitive_ontology.json')
    df.knowledge_base().load_json_file('cul_fit_ontology.json')
    df.knowledge_base().load_json_file('leadership_ontology.json')
    df.knowledge_base().load_json_file('tech_ontology.json')
    df.load_transitions(transitions)
    # df.load_transitions(transitions_technical)
    # df.load_transitions(transitions_cognitive)
    # df.load_transitions(transitions_classify)
    # df.load_transitions(transitions_leadership)
    # df.load_transitions(transitions_cultural)
    df.load_global_nlu(global_transitions)

    df.add_macros(macros)
    return df

def get_call_name(vars: Dict[str, Any]):
    ls = vars[V.call_name.name]
    return ls[random.randrange(len(ls))]

def save(d: List[Any]):
    fout = open('temp.txt', 'w')
    fout.write('\n'.join(d))
    # d = pickle.load(open(varfile, 'rb'))
    # df.vars().update(d)
    # df.run()
    # save(df, varfile)



# def save(df: DialogueFlow, varfile: str):
#     df.run()
#     d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
#     pickle.dump(d, open(varfile, 'wb'))


# def load(dialogue: List[Any], varfile: str):
#     d = pickle.load(open(varfile, 'rb'))
#     df.vars().update(d)
#     df.run()
#     save(df, varfile)

if __name__ == '__main__':
    interviewBuddy().run()
    save(dialogue)