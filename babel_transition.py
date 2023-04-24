from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
import random
from enum import Enum
import random
import openai

import json
from utils import MacroGPTJSON, MacroNLG, gpt_completion

PATH_API_KEY = 'openai_api.txt'
openai.api_key_path = PATH_API_KEY

def load():
    with open('babel_question.json', "r") as ff:
        babels = json.load(ff)

    return babels

dialogue = [] #GLOBAL VARIABLE
dialogue_counter = 0 #counter
babel_q = load() #key category, value dictionary with question, list pairs
counter = 0

class MacroBabelBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global babel_q, dialogue, counter, dialogue_counter
        if counter < 4: #arbitrary limit on big question ... ?
            key_list = list(babel_q.keys())
            qs = random.sample(key_list, 2)  # Big_Questions at least two
            question = random.choice(qs)
            follow_ups = [v for v in babel_q[question]]
            babel_q.pop(question)  # removes the big question
            vars["babel_follow_ups"] = follow_ups
            vars['b_stopper'] = "Go"
            counter = counter + 1
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + 'S: ' + question)
            return question
        else:
            vars['b_stopper'] = "Stop"
            question = "I love Babel!"
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + 'S: ' + question)
            return question


class MacroBabelLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global dialogue, dialogue_counter, babel_q
        try:
            context = str(dialogue[-2] + '\n' + dialogue[-1])
        except IndexError:
            print(dialogue)
            context = '\n'.join(dialogue)

        model = 'text-davinci-003'
        follow_ups = vars["babel_follow_ups"]
        try:
            follow_str = '[' + ';'.join(follow_ups) + ']'
        except TypeError:
            print(follow_ups)
        prompt = 'Select the most appropriate follow up question about the movie Babel (2006),from the following list' + follow_str + ' and the following dialogue context: ' + context + 'Output ONLY the index of the best question, assuming the list starts at index 0, such as "0" or "1". '

        if len(vars["babel_follow_ups"]) == 0:
            res = 'Very thoughtful of you!'
            dialogue.append('S: ' + res)
            return res
        else:
            idx = int(gpt_completion(prompt, model))
            try:
                res = vars["babel_follow_ups"][idx]
            except IndexError:
                print(prompt)
                print(idx)
                res = random.choice(vars["babel_follow_ups"])
                idx = vars["babel_follow_ups"].index(res)

            vars["babel_follow_ups"].pop(idx)
            dialogue.append('S: ' + res)
            return res

        return True

class MacroStoreSystem(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):

        global dialogue, dialogue_counter
        dialogue_counter = dialogue_counter + 1
        dialogue.append(str(dialogue_counter) + ' S: ' + str(args[0]))

        return str(args[0])
transitions_babel = {
    'state': 'movie_q',
    '#STORE_SYSTEM(`Ok, lets talk about the movie Babel (2006). How did you like the film?`)': {  # insert persona macro - Ameer
        '#STORE': {
            'state': 'babel_big_q',
            '#GET_BABEL_BIG': {
                '#IF($b_stopper=Go) #STORE': {
                    'state': 'babel_follow_up',
                    '#GET_BABEL_LITTLE': {
                        '#STORE': {
                            '#RESPOND': 'babel_big_q'
                        }
                    },
                },
                '#IF($b_stopper=Stop)': {
                    '`Thanks for chatting`#GET_NAME': {
                        '#STORE': 'start_evaluate'
                    }
                }
            }
        }
    }
}