import openai
import json
PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

def rateResponseQualityTurbo(transcript, job_description):
    jsonFile = json.load(open('SampleScoring/exampleQualityScoreFormat.json'))
    full_ex = json.dumps(jsonFile)
    task_1 = "TASK1: Evaluate the information density of each response. Calculate a float value rating for the efficiency of conveying information on a scale of 0 to 1 and provide the index where the answer occurred. Respond with the index of the most efficient statement and the index of the least efficient statment by the user. Respond with an explanation as to why these are efficient or inefficient."
    task_2 = "TASK2: Evaluate the total number of unique nouns, adjectives, and adverbs used in the transcript. Calculate a float value indicating the total number of unique words divided by the total number of words. Respond with the score and the most frequent word and least frequent word from the group of nouns, adjectives, and adverbs"
    task_3 = "TASK3: Evaluate the response for inclusive language. Count the total number of individualistic pronouns (e.g., 'I', 'me') compared to the number of inclusive pronouns (e.g., 'we', 'us'). Calculate a float value indicating a rating for inclusivity on a scale of 0 to 1. Respond with the index of the most and least inclusive answer and an explanation as to why."
    job_listing = job_description
    prompt = "Here is a transcript of an interview conducted with a candidate applying for this Job listing:"+job_listing+"\nPlease do the following two tasks:"+task_1+task_2+task_3+"\nONLY respond in the JSON schema such this example output format:"+full_ex+"\n Here is the transcript:"+transcript
    model = 'gpt-3.5-turbo'
    content = prompt
    # return prompt

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'user', 'content': content}]
    )
    printedText = response.choices[0].message.content
    return printedText

def isJobContextAppropriateTurbo(job_description, statement):
    model = 'gpt-3.5-turbo'
    content = job_description+"Is the following response appropriate for this job interview?\n\n" + statement + "\n\nReturn {Yes or no} and a one sentence reason why not"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'user', 'content': content}]
    )

    printedText = response.choices[0].message.content
    return printedText

def main():
#     N_job_description = """
#            Responsibilities:
#        * Provide technical support to customers
#        * Install and train customers on systems
#        * Test and quality assure products
#        Requirements:
#        * Bachelor of Science degree
#        * Strong communication and problem solving skills
#        * Willingness to travel domestically and internationally
#        Desired skills:
#        * Background in motion capture technology
#        * Experience with Matlab, Python or Visual 3D
#        * Familiarity with software such as Nexus, Unity, Unreal, etc.
#        """
#
#     print('==ISJOBCONTEXT APPROPRIATE== \n')
#     print('===CASE 1=== \n')
#
#     strong_statement = "I have experience developing scalable web applications that target usng python and visual 3d technologies like Unity and UNreal"
#     response= isJobContextAppropriateTurbo(strong_statement, N_job_description)
#     print(response)
#
#     print('===CASE 2=== \n')
#     icecream_statement = "I have experience working at an ice cream shop for 13 years"
#     response= isJobContextAppropriateTurbo(icecream_statement, N_job_description)
#     print(response)
#
#
# ##This shows that Davinci cannot perform for this task and should be avoided if possible
#     print('===CASE 3=== \n')
#     good_statement = "I have experience developing scalable web applications that target usng python and visual 3d technologies like Unity and UNreal"
#     response= isJobContextAppropriateDavinci(good_statement, N_job_description)
#     print(response)
    with open('SampleConvos/sampleFormattedConvo.txt', 'r') as l:
        convo = l.read()
    with open('job_descriptions.json', 'r') as f:
        data = json.load(f)

    jobs = list(data.keys())
    job = jobs[6]  # arbitrarily pick the third element from the list

    N_job_description = str(data[job])
    response = rateResponseQualityTurbo(convo, N_job_description)
    print(response)


if __name__ == '__main__':
    main()