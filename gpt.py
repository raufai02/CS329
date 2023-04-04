import openai

PATH_API_KEY = 'resources/open_ai.txt'
openai.api_key_path = PATH_API_KEY

model = 'gpt-3.5-turbo'
content = 'Say something inspiring'
response = openai.ChatCompletion.create(
    model=model,
    messages=[{'role': 'user', 'content': content}]
)

model = 'text-davinci-edit-001'
content = 'I have lots of experience in software engineering'
response2 = openai.Edit.create(
    model=model,
    messages=[{'role': 'user', 'content': content}],
    instruction='Modify the text to make the speaker more competitive as a hiring candidate')

print(response2)


