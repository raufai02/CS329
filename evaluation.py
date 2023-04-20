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
                '#GATE [inclusivity]' : 'inclusivity',
                '#GATE [efficiency]' : 'efficiency',
                '#GATE [unique words]': 'unique',
                '#GATE [job requirements]': 'requirements',
                'error': {
                    '`OK. Good job!`': 'end'
                }
            }
        },
        '[{no, nope, nah, na, all good, meh}]': {
            '`OK, no worries! Thanks for your time and good luck with your application!`': 'end'
        }
    }
}

transitions_friendliness = {
    'state' : 'friendliness',
    '#GATE #SETBOOL($friendliness, true) `Your overall friendliness score was ` $FRIENDLY_SCORE `. Would you like to see some examples?`' : {
        '[{yea, yes, sure, yeah, definitely, of course}]' : {
            '`Here is an example of a response where you demonstrated friendliness: \n ` $FRIENDLY_EX_GOOD `. You  ': 'what_else',
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
transitions_responseQuality = {
    'state': 'unique', #start w/ task 3...?
    '#RESPONSE_WHAT_ELSE '
    '#GATE  `You used ` $TOTAL_UNIQUE `unique words per word. Would you like to learn more about this score?`': {
        '[{yea, yes, sure, of course}]': {
            '`The most frequent word you used was ` $MOST_FREQUENT `. Limiting repeated use of words can help. `': 'what_else',
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


# if __name__ == '__main__':
#     evaluate().run()
#     # save(interviewBuddy(),dialogue)

