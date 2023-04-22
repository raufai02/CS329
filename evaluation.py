from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List

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




transitions_evaluate = {
    'state': 'start_evaluate',
    '`Congratulations on completing the interview! Would you like to receive feedback?`': {
        '[{yea, ya, yes, i would, of course, sure, definitely}] #RUN_EVAL': {
            'state': 'what_else',
            '`Perfect!` #WHAT_ELSE': {
                '#GATE [friendliness]': 'friendliness',
                '#GATE [emotion]' : 'emotion',
                '#GATE [inclusivity]': 'inclusive',
                '#GATE [efficiency]': 'efficiency',
                '#GATE [unique words]': 'unique',
                '#GATE [job requirements]': 'requirements',
                'error': {
                    '`OK. Good job!`': 'end'
                }
            }
        },
        '[{no, nope, nah, na, all good, meh}]': {
            '`OK, no worries! Thanks for your time and good luck with your applications!`': 'end'
        }
    }
}

transitions_friendliness = {
    'state' : 'friendliness',
    '#GATE #SETBOOL($friendliness, true) `Your overall friendliness score was ` $FRIENDLY_SCORE `. Would you like to see some examples?`' : {
        '[{yea, yes, sure, yeah, definitely, of course}]': {
            '`Here is an example of a response where you demonstrated friendliness: \n ` $FRIENDLY_EX_GOOD `. Do you want to see another example?': {
                '[{yea, yes, sure, yeah, definitely, of course}]': {
                    '`In this example, you could have been more friendly! \n ` $FRIENDLY_EX_BAD': 'what_else',
                },
                '[{no, nah, nope}]' : 'what_else'

            }
        }

    }
}
transitions_emotion = {
    'state': 'emotion',
    '#GATE #SETBOOL($emotion, true) `Your raw emotion score was ` $EMOTION_SCORE `. Would you like to learn more about this score?`': {
        '[context]': 'context',
        '[requirements]': 'requirements',
        '[{yea, yes, sure, yeah, definitely, of course}]': {
            '`Here is an example of a response where you expressed positive emotional content: \n `$EMOTION_EX_GOOD': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else',
        'error': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore emotion feedback for you!`': 'what_else'
    }
}

transitions_efficiency = {
    'state': 'efficiency',
    '#GATE `Let\'s look at your highest and lowest lexical density examples, OK?`': {
        'error': {
            '`Your most efficient response had a score of ` $LEXICAL_GOOD `, and an efficiency score of ` $EFFIENCY_GOOD `. \n` $EFFICIENCY_EX_GOOD' : {
                'error': {
                    '`Your least efficient response had a score of `$LEXICAL_BAD `, and an efficiency score of ` $EFFICIENCY_BAD `. \n ` $EFFICIENCY_EX_BAD' : 'what_else'
                }
            }
        }
    }

}
transitions_unique = {
    'state': 'unique',
    '#GATE`You used ` $TOTAL_UNIQUE `unique words per word. Would you like to learn more about this score?` #SETBOOL($unique, true)': {
        '[{yea, yes, sure, of course}]': {
            '`The most frequent word you used was ` $MOST_FREQUENT `. Limiting repeated use of words can help. The word you used least frequently was ` $LEAST_FREQUENT': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '#SETBOOL($quality, true) `I am sorry. I don\'t have anymore response quality feedback for you!`': 'what_else'
    }

}
transitions_requirements = {
    'state': 'requirements',
    '#GATE #SETBOOL($requirements, true) `Your raw score for meeting job requirements was ` $REQUIREMENT_SCORE `. Would you like to learn more about this score?`': {
        '[{yea, yes, sure, of course}]': {
            '`Here is an example of a response where you demonstrated job requirements: \n `$REQUIREMENT_EX_GOOD': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore requirements feedback for you!`': 'what_else'
    }
}


transitions_inclusive = {
    'state' : 'inclusive',
    '#GATE #SETBOOL($inclusive, true) `Your total inclusivity score was ` $INCLUSIVE_SCORE `. Would you like to learn more?': {
        '[{yea, yes, sure, of course}]': {
            '`Here is an example of a good response where you were very ` $INCLUSIVE_GOOD_ADJECTIVE `. \n` $INCLUSIVE_EX_GOOD `\n Your score for this response was ` $INCLUSIVE_GOOD_SCORE `. `': {
                'error': {
                    '`Here is an example of a weak response where you were  ` $INCLUSIVE_BAD_ADJECTIVE `. \n` $INCLUSIVE_EX_BAD `\n Your score for this response was ` $INCLUSIVE_BAD_SCORE `. `' : 'what_else'
                }
            }
        },
        '[{no, nah, naw, nope, meh}]' : 'what_else',
        'error' : 'inclusive'
    }
}
