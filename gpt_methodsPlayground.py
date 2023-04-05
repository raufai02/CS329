import openai

PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY


def analyze_emotion(statement):
    prompt = "Please analyze the emotion of this statement: \n\n" + statement + "\n\n Return the emotion indicated in the statement in a single word:"
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            temperature=0.5,
            max_tokens=10,
            n=1,
            stop=None,
            timeout=10,
        )
        sentiment = response.choices[0].text.strip()
        return sentiment
    except Exception as e:
        print(f"Error: {e}")
        return False

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
    # print('==eMOtIONs== \n')
    # print('===CASE 1=== \n')
    # statement = "I am really hated my job this past summer."
    # emotion = analyze_emotion(statement)
    # print(emotion)
    #
    # print('==ISJOBCONTEXT APPROPRIATE== \n')
    # print('===CASE 1=== \n')
    #
    # strong_statement = "I have experience developing scalable web applications that target usng python and visual 3d technologies like Unity and UNreal"
    # response= isJobContextAppropriateTurbo(strong_statement, N_job_description)
    # print(response)
    #
    # print('===CASE 2=== \n')
    # icecream_statement = "I have experience working at an ice cream shop for 13 years"
    # response= isJobContextAppropriateTurbo(icecream_statement, N_job_description)
    # print(response)
    #
    # print('===CASE 3=== \n')
    # good_statement = "I have experience developing scalable web applications that target usng python and visual 3d technologies like Unity and UNreal"
    # response= isJobContextAppropriateDavinci(good_statement, N_job_description)
    # print(response)

    print('RESPONSE SCORING \n')
    print('===CASE 1=== \n')
    n_statement = "While getting my bachelors degree in computer science I gained experience developing scalable web applications using python"
    response= rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    print(response)

    print('===CASE 2=== \n')
    n_statement = "I have experience developing scalable web applications that target using python and visual 3d technologies like Unity"
    response = rateResponseOnDescriptionTurbo(n_statement, N_job_description)
    print(response)


if __name__ == '__main__':
    main()

