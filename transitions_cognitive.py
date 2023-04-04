from emora_stdm import DialogueFlow, Macro, Ngrams
import re
from typing import Dict, Any, List

import time
import json
import requests

import random
import openai

transitions = {
    'state' : 'start',
    '`Tell me about a time you had to change`' : {
        '[#ONT(cognitive)]': {
            'SITUATION': 'end'
        },

        '#UNX': {
           '`Thanks for sharing`': 'end'
        }
    }
}


df = DialogueFlow('start', end_state='end')
df.knowledge_base().load_json_file('cognitive_ontology.json')
df.load_transitions(transitions)

if __name__ == '__main__':
    df.run()