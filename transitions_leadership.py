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
    '`Can you provide an example of when you took lead?`' : {
        '[#ONT(leadership)]': {
            '`Could you go into more detail about this experience as how you acted as a leader and the traits that made you qualified as a leader? `': 'end'
        },

        '#UNX': {
           '`Thanks for sharing`': 'end'
        }
    }
}

df = DialogueFlow('start', end_state='end')
df.knowledge_base().load_json_file('leadership_ontology.json')
df.load_transitions(transitions)

if __name__ == '__main__':
    df.run()