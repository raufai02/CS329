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