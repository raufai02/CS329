from emora_stdm import DialogueFlow, Macro, Ngrams
import re
from typing import Dict, Any, List

import time
import json
import requests

import random
import openai

import utils
from utils import MacroGPTJSON, MacroNLG

class MacroCallGPT(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        PATH_API_KEY = 'resources/openai_api.txt'
        openai.api_key_path = PATH_API_KEY

        model = 'gpt-3.5-turbo'
        content = 'Say something inspiring'
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )

        return response["choices"]["message"]["content"]


class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(mr|mrs|ms|dr)?(?:^|\s)([a-z']+)(?:\s([a-z']+))?")
        m = r.search(ngrams.text())
        if m is None: return False

        title, firstname, lastname = None, None, None

        if m.group(1):
            title = m.group(1)
            if m.group(3):
                firstname = m.group(2)
                lastname = m.group(3)
            else:
                firstname = m.group()
                lastname = m.group(2)
        else:
            firstname = m.group(2)
            lastname = m.group(3)

        vars['TITLE'] = title
        vars['FIRSTNAME'] = firstname
        vars['LASTNAME'] = lastname

        return True

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
        '#GREETING': { #return a custom greeting based on time and weather!
            '#GET_NAME': { #user input something, save their name!
                'state':'classify',
                '`Nice to meet you ` $FIRSTNAME `. Can you tell me a little about yourself?`' : { #first broad Q
                    '#GET_PERSONAL_INFO': {
                        '`Why do you want to join XYZ company?`': {
                            '#WHY_COMPANY': 'classify' #get information about why this company!
                        }
                    }
                }
            },
            'error': {
                '`I\'m sorry, I did not get your name.`' : 'start'
            }
        }
    }
    transitions_classify = {
        'state': 'classify',
        '#GATE `Cognitive Question Prompt` ': 'cognitive',
        '#GATE `Technical Question Prompt`': 'technical',
        '#GATE `Leadership Question Prompt`' : 'leadership',
        '#GATE `Cultural Question Prompt`': 'cultural',
        '`That\'s all I can talk about.`': {
            'state': 'end',
            'score': 0.1
        }
    }
    transitions_cultural = {
        'state': 'cultural',
        '`What type of work environment do you usually prefer?`':{
            '#ONT(cultural)':'end'

        }
    }
    transitions_leadership = {
        'state': 'leadership',
        '`What kinds of leadership experience do you have?`':'end'
    }

    transitions_cognitive = {
        'state': 'cognitive',
        '`Tell me about a time you had to adapt or change`': {
            '#ONT(cognitive)' :'end'
        }
    }
    transitions_technical = {
        'state':'technical',
        '`Tell me about a past project you have worked on and are proud of`': {
            '$SKILLS = #ONT(technical)' : 'end'
        }
    }
    global_transitions = {
        '[{leadership}]': {
            'score': 0.5,
            '``': 'leadership'
        },
        '[{programming}]': {
            'score': 0.5,
            '`Oh, I can recommend you a movie!`': 'technical'
        }
    }

    macros = {
        'GREETING': MacroGreet(),
        'GET_NAME' : MacroGetName()
    }

    df = DialogueFlow('start', end_state='end')
    df.knowledge_base().load_json_file('cognitive_ontology.json')
    df.knowledge_base().load_json_file('cul_fit_ontology.json')
    df.knowledge_base().load_json_file('leadership_ontology.json')
    df.knowledge_base().load_json_file('tech_ontology.json')
    df.load_transitions(transitions)
    df.load_transitions(transitions_technical)
    df.load_transitions(transitions_cognitive)
    df.load_transitions(transitions_classify)
    df.load_transitions(transitions_leadership)
    df.load_transitions(transitions_cultural)
    df.load_global_nlu(global_transitions)

    df.add_macros(macros)
    return df

if __name__ == '__main__':
    interviewBuddy().run()