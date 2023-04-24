from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List

question_transition = {
    'state' : 'movie_q',
    '`How do you think the name of the movie relates to its theme?`' : {
        'error' : {
            '`How do you think time and the butterfly effect is used in the movie?`' : {
                'error' : {
                    '`How do you feel about the American people being the only ones having the happy ending?`' : {
                        'error' : {
                            '`Lastly, language is just important element of the movie. Do you its more powerful to know only one language or to know all other languages?`' : {
                                'error' : {
                                    '`Thank you for taking the time to answer questions about Babel`' : 'end' # could transition back to the interview here
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


class MacroBabelBigQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global babel_q, dialogue, counter, globalCounter, globalCount, dialogue_counter
        if len(categories) != 0:

            key_list = list(babel_q.keys())
            qs = random.sample(key_list, 2)  # Big_Questions at least two
            question = random.choice(qs)
            follow_ups = [v for v in dict[question]]
            babel_q.pop(question)  # removes the big question
            vars["babel_follow_ups"] = follow_ups
            vars['stopper'] = "Go"
            counter = counter + 1
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + ' S: ' + question)
            return question
        else:
            vars['stopper'] = "Stop"
            question = "I love Babel!"
            dialogue_counter = dialogue_counter + 1
            dialogue.append(str(dialogue_counter) + ' S: ' + question)
            return question


class MacroBabelLittleQuestion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global dialogue, dialogue_counter, babel_q


        context = str(dialogue[-2] + '\n' + dialogue[-1])
        model = 'text-davinci-003'
        follow_ups = vars["babel_follow_ups"]
        follow_str = '[' + ';'.join(follow_ups) + ']'
        prompt = 'Select the most appropriate follow up question from the following list' + follow_str + ' and the following dialogue context: ' + context + 'Output ONLY the index of the best question, assuming the list starts at index 0, such as "0" or "1". '

        if len(vars["babel_follow_ups"]) == 0:

            res = 'OK. All of that is good to hear'
            dialogue.append('S: ' + res)
            return res
        else:
            idx = int(gpt_completion(prompt, model))
            try:
                res = vars["follow_ups"][idx]
            except IndexError:
                print(prompt)
                print(idx)
                res = random.choice(vars["follow_ups"])
                idx = vars["follow_ups"].index(res)

            # use random.choice on index out of bounds
            vars["follow_ups"].pop(idx)
            vars["Q_REMAIN"] = True
            vars["NO_FOLLOWUP"] = False
            dialogue.append('S: ' + res)
            return res

        return True

transitions_classify = {
    'state': 'movie_q',
    '#PERSONA': {  # insert persona macro - Ameer
        '#STORE': {
            'state': 'big_q',
            '#GET_BIG': {
                '#IF($stopper=Go) #STORE': {
                    'state': 'follow_up',
                    '#GET_LITTLE': {
                        '#STORE': {
                            '#RESPOND': 'big_q'
                        }
                    },
                },
                '#IF($stopper=Stop)': 'no_follow_up'
            }
        }
    }
}