import openai
import json
PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

def rateResponseOnDescriptionTurbo(transcript, job_description):
    jsonFile = json.load(open('SampleScoring/exampleJobScoreFormat.json'))
    full_ex = json.dumps(jsonFile)
    task_1 = "TASK1: Compare each user response with the job description. Rate each response based on the number of elements they fulfill from the job description. Only For the highest scored question and the lowest scored question, return the index of the response and provide a brief explanation for the score."
    task_2 = "TASK2: Compare the entire transcript with the job description. Rate each response based on the total number of elements they fulfill from the job description. Return a float value representing the number of items matched divided by the number of possible elements for the entire transcript."
    job_listing = job_description
    prompt = "Here is a transcript of an interview conducted with a candidate applying for this Job listing:"+job_listing+"\nPlease do the following two tasks:"+task_1+task_2+"\nONLY respond in the JSON schema such this example output format:"+full_ex+"\n Here is the transcript:"+transcript
    model = 'gpt-3.5-turbo'
    content = prompt
    # return prompt

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{'role': 'user', 'content': content}]
    )
    printedText = response.choices[0].message.content
    return printedText

def main():
    with open('SampleConvos/sampleFormattedConvo.txt', 'r') as l:
        convo = l.read()
    with open('job_descriptions.json', 'r') as f:
        data = json.load(f)

    jobs = list(data.keys())
    job = jobs[6] #arbitrarily pick the third element from the list

    N_job_description = str(data[job])

    response = rateResponseOnDescriptionTurbo(convo, N_job_description)
    print(response+'\n')

    # print('RESPONSE SCORING \n')
    # print('===CASE 1=== \n')
    # n_statement = "While getting my bachelors degree in computer science I gained experience developing scalable web applications using python"
    # response= rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    # print(response+'\n')
    #
    # print('===CASE 2=== \n')
    # n_statement = "I have experience developing scalable web applications that target using python and visual 3d technologies like Unity"
    # response = rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    # print(response+'\n')


if __name__ == '__main__':
    main()

#
# class MacroGPTJSON(Macro):
#     def __init__(self, request: str, full_ex: Dict[str, Any], empty_ex: Dict[str, Any] = None, set_variables: Callable[[Dict[str, Any], Dict[str, Any]], None] = None):
#         """
#         :param request: the task to be requested regarding the user input (e.g., How does the speaker want to be called?).
#         :param full_ex: the example output where all values are filled (e.g., {"call_names": ["Mike", "Michael"]}).
#         :param empty_ex: the example output where all collections are empty (e.g., {"call_names": []}).
#         :param set_variables: it is a function that takes the STDM variable dictionary and the JSON output dictionary and sets necessary variables.
#         """
#         self.request = request
#         self.full_ex = json.dumps(full_ex)
#         self.empty_ex = '' if empty_ex is None else json.dumps(empty_ex)
#         self.check = re.compile(regexutils.generate(full_ex))
#         self.set_variables = set_variables
#
#     def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
#         examples = f'{self.full_ex} or {self.empty_ex} if unavailable' if self.empty_ex else self.full_ex
#         prompt = f'{self.request} Respond in the JSON schema such as {examples}: {ngrams.raw_text().strip()}'
#         output = gpt_completion(prompt)
#         if not output: return False
#
#         try:
#             d = json.loads(output)
#         except JSONDecodeError:
#             print(f'Invalid: {output}')
#             return False
#
#         if self.set_variables:
#             self.set_variables(vars, d)
#         else:
#             vars.update(d)
#
#         return True
