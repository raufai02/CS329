import openai
import json
PATH_API_KEY = 'resources/open_ai.txt'
openai.api_key_path = PATH_API_KEY

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

    with open('job_descriptions.json', 'r') as f:
        data = json.load(f)

    jobs = list(data.keys())
    job = jobs[2] #arbitrarily pick the third element from the list

    N_job_description = str(data[job])

    # Write the updated dictionary back to the JSON file!
    # with open('resources/previous.json', 'w') as f:
    #     json.dump(data, f)
    # N_job_description = """
    #        Responsibilities:
    #    * Provide technical support to customers
    #    * Install and train customers on systems
    #    * Test and quality assure products
    #    Requirements:
    #    * Bachelor of Science degree
    #    * Strong communication and problem solving skills
    #    * Willingness to travel domestically and internationally
    #    Desired skills:
    #    * Background in motion capture technology
    #    * Experience with Matlab, Python or Visual 3D
    #    * Familiarity with software such as Nexus, Unity, Unreal, etc.
    #    """

    print('RESPONSE SCORING \n')
    print('===CASE 1=== \n')
    n_statement = "While getting my bachelors degree in computer science I gained experience developing scalable web applications using python"
    response= rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    print(response+'\n')

    print('===CASE 2=== \n')
    n_statement = "I have experience developing scalable web applications that target using python and visual 3d technologies like Unity"
    response = rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    print(response+'\n')


if __name__ == '__main__':
    main()