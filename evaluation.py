
class MacroWhatElse(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        strlist = []
        if not vars['requirements']: #not yet covered
            strlist.append("job requirements")
        if not vars['context']:
            strlist.append("context appropriateness")
        if not vars['emotion']:
            strlist.append("emotional appropriateness")

        output = "What area would you like feedback on? " + '[' + ', '.join(strlist) + ']'

        return output

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
        'state' : 'start_evaluate',
        '`Thank you for your time. Congratulations on completing the interview! Would you like to receive feedback?`' : {
            '[{yea, ya, yes, i would, of course, sure, definitely}]' : {
                'state': 'what_else',
                '`Perfect!` #WHAT_ELSE': {
                    '#GATE [emotion]': 'emotion',
                    '#GATE [context]' : 'context',
                    '#GATE [requirements]': 'context',
                    'error': 'what_else'
                }
            },
            '[{no, nope, nah, na, I\'m good, meh}]' : {
                '`OK, no worries! Thanks for your time and good luck with your application!`': 'end'
            }
        }
}

transitions_emotion = {
    'state': 'emotion',
    '#GATE #SETBOOL($emotion, true) `Your raw emotion score was ` #EMOTION_SCORE `. Would you like to learn more about this score?`' : {
        '[context]': 'context',
        '[requirements]' : 'requirements',
        '[{yea, yes, sure, of course}]': {
            '#EMOTION_EXAMPLE' : 'what_else',
        },
        '[{no, nah, nope}]' : 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore emotion feedback for you!`' : 'what_else'
    }
}

transitions_context = {
    'state' : 'context',
    '#GATE #SETBOOL($context, true) `Your raw contextual appropriateness score was ` #CONTEXT_SCORE `. Would you like to learn more about this score?`': {
        '[{yea, yes, sure, of course}]' : {
            '#CONTEXT_EXAMPLE' : 'what_else',
        },
        '[{no, nah, nope}]' : 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore context feedback for you!`': 'what_else'
    }

}

transitions_requirements = {
    'state': 'requirements',
    '#GATE #SETBOOL($requirements, true) `Your raw score for meeting job requirements was ` #CONTEXT_SCORE `. Would you like to learn more about this score?`': {
        '[{yea, yes, sure, of course}]': {
            '#REQUIREMENT_EXAMPLE': 'what_else',
        },
        '[{no, nah, nope}]': 'what_else'
    },
    'error': {
        '`I am sorry. I don\'t have anymore emotion feedback for you!`' : 'what_else'
    }
}

