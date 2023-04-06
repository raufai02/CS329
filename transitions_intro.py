from emora_stdm import DialogueFlow, Macro, Ngrams
import re
from typing import Dict, Any, List

import time
import json
import requests
from enum import Enum
import random
import openai
from utils import MacroGPTJSON
from utils import MacroNLG

PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY


def get_call_name(vars: Dict[str, Any]):
    ls = vars[V.call_names.name]
    return ls[random.randrange(len(ls))]

class V(Enum):
    call_names = 0,  
    office_location = 1
    office_hours = 2 


class MacroEncourage(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        encouragement = ["You got this! Just be confident and show them why you're the best fit for the job.",    "Take a deep breath and remember all the hard work you've put in to get here. You deserve to be in that interview room.",    "Don't worry about being perfect. Just be yourself and let your personality shine through. That's what will make you stand out.",    "It's natural to feel nervous, but try to channel that energy into excitement. You have a great opportunity in front of you!",    "Believe in yourself and your abilities. You wouldn't have been called in for an interview if you weren't a strong candidate.",    "Remember that the interviewer is rooting for you too. They want to find the right person for the job, and that could very well be you.",    "Don't be afraid to ask questions or ask for clarification if you need it. That shows that you're engaged and interested in the role.",    "You're prepared and qualified for this interview. Now it's just a matter of showing them why you're the best fit. You've got this!"]
        return random.choice(encouragement)


class MacroRandomName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):

        names = ['Liam', 'Emma', 'Noah', 'Olivia', 'William', 'Ava', 'James', 'Isabella', 'Oliver', 'Sophia', 'Benjamin', 'Charlotte', 'Elijah', 'Mia', 'Lucas', 'Amelia', 'Mason', 'Harper', 'Logan', 'Evelyn', 'Alexander', 'Abigail', 'Ethan', 'Emily', 'Jacob', 'Elizabeth', 'Michael', 'Mila', 'Daniel', 'Ella', 'Henry', 'Avery', 'Jackson', 'Sofia', 'Sebastian', 'Camila', 'Aiden', 'Scarlett', 'Matthew', 'Victoria', 'Samuel', 'Madison', 'David', 'Luna', 'Joseph', 'Chloe', 'Carter', 'Grace', 'Owen', 'Penelope', 'Wyatt', 'Lily', 'John', 'Hannah', 'Jack', 'Layla', 'Luke', 'Nora', 'Jayden', 'Zoe', 'Dylan', 'Stella', 'Levi', 'Hazel', 'Gabriel', 'Ellie', 'Anthony', 'Natalie', 'Isaac', 'Aria', 'Grayson', 'Audrey', 'Christopher', 'Lila', 'Joshua', 'Violet', 'Andrew', 'Claire', 'Lincoln', 'Savannah', 'Mateo', 'Alice', 'Ryan', 'Nora', 'Jaxon', 'Bella', 'Nicholas', 'Lucy', 'Leo', 'Anna', 'Adam', 'Ruby', 'Xavier', 'Madeline', 'Eli', 'Paisley', 'Nathan', 'Elena', 'Landon', 'Gabriella', 'Ian', 'Sarah', 'Ezra', 'Madelyn', 'Jordan', 'Skylar', 'Aaron', 'Caroline', 'Connor', 'Kaylee', 'Charlotte', 'Eleanor', 'Hunter', 'Samantha', 'Caleb', 'Julia', 'Cameron', 'Genesis', 'Adrian', 'Valentina', 'Colton', 'Ruby', 'Evelyn', 'Katherine', 'Luis', 'Sadie', 'Austin', 'Autumn', 'Alexa', 'Nevaeh', 'Cooper', 'Gianna', 'Easton', 'Arianna', 'Isaiah', 'Aaliyah', 'Charles', 'Gabrielle', 'Josiah', 'Piper', 'Christian', 'Annabelle', 'Jeremiah', 'Maria', 'Anthony', 'Delilah', 'Jaxson', 'Aurora', 'Miles', 'Adeline', 'Elias', 'Emilia', 'Eric', 'Isabelle', 'Braxton', 'Ivy', 'Everett', 'Liliana', 'Caden', 'Josephine', 'Axel']
        vars['interviewer_name'] = random.choice(names)
        return vars['interviewer_name']


transitions_intro = {
    'state' : 'start',
    '`Hello, my name is`#INTERVIEWER`. You\'re here for the interview today, right? What should I call you?`' : { # can make macros for differnet ways to greet and ask names to make more conversational
        '#SET_CALL_NAMES': {
            'state': 'get_feeling',
            '`Nice to meet you,` #GET_CALL_NAME `! How are you feeling right now?`' : {
                '[{good, well, great, fine, splendid, awesome, wonderful, terrfic, superb, nice, not bad, fantastic, amazing, alright, all right, better, best}]' : {
                        'state': 'check_year',
                        '`That\'s awesome! I\'m glad you\'re feeling well! You\'re a young college student\graduate, correct?`' : {
                            '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                '`Gotcha. What is your major, if you don\'t mind me asking?`' : {
                                    '[$MAJOR=#ONT(major)]' : { # expressions dont work for some reason ? # UPDATE: now also crashes ?
                                        '`That\'s interesting. I\'ve always found` $MAJOR `to be compelling. What kind of software developer do want to be when you apply for jobs?`' : {
                                            '[{$USER_JOB=#ONT(job), $USER_JOB=#ONT(field)}]' : { #add logic to also match the field ontology if no job match
                                                '`And what field of software engineering/computer science are you interesting in? `' : {
                                                    '[$USER_FIELD=#ONT(field)]' : { # crashes here. not sure why ?
                                                        '`So you want to be` $USER_JOB `and` $USER_FIELD `? That\'s awesome. What an interesting combination. Anyways, we should probably get into the interview. Are you feeling nervous or confident?`' : {
                                                            '[nervous]' : {
                                                                '#ENCOURAGEMENT `Are you ready now?`' : {
                                                                    '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                                                        '`Then, let\'s begin.`' : 'end'
                                                                    },
                                                                    '[{no, nah, negative, incorrect, not correct, false, nope, nada}]' : {
                                                                        '`Well, you\'re gonna have to be ready because we need to begin now`' : 'end'
                                                                    }
                                                                } 
                                                            },
                                                            '[confident]' : {
                                                                '`That\'s great. Now, let\'s begin`' : 'end'
                                                            },
                                                            'error' : {
                                                                '`....`': 'end'
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
                            '`You\'re not? Oh, my bad. I got you confused with someone else. I\'m looking for a computer science student in undergrad/grad. If you find someone like that, tell them I\'m looking for them`' : 'end' 
                            },
                            'error' : {
                                '`Sorry, I don\'t understand. Please try again.`' : 'end'
                            }
                    }
                },

                
                    
                '[{bad, terrible, aweful, not great, sucks, meh, could be better, rough, tough, not my day, down, worse, worst}]'  : { #replace with transition to check_year state
                        '`Aw, man that sucks. Hope you\'re able to feel better soon though! Also, you\'re a young college student\graduate, correct?`' : {
                            '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                '`Gotcha. What is your major, if you don\'t mind me asking?`' : {
                                    '[$MAJOR=#ONT(major)]' : {
                                        '`That\'s interesting. I\'ve always found` $MAJOR `to be compelling. What kind of software developer do want to be when you apply for jobs?`' : {
                                            '[$USER_JOB=#ONT(job)]' : {
                                                '`And what field of software engineering/computer science are you interesting in? `' : {
                                                    '[$USER_FIELD=#ONT(field)]' : { # need to make this
                                                        '`So you\'re into` $USER_JOB `and` $USER_FIELD `? That\'s awesome. What an interesting combination. Anyways, we should probably get into the interview. Are you feeling nervous or confident?`' : {
                                                            '[nervous]' : {
                                                                '#ENCOURAGEMENT `Are you ready now?`' : {
                                                                    '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                                                        '`Then, let\'s begin.`' : 'end'
                                                                    },
                                                                    '[{no, nah, negative, incorrect, not correct, false, nope, nada, uh uh}]' : {
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
                            'error' : {
                                '`Sorry, I don\'t understand. Please try again.`' : 'end'
                            }
                    }  
                },

                'error' : {
                        '`Gotcha. Thank you for sharing! Also, you\'re a young college student\graduate, correct?`' : {
                            '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                '`Gotcha. What is your major, if you don\'t mind me asking?`' : {
                                    '[$MAJOR=#ONT(major)]' : {
                                        '`That\'s interesting. I\'ve always found` $MAJOR `to be compelling. What kind of software developer do want to be when you apply for jobs?`' : {
                                            '[$USER_JOB=#ONT(job)]' : {
                                                '`And what field of software engineering/computer science are you interesting in? `' : {
                                                    '[$USER_FIELD=#ONT(field)]' : { # crashes
                                                        '`So you\'re into` $USER_JOB `and` $USER_FIELD `? That\'s awesome. What an interesting combination. Anyways, we should probably get into the interview. Are you feeling nervous or confident?`' : {
                                                            '[nervous]' : {
                                                                '#ENCOURAGEMENT `Are you ready now?`' : {
                                                                    '[{yes, yeah, yea, ye, yeye, correct, indeed, affirmative, absolutely,bet,roger, yup, definitely, uh huh, yep}]' : {
                                                                        '`Then, let\'s begin.`' : 'end'
                                                                    },
                                                                    '[{no, nah, negative, incorrect, not correct, false, nope, nada, uh uh}]' : {
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
                            'error' : {
                                '`Sorry, I don\'t understand. Please try again.`' : 'end'
                            }
                    }  
                },

            }  # can do something for response prompt as comment above.
        }
    } 

}
macros = {
 'GET_CALL_NAME': MacroNLG(get_call_name),
 'INTERVIEWER' : MacroRandomName(),
 'SET_CALL_NAMES': MacroGPTJSON(
        'How does the speaker want to be called?',
        {V.call_names.name: ["Mike", "Michael"]}),

 'ENCOURAGEMENT' : MacroEncourage()

}


df = DialogueFlow('start', end_state='end')
df.load_transitions(transitions_intro)
df.knowledge_base().load_json_file('major_ontology.json')
df.add_macros(macros)

if __name__ == '__main__':
    df.run()
