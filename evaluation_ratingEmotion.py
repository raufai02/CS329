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


def main():
    print('==eMOtIONs== \n')
    print('===CASE 1=== \n')
    statement = "I am really hated my job this past summer."
    emotion = analyze_emotion(statement)
    print(emotion)

if __name__ == '__main__':
    main()