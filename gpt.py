import openai

PATH_API_KEY = 'resources/openai_api.txt'
openai.api_key_path = PATH_API_KEY

model = 'gpt-3.5-turbo'
content = 'Say something inspiring'
response = openai.ChatCompletion.create(
    model=model,
    messages=[{'role': 'user', 'content': content}]
)

printedText = response.choices[0].message.content


print(printedText)


