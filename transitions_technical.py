from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
import re

class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(?:.*)(mr|mrs|ms|dr|me|am|is|name's|by)?(?:^|\s)([a-z']+)(?:\s([a-z']+))?")
        m = r.search(ngrams.text())
        if m is None: return False

        title, firstname, lastname = None, None, None

        if m.group(1):
            title = m.group(1)
            if m.group(3):
                firstname = m.group(2).capitalize()
                lastname = m.group(3)
            else:
                firstname = m.group().capitalize()
                lastname = m.group(2)
        else:
            firstname = m.group(2).capitalize()
            lastname = m.group(3)

        vars['FIRSTNAME'] = firstname
        return True

transitions = {
    'state': 'start',
    '`Tell me about a project you are currently working on`': {
        '[#ONT(tech_role_ontology)]': {
            '`that is awesome!`': 'end'
        }, 
        '#UNX': {
            '`Thanks for sharing.`': 'end'
        },
    }
}

macros = {
    'GET_NAME': MacroGetName()
}

df = DialogueFlow('start', end_state='end')
df.knowledge_base().load_json_file('ontology.json')
df.load_transitions(transitions)
df.add_macros(macros)

if __name__ == '__main__':
    df.run()


