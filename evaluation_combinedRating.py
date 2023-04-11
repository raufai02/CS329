import openai
import json
from json import JSONDecodeError
import utils
from utils import gpt_completion
import regexutils




PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

class MacroGPTEval(Macro):
    def __init__(self, transcript: List[Any], job_description: str, set_variables: Callable[[Dict[str, Any], Dict[str, Any]], None] = None):
        # self.request = request
        # self.full_ex = json.dumps(full_ex)
        # self.empty_ex = '' if empty_ex is None else json.dumps(empty_ex)

        self.transcript = transcript
        self.job_description = job_description
        self.set_variables = set_variables

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):

        transcript = self.transcript
        job_description = self.job_description
        dict = ratecombinedScoreTurbo(transcript, job_description)

        vars["REQUIREMENT_SCORE"] = str(dict['Task 2']['Total Score'][0])

        requirement_bad_example_idx = dict['Task 1']['Worst Response']['answer index'][0]

        vars["REQUIREMENT_EX_BAD_"] = transcript[requirement_bad_example_idx]

        requirement_good_example_idx = dict['Task 1']['Best Response']['answer_index'][0]
        vars["REQUIREMENT_EX_GOOD"] = transcript[requirement_good_example_idx]

        vars["CONTEXT_SCORE"] = str(dict['Task 4']['Total Score'][0])

        requirement_bad_example_idx = dict['Task 1']['Worst Response']['answer index'][0]

        vars["REQUIREMENT_EX_BAD"] = transcript[requirement_bad_example_idx]

        requirement_good_example_idx = dict['Task 1']['Best Response']['answer_index'][0]
        vars["REQUIREMENT_EX_GOOD"] = transcript[requirement_good_example_idx]


        efficiency_good_idx = dict['Task 3']['Most efficient Response']['answer_index'][0]
        vars["EFFICIENCY_EX_GOOD"] = transcript[efficiency_good_idx]


        # examples = f'{self.full_ex} or {self.empty_ex} if unavailable' if self.empty_ex else self.full_ex
        # prompt = f'{self.request} Respond in the JSON schema such as {examples}: {ngrams.raw_text().strip()}'
        # output = gpt_completion(prompt)
        # if not output: return False
        #
        # try:
        #     d = json.loads(output)
        # except JSONDecodeError:
        #     print(f'Invalid: {output}')
        #     return False
        #
        # if self.set_variables:
        #     self.set_variables(vars, d)
        # else:
        #     vars.update(d)

        return True

def ratecombinedScoreTurbo(transcript, job_description):
    jsonFile = json.load(open('SampleScoring/exampleScoreFormat.json'))
    full_ex = json.dumps(jsonFile)
    #JOBS
    task_1 = "TASK1: Compare each user response with the job description. Rate each response based on the number of elements they fulfill from the job description. Only For the highest scored question and the lowest scored question, return the index of the response and provide a brief explanation for the score explaining what elements from the job description they fullfilled.\n"
    task_2 = "TASK2: Compare the entire transcript with the job description. Rate each response based on the total number of elements they fulfill from the job description. Return a float value representing the number of items matched divided by the number of possible elements for the entire transcript.\n"
    #RESPONSE QUALITY
    task_3 = "TASK3: Evaluate the information density of each response. Calculate a float value rating for the efficiency of conveying information on a scale of 0 to 1 and provide the index where the answer occurred. Respond with the index of the most efficient statement and the index of the least efficient statment by the user. Respond with an explanation as to why these are efficient or inefficient.\n"
    task_4 = "TASK4: Evaluate the total number of unique nouns, adjectives, and adverbs used in the transcript. Calculate a float value indicating the total number of unique words divided by the total number of words. Respond with the score and the most frequent word and least frequent word from the group of nouns, adjectives, and adverbs\n"
    task_5 = "TASK5: Evaluate the response for inclusive language. Count the total number of individualistic pronouns (e.g., 'I', 'me') compared to the number of inclusive pronouns (e.g., 'we', 'us'). Calculate a float value indicating a rating for inclusivity on a scale of 0 to 1. Respond with the index of the most and least inclusive answer and an explanation as to why.\n"
    #EMOTION
    task_6 = "TASK6: Please analyze the responses from this transcript for emotional content. Calculate  a float value rating each user's response from 0 (negative emotional content, e.g., bad, fool, hate, lose) to 1 (positive emotional content, e.g., hope, improve, kind, love). Respond with the index of the the most positive emotional response and most negative  emotional response and their scores. Also respond with a string indicating an explanation describing the emotions expressed in the sentence.\n"
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

    output = gpt_completion(prompt)

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
    print(response)


if __name__ == '__main__':
    main()