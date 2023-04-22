from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
from enum import Enum

import pickle
import time
import json
import requests

import random
import openai
import os
from utils import MacroGPTJSON, MacroNLG, gpt_completion
from evaluation import transitions_unique, transitions_friendliness, transitions_inclusive, transitions_efficiency, transitions_emotion, transitions_evaluate, transitions_requirements
from transitions_intro import transitions_intro, transition_greetings, transitions_feeling,transitions_field, transitions_job
from transitions_intro import MacroEncourage
from babel_transition import question_transition
from transitions_intro import MacroVisits, get_call_name
from evaluation_combinedRating import MacroGPTEval



def saveName(df: DialogueFlow, varfile: str):
    df.run()
    d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
    pickle.dump(d, open(varfile, 'wb'))

def loadName(df: DialogueFlow, varfile: str):
        d = pickle.load(open(varfile, 'rb'))
        df.vars().update(d)
        df.run()
        save(df, varfile)

def load():
    with open('question_bank.json', "r") as f:
        stuff = json.load(f)
    with open('babel_question.json', "r") as ff:
        babels = json.load(ff)

    return stuff, babels

def loadJD():
    with open('resources/job_descriptions.json', "r") as f:
        stuff = json.load(f)
    return stuff

def loadPersonas():
    with open('resources/personas.json', "r") as f:
        stuff = json.load(f)
    return stuff

def loadComments():
    with open('resources/contextual_comments.json', "r") as f:
        stuff = json.load(f)
    return stuff

def get_call_name(vars: Dict[str, Any]):
    ls = vars[V.call_names.name]
    return ls[random.randrange(len(ls))]

dialogue = [] #GLOBAL VARIABLE
dialogue_counter = 0 #counter
personaSkills = []
categories = ['technical', 'leadership', 'culture', 'cognitive']
global_var_state = random.choice(categories)
bank, babel = load() #key category, value dictionary with question, list pairs
globalCount = {'technical':0, 'leadership':0, 'culture':0, 'cognitive':0}
globalCounter = 0
counter = 0
responseDS = loadComments()
stuff = loadJD()
job = random.choice(list(stuff.keys()))
job_description = str(stuff[job])
PATH_API_KEY = 'openai_api.txt'
openai.api_key_path = PATH_API_KEY

class V(Enum):
    call_name = 0,  # str

class MacroVisits(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        ls = vars[V.call_name.name]
        vars['name'] = ls[random.randrange(len(ls))]
        vn = vars['name']
        
        if vn not in vars:
            vars[vn] = 1
            return f'Nice to meet you, ' + vars['name'] + '!'

        else:
            count = vars[vn] + 1
            vars[vn] = count
            return f'Welcome back, ' + vars['name'] + '!'
class MacroPersona(Macro): 
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        global personaSkills
        # chosenName = random.choice(names)
        # field = vars['USER_FIELD']
        # jd = loadJD()
        # position = random.choice(list(jd.keys()))
        # words = position.split()
        # company = words[0]
        # position = ' '.join(words[1:])
        ds = loadPersonas()
        context = str(vars['USER_FIELD'] + '\n' + vars['USER_JOB'])
        # print(context)
        model = 'text-davinci-003'
        allFields = ds.keys()
        field_str = '[' + ';'.join(allFields) + ']'
        # print("All fields: ", field_str)
        prompt = 'Select the most appropriate field from the following list' + field_str + ' and the following dialogue context: ' + context + 'Output ONLY the most appropriate field from the following list' + field_str + '.'
        # print("promot: ", prompt)
        finalField = gpt_completion(prompt, model).lower()
        # print("finalField: ", finalField)
        dict = ds[finalField]
        # print("dict: ", dict)
        position = dict["position"]
        company = dict["company"]
        chosenName = dict["name"]
        personaSkills = dict['skills']
        return f"Hi there! My name is {chosenName}, I know a thing or two about {finalField}. I am working at {company} as a {position}. I will be conducting the interview with you! I want to you to know that I am on your side throughout this process, just do your best when answering the questions. So let's start!"

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
        if 'quality' not in vars:
            strlist.append("context appropriateness")
        if 'emotion' not in vars:
            strlist.append("emotional appropriateness")
        if 'inclusive' not in vars:
            strlist.append("inclusivity")
        if 'efficiency' not in vars:
            strlist.append("efficiency")
        if 'unique' not in vars:
            strlist.append('unique words')


        if len(strlist) == 0:
            output = "That's all the feedback I have for you!"
        else:
            output = "What area would you like feedback on? " + '[' + ', '.join(strlist) + ']'

        return output

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
            question = "OK. That's all I have for you today!"
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + ' S: ' + question)
            return question  
        
class MacroGetLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global dialogue, dialogue_counter

        context = str(dialogue[-2] + '\n' + dialogue[-1])
        # print(context)
        model = 'text-davinci-003'
        follow_ups = vars["follow_ups"]
        follow_str = '[' + ';'.join(follow_ups) + ']'
        prompt = 'Select the most appropriate follow up question from the following list' + follow_str + ' and the following dialogue context: ' + context + 'Output ONLY the index of the best question, assuming the list starts at index 0, such as "0" or "1". '

        if len(vars["follow_ups"]) == 0:
            vars["Q_REMAIN"] = False
            vars["NO_FOLLOWUP"] = True
            #str = 'That should be good enough to cover $CURR STATE
            res = 'OK. All of that is good to hear'
            dialogue.append('S: ' + res)
            return res
        else:
            idx = int(gpt_completion(prompt, model))
            try: 
                res = vars["follow_ups"][idx]
            except IndexError: 
                print(prompt)
                print(idx)
                res = random.choice(vars["follow_ups"])
                idx = vars["follow_ups"].index(res)
            
            #use random.choice on index out of bounds
            vars["follow_ups"].pop(idx)
            vars["Q_REMAIN"] = True
            vars["NO_FOLLOWUP"] = False
            dialogue.append('S: ' + res)
            return res

        return True

class MacroRespond(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global responseDS, dialogue, dialogue_counter

        context = str(dialogue[-2] + '\n' + dialogue[-1])
        model = 'gpt-3.5-turbo'
        prompt = 'Select the most appropriate follow up response from the following list: ' + str(responseDS) + ' and the following dialogue context: ' + context + 'Output ONLY the index of the best response, assuming the list starts at index 0, such as "0" or "1". If none of the above are appropriate responses respond with index 0 (the index of an empty string) '
        idx = gpt_completion(prompt, model)
        output = responseDS[str(idx)]
        del responseDS[str(idx)]
        return output



def interviewBuddy() -> DialogueFlow:
    global_transitions = {
    '[babel]' : {
        '`Ok, lets talk about the movie Babel. What did you think of it?`' : {
            '[{good, great, amazing, compelling, powerful, capitvating, gripping, moving, masterful, masterpiece, multilayered, poignant, authentic, impactful, cinematic, profound, bold, oscar}]' : {
                '`I\'m glad you enjoyed the movie! `' : 'movie_q' 
                },
            '[{bad, terrible, aweful, garbage, meh, ok, boring, predictable, dull, lifeless, tedious, flat, confusing, disappointing, cliche, corny, mediocre, sloppy, unoriginal}]' : {
                '`I\'m sorry to hear that it didn\'t meet your expectations.`' : 'movie_q' 
                },
            'error' : {
                '`Gotcha. Your opinion is noted`' : 'movie_q'
            }
                   
            
        } 
    }
}
    transitions_classify = { #classification state
    'state' : 'interview',
    '#PERSONA' : { # insert persona macro - Ameer
        '#STORE' : {
        'state': 'big_q',
        '#GET_BIG': {
            '#IF($stopper=Go) #STORE': {
                'state': 'follow_up',
                '#GET_LITTLE': {
                    '#STORE' : {
                        '#RESPOND' : 'big_q'
                    }
                    # 'state': 'store_follow_up',
                    # '#IF($Q_REMAIN) #STORE':'follow_up',
                    # '#IF($NO_FOLLOWUP)': 'no_follow_up'
                },
            }, 
            '#IF($stopper=Stop)': 'no_follow_up'
            }
        }
    }

    }
                
            # }
    transitions_no_follow = {
        'state': 'no_follow_up',
        '`Thanks for chatting`#GET_NAME': {
            '#STORE': 'start_evaluate'
        }
    }

    macros = {
        'STORE': MacroStoreResponse(),
        'SET_CALL_NAMES': MacroGPTJSON(
            'How does the speaker want to be called? Select the name provided by the user and return. If no name is available return Micheal',
            {V.call_name.name: ["Mike", "Michael"]}, {V.call_name.name: ["Micheal"]}),
        'GET_NAME': MacroNLG(get_call_name),
        'GET_BIG': MacroGetBigQuestion(),
        'GET_LITTLE' : MacroGetLittleQuestion(),
        'GET_CALL_NAME': MacroNLG(get_call_name),
        'GET_EXAMPLE' : MacroGetExample(),
        'WHAT_ELSE': MacroWhatElse(),
        'SETBOOL': MacroSetBool(),
        'ENCOURAGEMENT': MacroEncourage(), 
        'PERSONA' : MacroPersona(),
        'RUN_EVAL' : MacroGPTEval(dialogue, job_description),
        'NAME_SAVE' : MacroVisits(), 
        'RESPOND' : MacroRespond()
        #'RUN_EVAL' : MacroGPTEval(dummy, job_description)
    }

    df = DialogueFlow('start', end_state='end')
    df.knowledge_base().load_json_file('cognitive_ontology.json')
    df.knowledge_base().load_json_file('cul_fit_ontology.json')
    df.knowledge_base().load_json_file('leadership_ontology.json')
    df.knowledge_base().load_json_file('tech_ontology.json')
    df.knowledge_base().load_json_file('major_ontology.json')
    df.load_transitions(transitions_classify)
    df.load_transitions(transitions_no_follow)
    df.load_transitions(transitions_intro)
    df.load_transitions(transition_greetings)
    df.load_transitions(transitions_field)
    df.load_transitions(transitions_job)
    df.load_transitions(transitions_feeling)
    df.load_transitions(transitions_evaluate)
    df.load_transitions(transitions_unique)
    df.load_transitions(transitions_efficiency)
    df.load_transitions(transitions_inclusive)
    df.load_transitions(transitions_friendliness)
    df.load_transitions(transitions_requirements)
    df.load_transitions(transitions_emotion)
    df.load_global_nlu(global_transitions)
    df.load_transitions(question_transition)
    df.add_macros(macros)

    return df

def get_call_name(vars: Dict[str, Any]):
    ls = vars[V.call_name.name]
    vars['user_name']= ls[random.randrange(len(ls))]
    return vars['user_name']

def save(df: DialogueFlow, d: List[Any]): #d is the dialogue list
    df.run()
    vars = {k: v for k, v in df.vars().items() if not k.startswith('_')} #df vars (?)
    filename = vars["user_name"] + '.txt'
    fout = open(filename, 'w')
    fout.write('\n'.join(d))

if os.path.exists('test.pkl') is False:
    saveName(interviewBuddy(),'test.pkl')
loadName(interviewBuddy(),'test.pkl')

if __name__ == '__main__':
    interviewBuddy().run()
    saveName(interviewBuddy(),'test.pkl')

    # save(interviewBuddy(),dialogue)