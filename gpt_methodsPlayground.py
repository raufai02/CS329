import openai
import json
PATH_API_KEY = 'openai_api.txt'
openai.api_key_path = PATH_API_KEY
from utils import MacroGPTJSON, MacroNLG, gpt_completion
def contextual_comments():
    with open('resources/contextual_comments.json', "r") as f:
        stuff = json.load(f)
    return stuff


def responder():
        contextualComments = contextual_comments()
        # contextualComments = '[' + ','.join(contextualComments) + ']'
        print(contextualComments['6'])
        context = "S: How do you think working on a team in a virtual environment differs from working on a team in an in-person environment, and how would that impact your productivity?U: I think that working virtually makes you less productive because you dont get to collaborate"

        model = 'gpt-3.5-turbo'
        prompt = 'Pick a follow up response from the following list of possible follow-ups: ' + str(contextualComments) + ' given the conversation has the following context: ' + context + ' Output ONLY the index of the best question, assuming the list starts at index 0, such as "0" or "1".'
        idx =  gpt_completion(prompt, model)
        response = contextualComments[str(idx)]
        #
        return response


def is_interview_appropriate(statement):
    prompt = "Is the following response appropriate for this job interview?\n\n" + statement + "\n\nYes or no:"
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.5,
            n=1,
            stop=None,
            timeout=10,
        )
        classification = response.choices[0].text.strip()
        return classification
    except Exception as e:
        print(f"Error: {e}")
        return False

def isJobContextAppropriateDavinci(statement, job_description):
    job_description = job_description
    prompt = job_description+"Is the following response appropriate for this job interview?\n\n" + statement + "\n\n Return {Yes or no} and a one sentence reason why not"
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=100,
            temperature=0.5,
            n=1,
            stop=None,
            timeout=10,
        )
        classification = response.choices[0].text.strip()
        return classification
        # if classification.lower() == 'yes':
        #     # Check if the candidate's response matches the job description
        #     if any(word in statement.lower() for word in job_description.lower().split()):
        #         return "Yes, the candidate's response is appropriate for this job interview."
        #     else:
        #         return "No, the candidate's response is not relevant to the job description."
        # elif classification.lower() == 'no':
        #     return "No, the candidate's response is not appropriate for this job interview."
        # else:
        #     return "Invalid response. Please respond with 'yes' or 'no'."
    except Exception as e:
        print(f"Error: {e}")
        return False


def isJobContextAppropriateTurbo(job_description, statement):
    model = 'gpt-3.5-turbo'
    content = job_description+"Is the following response appropriate for this job interview?\n\n" + statement + "\n\nReturn {Yes or no} and a one sentence reason why not"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'user', 'content': content}]
    )

    printedText = response.choices[0].message.content
    return printedText

def rateResponseOnDescriptionTurbo(job_description, statement):
    model = 'gpt-3.5-turbo'
    content = job_description+"Rate the following response for the number of items it fulfills from the job description? Be sure to note if they have any qualifications or certfications.\n\n" + statement + "\n\nReturn a numerical response followed by a bulleted list. Here is an example of the response: {Score:2,  List: - The response fulfills the requirement of having a Bachelor of Science degree.,The response mentions experience with Python"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'user', 'content': content}]
    )

    printedText = response.choices[0].message.content
    return printedText

def main():

    # print('===CASE 2=== \n')
    # n_statement = "I have experience developing scalable web applications that target using python and visual 3d technologies like Unity"
    # response = rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    # print(response)
    response = responder()
    print(response)


if __name__ == '__main__':
    main()

