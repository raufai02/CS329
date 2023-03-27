import openai

PATH_API_KEY = 'resources/noah_api_key.txt'
openai.api_key_path = PATH_API_KEY

model = 'gpt-3.5-turbo'
content = 'Say something inspiring'
response = openai.ChatCompletion.create(
    model=model,
    messages=[{'role': 'user', 'content': content}]
)

print(response)


