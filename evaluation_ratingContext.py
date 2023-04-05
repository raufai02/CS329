import openai
PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

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

def main():
    N_job_description = """
           Responsibilities:
       * Provide technical support to customers
       * Install and train customers on systems
       * Test and quality assure products
       Requirements:
       * Bachelor of Science degree
       * Strong communication and problem solving skills
       * Willingness to travel domestically and internationally
       Desired skills:
       * Background in motion capture technology
       * Experience with Matlab, Python or Visual 3D
       * Familiarity with software such as Nexus, Unity, Unreal, etc.
       """

    print('==ISJOBCONTEXT APPROPRIATE== \n')
    print('===CASE 1=== \n')

    strong_statement = "I have experience developing scalable web applications that target usng python and visual 3d technologies like Unity and UNreal"
    response= isJobContextAppropriateTurbo(strong_statement, N_job_description)
    print(response)

    print('===CASE 2=== \n')
    icecream_statement = "I have experience working at an ice cream shop for 13 years"
    response= isJobContextAppropriateTurbo(icecream_statement, N_job_description)
    print(response)


##This shows that Davinci cannot perform for this task and should be avoided if possible
    print('===CASE 3=== \n')
    good_statement = "I have experience developing scalable web applications that target usng python and visual 3d technologies like Unity and UNreal"
    response= isJobContextAppropriateDavinci(good_statement, N_job_description)
    print(response)



if __name__ == '__main__':
    main()