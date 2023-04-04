from emora_stdm import DialogueFlow, Macro, Ngrams
import re
from typing import Dict, Any, List

import time
import json
import requests

import random
import openai

class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(mr|mrs|ms|dr|my name is|call me|i have the name|i was given the name|i'm|i am|i prefer|i prefer you call me|i go by|it's|its|)?(?:^|\s)([a-z']+)(?:\s([a-z']+))?")
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
        vars['LASTNAME'] = lastname.capitalize()


class MacroRandomName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):

        names = ['Liam', 'Emma', 'Noah', 'Olivia', 'William', 'Ava', 'James', 'Isabella', 'Oliver', 'Sophia', 'Benjamin', 'Charlotte', 'Elijah', 'Mia', 'Lucas', 'Amelia', 'Mason', 'Harper', 'Logan', 'Evelyn', 'Alexander', 'Abigail', 'Ethan', 'Emily', 'Jacob', 'Elizabeth', 'Michael', 'Mila', 'Daniel', 'Ella', 'Henry', 'Avery', 'Jackson', 'Sofia', 'Sebastian', 'Camila', 'Aiden', 'Scarlett', 'Matthew', 'Victoria', 'Samuel', 'Madison', 'David', 'Luna', 'Joseph', 'Chloe', 'Carter', 'Grace', 'Owen', 'Penelope', 'Wyatt', 'Lily', 'John', 'Hannah', 'Jack', 'Layla', 'Luke', 'Nora', 'Jayden', 'Zoe', 'Dylan', 'Stella', 'Levi', 'Hazel', 'Gabriel', 'Ellie', 'Anthony', 'Natalie', 'Isaac', 'Aria', 'Grayson', 'Audrey', 'Christopher', 'Lila', 'Joshua', 'Violet', 'Andrew', 'Claire', 'Lincoln', 'Savannah', 'Mateo', 'Alice', 'Ryan', 'Nora', 'Jaxon', 'Bella', 'Nicholas', 'Lucy', 'Leo', 'Anna', 'Adam', 'Ruby', 'Xavier', 'Madeline', 'Eli', 'Paisley', 'Nathan', 'Elena', 'Landon', 'Gabriella', 'Ian', 'Sarah', 'Ezra', 'Madelyn', 'Jordan', 'Skylar', 'Aaron', 'Caroline', 'Connor', 'Kaylee', 'Charlotte', 'Eleanor', 'Hunter', 'Samantha', 'Caleb', 'Julia', 'Cameron', 'Genesis', 'Adrian', 'Valentina', 'Colton', 'Ruby', 'Evelyn', 'Katherine', 'Luis', 'Sadie', 'Austin', 'Autumn', 'Alexa', 'Nevaeh', 'Cooper', 'Gianna', 'Easton', 'Arianna', 'Isaiah', 'Aaliyah', 'Charles', 'Gabrielle', 'Josiah', 'Piper', 'Christian', 'Annabelle', 'Jeremiah', 'Maria', 'Anthony', 'Delilah', 'Jaxson', 'Aurora', 'Miles', 'Adeline', 'Elias', 'Emilia', 'Eric', 'Isabelle', 'Braxton', 'Ivy', 'Everett', 'Liliana', 'Caden', 'Josephine', 'Axel']
        vars['interviewer_name'] = random.choice(names)
        return vars['interviewer_name']


transitions = {
    'state' : 'start',
    '`Hello, my name is`#INTERVIEWER`.` `What should I call you?`' : { # can make macros for differnet ways to greet and ask names to make more conversational
        '[#GET_NAME]' : {
            '`Nice to meet you,` $FIRSTNAME `! How are you feeling right now?`' : {
                '[good]' : {
                        '`That\'s awesome! I\'m glad you\'re feeling well! You\'re a young college student\graduate, correct?`' : {
                            '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                '`Gotcha. What is your major, if you don\'t mind me asking?`' : {
                                    '$MAJOR=#ONT(major)' : {
                                        '`That\'s interesting. I\'ve always found` $MAJOR to be compelling. What kind of software developer do want to be when you apply for jobs?' : {
                                            '$USER_JOB=#ONT(JOB)' : { # need to make this
                                                '`And what field of software engineering/computer science are you interesting in? `' : {
                                                    '$USER_FIELD=#ONT(FIELD)`' : { # need to make this
                                                        '`So you\'re into` $USER_JOB `and` $USER_FIELD `? That\'s awesome. What an interesting conversation. Anyways, we should probably get into the interview. Are you feeling nervous or confident?`' : {
                                                            '[nervous]' : {
                                                                '#ENCOURAGEMENT `Are you ready now?`' : {
                                                                    '[yes]' : {
                                                                        '`Then, let\'s begin.`' : 'end'
                                                                    },
                                                                    '[no]' : {
                                                                        '`Well, you\'re gonna have to be ready because we need to begin now`' : 'end'
                                                                    }
                                                                } 
                                                            },
                                                            '[confident]' : {
                                                                '`That\'s great. Now, let\'s begin`' : 'end'
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        } 
                                    }
                            } 
                            },
                            '[{no, nah, negative, incorrect, not correct, false, nope, nada}]' : {
                            '`You\'re not? Oh, my bad. I got you confused with someone else. I\'m looking for a computer science student in undergrad/grad. If you find someone like that, tell them I\'m looking for them`' : 'start' 
                            },
                    }
                },

                
                    
                '[bad]'  : {
                        '`Aw, man that sucks. Hope you\'re able to feel better soon though! Also, you\'re a young college student\graduate, correct?`' : {
                            '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                '`Gotcha. What is your major, if you don\'t mind me asking?`' : {
                                    '$MAJOR=#ONT(major)' : {
                                        '`That\'s interesting. I\'ve always found` $MAJOR to be compelling. What kind of software developer do want to be when you apply for jobs?' : {
                                            '$USER_JOB=#ONT(JOB)' : { # need to make this
                                                '`And what field of software engineering/computer science are you interesting in? `' : {
                                                    '$USER_FIELD=#ONT(FIELD)`' : { # need to make this
                                                        '`So you\'re into` $USER_JOB `and` $USER_FIELD `? That\'s awesome. What an interesting conversation. Anyways, we should probably get into the interview. Are you feeling nervous or confident?`' : {
                                                            '[nervous]' : {
                                                                '#ENCOURAGEMENT `Are you ready now?`' : {
                                                                    '[yes]' : {
                                                                        '`Then, let\'s begin.`' : 'end'
                                                                    },
                                                                    '[no]' : {
                                                                        '`Well, you\'re gonna have to be ready because we need to begin now`' : 'end'
                                                                    }
                                                                } 
                                                            },
                                                            '[confident]' : {
                                                                '`That\'s great. Now, let\'s begin`' : 'end'
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        } 
                                    }
                            } 
                            },
                            '[{no, nah, negative, incorrect, not correct, false, nope, nada}]' : {
                            '`You\'re not? Oh, my bad. I got you confused with someone else. I\'m looking for a computer science student in undergrad/grad. If you find someone like that, tell them I\'m looking for them`' : 'start' 
                            },
                    }  
                },

                'error' : {},

            }  # can do something for response prompt as comment above. Also maybe more efficient way to get name ?
        }
    } 

}
macros = {
 'INTERVIEWER' : MacroRandomName(),
 'GET_NAME' : MacroGetName()

}

df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions)
df.add_macros(macros)

if __name__ == '__main__':
    df.run()
