import openai
import json
from json import JSONDecodeError
import utils
from utils import gpt_completion
import regexutils




PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY


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
    with open('job_descriptions.json', 'r') as f:
        data = json.load(f)

    jobs = list(data.keys())
    job = jobs[6]  # arbitrarily pick the third element from the list

    N_job_description = str(data[job])
    response = ratecombinedScoreTurbo(convo, N_job_description)


if __name__ == '__main__':
    main()