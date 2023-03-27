import openai

PATH_API_KEY = 'resources/noah_api_key.txt'
openai.api_key_path = PATH_API_KEY


def analyze_sentiment(statement):
    prompt = "Please analyze the sentiment of this statement: \n\n" + statement + "\n\nSentiment:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=1,
        n=1,
        stop=None,
        timeout=10,
    )
    sentiment = response.choices[0].text.strip()
    return sentiment

def is_interview_appropriate(statement):
    prompt = "Is the following response appropriate for a job interview?\n\n" + statement + "\n\nYes or no:"
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

def main():
    # statement = "I had a really bad day today"
    # result = analyze_sentiment(statement)
    # print(result)
    # statement = "I am very good at interviwing for jobs"
    # result = analyze_sentiment(statement)
    # print(result)


    context = "John is applying for a software engineering job at Google"
    statement = "I have experience developing scalable web applications using Java and Spring"
    result = is_interview_appropriate(statement)
    print(result)  # should theoretically print True
#     SHOULD RETURN True

    statement = "I dont like apple pie, but I would eat it if I worked here"
    result = is_interview_appropriate(statement)
    print(result)  # should theoretically print False
#     SHOULD RETURN False

if __name__ == '__main__':
    main()