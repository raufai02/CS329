import openai
import json
PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY


def rateEmotionTurbo(transcript, job_description):
    jsonFile = json.load(open('SampleScoring/exampleEmotionScoreFormat.json'))
    full_ex = json.dumps(jsonFile)
    task_1 = "TASK1: Please analyze the responses from this transcript for emotional content. Calculate  a float value rating each user's response from 0 (negative emotional content, e.g., bad, fool, hate, lose) to 1 (positive emotional content, e.g., hope, improve, kind, love). Respond with the index of the the most positive emotional response and most negative  emotional response and their scores. Also respond with a string indicating an explanation describing the emotions expressed in the sentence."
    task_2 = "TASK2: Please analyze the responses from this transcript for friendliness. Return a value for the overall friendliness of the text. Respond with an example of the most positive friendly sentence. Also, respond with an example of the least friendly sentence. Return the index of the emotional response."
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


def main():
    print('==eMOtIONs== \n')
    print('===CASE 1=== \n')

    with open('SampleConvos/sampleFormattedConvo.txt', 'r') as l:
        convo = l.read()
    with open('resources/job_descriptions.json', 'r') as f:
        data = json.load(f)

    jobs = list(data.keys())
    job = jobs[6]  # arbitrarily pick the third element from the list

    N_job_description = str(data[job])

    emotion = rateEmotionTurbo(convo, N_job_description)
    print(emotion)

if __name__ == '__main__':
    main()