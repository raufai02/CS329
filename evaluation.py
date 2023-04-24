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
            '#WHAT_ELSE': {
                '[friendliness]': 'friendliness',
                '[{emotion, emotional content}]': 'emotion',
                '[inclusivity]': 'inclusive',
                '[efficiency]': 'efficiency',
                '[unique words]': 'unique',
                '[job requirements]': 'requirements',
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
    '#GATE #SETBOOL($friendliness, true) `Your overall friendliness score was ` $FRIENDLY_SCORE `. Would you like to see some examples?`': {
        '[{yea, yes, sure, yeah, definitely, of course}]': {
            '`Here is an example of a response where you demonstrated friendliness: \n ` $FRIENDLY_EX_GOOD `. Do you want to see another example? \n`': {
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
    '#GATE `Let\'s look at some examples where you succeeded and struggled with emotional content. OK?`#SETBOOL($emotion, true)': {
        '[{yea, yes, sure, yeah, definitely, of course, ok}]': {
            '`Here is an example of a response where you were ` $EMOTION_EX_GOOD_ADJ `: \n ` $EMOTION_EX_GOOD `\n We gave you a score of ` $EMOTION_EX_GOOD_SCORE `. \n Would you like to see another example?\n`': {
                '[{yea, yes, sure, yeah, definitely, of course}]': {
                    '`Here was an example where you were ` $EMOTION_EX_BAD_ADJ ` and could have done better: \n ` $EMOTION_EX_BAD `\n We gave you a score of ` $EMOTION_EX_BAD_SCORE `\n` ': 'what_else'
                }
            }
        },
        '[{no, nah, nope, pass, naw}]': {
          '`OK. Never-mind then!`':'what_else'
        },
        'error': 'emotion'
    },
    'error': {
        '`I am sorry. I don\'t have anymore emotion feedback for you!`': 'what_else'
    }
}

transitions_efficiency = {
    'state': 'efficiency',
    '#GATE `Let\'s look at your highest and lowest lexical density examples, OK?`': {
        'error': {
            '`Your most efficient response had a score of ` $LEXICAL_GOOD `, and an efficiency score of ` $EFFICIENCY_GOOD `. \n` $EFFICIENT_EX_GOOD `. \n Would you like to see another example?`': {
                'error': {
                    '`Your least efficient response had a score of `$LEXICAL_BAD `, and an efficiency score of ` $EFFICIENCY_BAD `. \n ` $EFFICIENT_EX_BAD' : 'what_else'
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
            '`Here is an example of a response where you demonstrated job requirements: \n` $REQUIREMENT_EX_GOOD `. \n Would you like to see another example? \n `': {
                '[{yea, yes, sure, of course}]': {
                    '`In this response you could have done better in showing that you meet job requirements: \n \t` $REQUIREMENT_EX_BAD `\n`': 'what_else'
                },
                '[{no, nah, nope, naw}]':'what_else'
            }
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore requirements feedback for you!`': 'what_else'
    }
}


transitions_inclusive = {
    'state' : 'inclusive',
    '#GATE `Your total inclusivity score was ` $INCLUSIVE_SCORE `. Would you like to learn more?`#SETBOOL($inclusive, true)': {
        '[{yea, yes, sure, of course}]': {
            '`Here is an example of a good response where you were very ` $INCLUSIVE_GOOD_ADJECTIVE `. \n` $INCLUSIVE_EX_GOOD `\n Your score for this response was ` $INCLUSIVE_GOOD_SCORE `. Do you want to see another example? \n`': {
                'error': {
                    '`Here is an example of a weak response where you were  ` $INCLUSIVE_BAD_ADJECTIVE `. \n` $INCLUSIVE_EX_BAD `\n Your score for this response was ` $INCLUSIVE_BAD_SCORE `. \n`' : 'what_else'
                }
            }
        },
        '[{no, nah, naw, nope, meh}]' : 'what_else',
        'error': 'inclusive'
    }
}
