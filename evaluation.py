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
                '#GATE [emotional appropriateness]': 'emotion',
                '#GATE [context appropriateness]': 'context',
                '#GATE [job requirements]': 'context',
                'error': 'what_else'
            }
        },
        '[{no, nope, nah, na, all good, meh}]': {
            '`OK, no worries! Thanks for your time and good luck with your application!`': 'end'
        }
    }
}
transitions_emotion = {
    'state': 'emotion',
    '#GATE #SETBOOL($emotion, true) `Your raw emotion score was ` $EMOTION_SCORE `. Would you like to learn more about this score?`': {
        '[context]': 'context',
        '[requirements]': 'requirements',
        '[{yea, yes, sure, of course}]': {
            '$EMOTION_EXAMPLE': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore emotion feedback for you!`': 'what_else'
    }
}
transitions_context = {
    'state': 'context',
    '#GATE #SETBOOL($context, true) `Your raw contextual appropriateness score was ` $CONTEXT_SCORE `. Would you like to learn more about this score?`': {
        '[{yea, yes, sure, of course}]': {
            '$CONTEXT_EXAMPLE': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore context feedback for you!`': 'what_else'
    }

}
transitions_requirements = {
    'state': 'requirements',
    '#GATE #SETBOOL($requirements, true) `Your raw score for meeting job requirements was ` $REQUIREMENT_SCORE `. Would you like to learn more about this score?`': {
        '[{yea, yes, sure, of course}]': {
            '$REQUIREMENT_EXAMPLE': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore emotion feedback for you!`': 'what_else'
    }
}


# if __name__ == '__main__':
#     evaluate().run()
#     # save(interviewBuddy(),dialogue)

