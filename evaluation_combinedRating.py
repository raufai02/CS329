import openai
import json
from json import JSONDecodeError
import utils
from utils import gpt_completion
import regexutils

from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
from enum import Enum




PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY




class MacroGPTEval(Macro):
    def __init__(self, transcript: List[str], job_description: str):
        self.transcript = transcript
        self.job_description = job_description

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):

        dict = ratecombinedScoreTurbo('\n'.join(self.transcript), self.job_description)

        # REQUIREMENTS ********
        requirement_bad_example_idx = dict['Task 1']['Worst Response']['answer_index'][0]
        vars["REQUIREMENT_EX_BAD"] = self.transcript[requirement_bad_example_idx] if self.transcript[
            requirement_bad_example_idx] else "REQUIREMENT_EX_BAD"

        requirement_good_example_idx = dict['Task 1']['Best Response']['answer_index'][0]
        vars["REQUIREMENT_EX_GOOD"] = self.transcript[requirement_good_example_idx] if self.transcript[
            requirement_good_example_idx] else "REQUIREMENT_EX_GOOD"

        vars["REQUIREMENT_SCORE"] = str(dict['Task 2']['Total Score'][0]) if 'Total Score' in dict[
            'Task 2'] else "REQUIREMENT_SCORE"

        # RESPONSE QUALITY
        # TASK3
        efficient_bad_example_idx = dict['Task 3']['least efficient response']['answer_index'][0]
        vars["EFFICIENT_EX_BAD"] = self.transcript[efficient_bad_example_idx] if self.transcript[
            efficient_bad_example_idx] else "EFFICIENT_EX_BAD"
        vars["LEXICAL_BAD"] = str(
            dict['Task 3']['least efficient response']['lexical_density'][0]) if 'lexical_density' in \
                                                                                 dict['Task 3'][
                                                                                     'least efficient response'] else "LEXICAL_BAD"
        vars["EFFICIENCY_BAD"] = str(
            dict['Task 3']['least efficient response']['answer_efficiencyScore'][0]) if 'answer_efficiencyScore' in \
                                                                                        dict['Task 3'][
                                                                                            'least efficient response'] else "EFFICIENCY_BAD"

        efficient_good_example_idx = dict['Task 3']['most efficient response']['answer_index'][0]
        vars["EFFICIENT_EX_GOOD"] = self.transcript[efficient_good_example_idx] if self.transcript[
            efficient_good_example_idx] else "EFFICIENT_EX_GOOD"
        vars["LEXICAL_GOOD"] = str(
            dict['Task 3']['most efficient response']['lexical_density'][0]) if 'lexical_density' in dict['Task 3'][
            'most efficient response'] else "LEXICAL_GOOD"
        vars["EFFICIENCY_GOOD"] = str(
            dict['Task 3']['most efficient response']['answer_efficiencyScore'][0]) if 'answer_efficiencyScore' in \
                                                                                       dict['Task 3'][
                                                                                           'most efficient response'] else "EFFICIENCY_GOOD"

        # TASK 4
        vars["TOTAL_UNIQUE"] = str(dict['Task 4']['Unique words']['total_uniqueWords'][0]) if 'total_uniqueWords' in \
                                                                                              dict['Task 4'][
                                                                                                  'Unique words'] else "TOTAL_UNIQUE"
        # these next two are supposed to be lists, not single words. but we will just extract a single word for now...
        vars["MOST_FREQUENT"] = str(dict['Task 4']['Unique words']['most_frequent'][0]) if 'most_frequent' in \
                                                                                           dict['Task 4'][
                                                                                               'Unique words'] else "MOST_FREQUENT"
        vars["LEAST_FREQUENT"] = str(dict['Task 4']['Unique words']['least_frequent'][0]) if 'least_frequent' in \
                                                                                             dict['Task 4'][
                                                                                                 'Unique words'] else "LEAST_FREQUENT"

            #TASK 5
        vars["INCLUSIVE_SCORE"] = str(dict['Task 5']['Inclusive Language']['inclusive_score'][0])
        idx = dict['Task 5']['Most Inclusive Answer']['answer_index'][0]

        if self.transcript[idx]:
            vars["INCLUSIVE_EX_GOOD"] = self.transcript[idx]
        else:
            vars["INCLUSIVE_EX_GOOD"] = "None"

        if dict['Task 5']['Most Inclusive Answer']['response_adjectives']:
            vars["INCLUSIVE_GOOD_ADJECTIVE"] = dict['Task 5']['Most Inclusive Answer']['response_adjectives'][0]
        else:
            vars["INCLUSIVE_GOOD_ADJECTIVE"] = "None"

        if dict['Task 5']['Most Inclusive Answer']['inclusive_score']:
            vars["INCLUSIVE_GOOD_SCORE"] = str(dict['Task 5']['Most Inclusive Answer']['inclusive_score'][0])
        else:
            vars["INCLUSIVE_GOOD_SCORE"] = "None"

        idx = dict['Task 5']['Least Inclusive Answer']['answer_index'][0]

        if self.transcript[idx]:
            vars["INCLUSIVE_EX_BAD"] = self.transcript[idx]
        else:
            vars["INCLUSIVE_EX_BAD"] = "None"

        adjectives = dict['Task 5']['Least Inclusive Answer']['response_adjectives']

        if adjectives:
            vars["INCLUSIVE_BAD_ADJECTIVE"] = adjectives[0]
        else:
            vars["INCLUSIVE_BAD_ADJECTIVE"] = "None"

        if dict['Task 5']['Least Inclusive Answer']['inclusive_score']:
            vars["INCLUSIVE_BAD_SCORE"] = str(dict['Task 5']['Least Inclusive Answer']['inclusive_score'][0])
        else:
            vars["INCLUSIVE_BAD_SCORE"] = "None"

        emotion_good_idx = dict['Task 6']['Most Positive Response']['answer_index'][0]

        if self.transcript[emotion_good_idx]:
            vars["EMOTION_EX_GOOD"] = self.transcript[emotion_good_idx]
        else:
            vars["EMOTION_EX_GOOD"] = "None"

        if dict['Task 6']['Most Positive Response']['descriptors']:
            vars["EMOTION_EX_GOOD_ADJ"] = dict['Task 6']['Most Positive Response']['descriptors'][0]
        else:
            vars["EMOTION_EX_GOOD_ADJ"] = "None"

        if dict['Task 6']['Most Positive Response']['answer_emotionScore']:
            vars["EMOTION_EX_GOOD_SCORE"] = str(dict['Task 6']['Most Positive Response']['answer_emotionScore'][0])
        else:
            vars["EMOTION_EX_GOOD_SCORE"] = "None"

        idx = dict['Task 6']['Most Negative Response']['answer_index'][0]

        if self.transcript[idx]:
            vars["EMOTION_EX_BAD"] = self.transcript[idx]
        else:
            vars["EMOTION_EX_BAD"] = "None"

        if dict['Task 6']['Most Negative Response']['descriptors']:
            vars["EMOTION_EX_BAD_ADJ"] = dict['Task 6']['Most Negative Response']['descriptors'][0]
        else:
            vars["EMOTION_EX_BAD_ADJ"] = "None"

        if dict['Task 6']['Most Negative Response']['answer_emotionScore']:
            vars["EMOTION_EX_BAD_SCORE"] = str(dict['Task 6']['Most Negative Response']['answer_emotionScore'][0])
        else:
            vars["EMOTION_EX_BAD_SCORE"] = "None"
        # assign to vars[] only if the fields are not empty, and to "None" otherwise
        vars["FRIENDLY_SCORE"] = str(dict['Task 7']['Friendliness'][0]) if 'Task 7' in dict and 'Friendliness' in dict[
            'Task 7'] else "None"

        idx = dict['Task 7']['Most Friendly Response']['answer_index'][
            0] if 'Task 7' in dict and 'Most Friendly Response' in dict['Task 7'] else None
        vars["FRIENDLY_EX_GOOD"] = self.transcript[idx] if idx is not None else "None"
        vars["FRIENDLY_EX_GOOD_SCORE"] = str(dict['Task 7']['Most Friendly Response']['answer_friendlinessScore'][
                                                 0]) if 'Task 7' in dict and 'Most Friendly Response' in dict[
            'Task 7'] else "None"

        idx = dict['Task 7']['Least Friendly Response']['answer_index'][
            0] if 'Task 7' in dict and 'Least Friendly Response' in dict['Task 7'] else None
        vars["FRIENDLY_EX_BAD"] = self.transcript[idx] if idx is not None else "None"
        vars["FRIENDLY_EX_BAD_SCORE"] = str(dict['Task 7']['Least Friendly Response']['answer_friendlinessScore'][
                                                0]) if 'Task 7' in dict and 'Least Friendly Response' in dict[
            'Task 7'] else "None"


        return True

def ratecombinedScoreTurbo(transcript, job_description):
    jsonFile = json.load(open('SampleScoring/exampleScoreFormat.json'))
    full_ex = json.dumps(jsonFile)
    #JOBS
    task_1 = "TASK1: Compare each user response with the job description. Rate each response based on the number of elements they fulfill from the job description. Only for the highest scored question and the lowest scored question, return the index of the response and provide a list of requirements they fulfilled.\n"
    task_2 = "TASK2: Compare the entire transcript with the job description. Rate each response based on the total number of elements they fulfill from the job description. Return a float value representing the number of items matched divided by the number of possible elements for the entire transcript.\n"
    #RESPONSE QUALITY
    task_3 = "TASK3: Evaluate the information density of each response. Calculate a float value rating for the efficiency of conveying information on a scale of 0 to 1 and provide the index where the answer occurred. Respond with the index of the most efficient statement and the index of the least efficient statement by the user. Also calculate the lexical density of the response\n"
    task_4 = "TASK4: Evaluate the total number of unique nouns, adjectives, and adverbs used in the transcript. Calculate a float value indicating the total number of unique words divided by the total number of words. Respond with the score and the most frequent word and least frequent word from the group of nouns, adjectives, and adverbs\n"
    task_5 = "TASK5: Evaluate the response for inclusive language. Count the total number of individualistic pronouns (e.g., 'I', 'me') compared to the number of inclusive pronouns (e.g., 'we', 'us'). Calculate a float value indicating a rating for inclusivity on a scale of 0 to 1. Respond with the index of the most and least inclusive answer and a list of adjectives to describe the quality of the response.\n"
    #EMOTION
    task_6 = "TASK6: Please analyze the responses from this transcript for emotional content. Calculate  a float value rating each user's response from 0 (negative emotional content, e.g., bad, fool, hate, lose) to 1 (positive emotional content, e.g., hope, improve, kind, love). Respond with the index of the the most positive emotional response and most negative  emotional response and their scores. Also respond with a list of emotions expressed in the sentence.\n"
    task_7 = "TASK7: Please analyze the responses from this transcript for friendliness. Return a value for the overall friendliness of the text from 0(not friendly) to 1 (friendly). Respond with an example of the most positive friendly sentence. Also, respond with an example of the least friendly sentence. Return the index and a score of the friendly responses.\n"


    job_listing = job_description
    prompt = "Here is a transcript of an interview conducted with a candidate applying for this Job listing:"+job_listing+"\nPlease do the following two tasks:"+task_1+task_2+task_3+task_4+task_5+task_6+task_7+"\nTHE response content be in the JSON schema shown in this example format:"+full_ex+"\n Here is the transcript:"+transcript + "Only evaluate the user responses, which are the responses that start with 'U:'. The other responses are from the dialogue system and are only for context."
    model = 'gpt-3.5-turbo'
    content = prompt


    output = gpt_completion(prompt, model)

    if not output: return False

    try:
        d = json.loads(output)
    except JSONDecodeError:
        print(f'Invalid: {output}')
        return False

    return d


def main():
    with open('SampleConvos/sampleFormattedConvo.txt', 'r') as l:
        convo = l.read()
    with open('resources/job_descriptions.json', 'r') as f:
        data = json.load(f)

    jobs = list(data.keys())
    job = jobs[6]  # arbitrarily pick the third element from the list

    N_job_description = str(data[job])
    response = ratecombinedScoreTurbo(convo, N_job_description)

    print(convo)
    print(response)


if __name__ == '__main__':
    main()