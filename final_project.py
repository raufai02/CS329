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
from evaluation import MacroWhatElse, MacroSetBool
from transitions_intro import transitions_intro, transition_greetings, transitions_feeling,transitions_field, transitions_job
from transitions_intro import MacroEncourage

def load():
    with open('question_bank.json', "r") as f:
        stuff = json.load(f)
    return stuff

dialogue = [] #GLOBAL VARIABLE
categories = ['technical', 'leadership', 'culture', 'cognitive']
global_var_state = random.choice(categories)

bank = load() #key category, value dictionary with question, list pairs

PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

class V(Enum):
    call_name = 0,  # str



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
        if not vars['requirements']: #not yet covered
            strlist.append("job requirements")
        if not vars['context']:
            strlist.append("context appropriateness")
        if not vars['emotion']:
            strlist.append("emotional appropriateness")

        output = "What area would you like feedback on? " + '[' + ', '.join(strlist) + ']'

        return output


class MacroLoadScores(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        filename = "scoring/" + vars["user_name"] + '.json'
        with open(filename, 'r') as f:
            data = json.load(f) #load the scoring file into the workspace!

        vars["total_score"] = data["Total Score"]
        vars["emotion_score"] = data["Emotion Score"]
        vars["context_score"] = data["Context Score"]
        vars["requirement_score"] = data["Requirement Score"]

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
        global dialogue

        dialogue.append('U: ' + ngrams.text())
        return True
        # vars[Dialogue.DialogueList[num_threads - 1][num_questions - 1].question.name] = vars['QUESTION']


class MacroGetBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global global_var_state
        global bank
        global dialogue
        # stuff to select a question to ask
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
        dialogue.append('S: ' + question)
        return question
class MacroGetLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global dialogue

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
        'state':'intro',
            '`Let\'s start with some easy questions, OK?`': {
                '#STORE' : {
                    'state': 'big_q',
                    '#GET_BIG': {
                        '#STORE': {
                            'state': 'follow_up',
                            '#GET_LITTLE': {
                                'state': 'store_follow_up',
                                '#IF($Q_REMAIN) #STORE':'follow_up',
                                'error': {
                                    '`Let\'s move on to another topic`':'no_follow_up'
                                }
                            },
                        }
                    }
                }
            }
        }
    transitions_no_follow = {
        'state': 'no_follow_up',
        '`Thanks for chatting ` #GET_NAME': {
            '#STORE': 'start_evaluate'
        }
    }

    macros = {
        'STORE': MacroStoreResponse(),
        'SET_NAME': MacroGPTJSON(
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

        'ENCOURAGEMENT': MacroEncourage()


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
    # save(interviewBuddy(),dialogue)