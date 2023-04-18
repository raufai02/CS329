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
       # transcript = args[0]
       # job_description = self.job_description
        dict = ratecombinedScoreTurbo('\n'.join(self.transcript), self.job_description)

       #transcript_str = '\n'.join(self.transcript)

        vars["REQUIREMENT_SCORE"] = str(dict['Task 2']['Total Score'][0])

        requirement_bad_example_idx = dict['Task 1']['Worst Response']['answer_index'][0]
        vars["REQUIREMENT_EX_BAD_"] = self.transcript[requirement_bad_example_idx]

        requirement_good_example_idx = dict['Task 1']['Best Response']['answer_index'][0]
        vars["REQUIREMENT_EX_GOOD"] = self.transcript[requirement_good_example_idx]

        vars["CONTEXT_SCORE"] = str(dict['Task 4']['Unique words']['total_uniqueWords'])
        context_bad_example_idx = dict['Task 3']['Least efficient Response']['answer_index'][0]
        vars["CONTEXT_EX_BAD"] = self.transcript[context_bad_example_idx]
        context_good_example_idx = dict['Task 3']['Most efficient Response']['answer_index'][0]
        vars["CONTEXT_EX_GOOD"] = self.transcript[context_good_example_idx]

        emotion_good_idx = dict['Task 6']['Most Positive Response']['answer_index'][0]
        vars["EMOTION_EX_GOOD"] = self.transcript[emotion_good_idx]
        vars["EMOTION_SCORE"] = str(dict['Task 7']['Friendliness']['answer_friendlinessScore'][0])


        efficiency_good_idx = dict['Task 3']['Most efficient Response']['answer_index'][0]
        vars["EFFICIENCY_EX_GOOD"] = self.transcript[efficiency_good_idx]

        return True

def ratecombinedScoreTurbo(transcript, job_description):
    jsonFile = json.load(open('SampleScoring/exampleScoreFormat.json'))
    full_ex = json.dumps(jsonFile)
    #JOBS
    task_1 = "TASK1: Compare each user response with the job description. Rate each response based on the number of elements they fulfill from the job description. Only For the highest scored question and the lowest scored question, return the index of the response and provide a list of requirements they fulfilled.\n"
    task_2 = "TASK2: Compare the entire transcript with the job description. Rate each response based on the total number of elements they fulfill from the job description. Return a float value representing the number of items matched divided by the number of possible elements for the entire transcript.\n"
    #RESPONSE QUALITY
    task_3 = "TASK3: Evaluate the information density of each response. Calculate a float value rating for the efficiency of conveying information on a scale of 0 to 1 and provide the index where the answer occurred. Respond with the index of the most efficient statement and the index of the least efficient statement by the user.\n"
    task_4 = "TASK4: Evaluate the total number of unique nouns, adjectives, and adverbs used in the transcript. Calculate a float value indicating the total number of unique words divided by the total number of words. Respond with the score and the most frequent word and least frequent word from the group of nouns, adjectives, and adverbs\n"
    task_5 = "TASK5: Evaluate the response for inclusive language. Count the total number of individualistic pronouns (e.g., 'I', 'me') compared to the number of inclusive pronouns (e.g., 'we', 'us'). Calculate a float value indicating a rating for inclusivity on a scale of 0 to 1. Respond with the index of the most and least inclusive answer and a list of adjectives to describe the quality of the response.\n"
    #EMOTION
    task_6 = "TASK6: Please analyze the responses from this transcript for emotional content. Calculate  a float value rating each user's response from 0 (negative emotional content, e.g., bad, fool, hate, lose) to 1 (positive emotional content, e.g., hope, improve, kind, love). Respond with the index of the the most positive emotional response and most negative  emotional response and their scores. Also respond with a list of emotions expressed in the sentence.\n"
    task_7 = "TASK7: Please analyze the responses from this transcript for friendliness. Return a value for the overall friendliness of the text. Respond with an example of the most positive friendly sentence. Also, respond with an example of the least friendly sentence. Return the index of the emotional response.\n"


    job_listing = job_description
    prompt = "Here is a transcript of an interview conducted with a candidate applying for this Job listing:"+job_listing+"\nPlease do the following two tasks:"+task_1+task_2+task_3+task_4+task_5+task_6+task_7+"\nTHE response content be in the JSON schema shown in this example format:"+full_ex+"\n Here is the transcript:"+transcript
    model = 'gpt-3.5-turbo'
    content = prompt
    # # model = 'gpt-3.5-turbo'
    # # content = prompt
    # # # return prompt
    #
    # response = openai.ChatCompletion.create(
    #     model=model,
    #     messages=[{'role': 'user', 'content': content}]
    # )
    # printedText = response.choices[0].message.content
    # return printedText

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