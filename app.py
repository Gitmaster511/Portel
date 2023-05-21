from flask import Flask, render_template, request
import openai
from time import time, sleep

app = Flask(__name__)


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def append_file(filepath, text):
    with open(filepath, 'a', encoding='utf-8') as infile:
        return infile.write("".join(text))


def write_file(filepath, text):
    with open(filepath, 'w', encoding='utf-8') as infile:
        return infile.write(text)


write_file('prompt.txt', "You are a friend. You are helpful, friendly, kind, sympathetic, and human.\nAI: Hello, my name is Portel. How can I help you today?\nHuman: ")

openai.api_key = open_file('openaiapikey.txt').strip()


def bot(p):
    max_retry = 1
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=p,
                temperature=0.9,
                max_tokens=250,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6,
                stop=[" Human:", " AI:"]
            )
            text = response['choices'][0]['text'].strip()
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + p +
                              '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def get_sentiment(p):
    res = openai.Completion.create(
        model="text-davinci-002",
        prompt="Decide whether a Tweet's sentiment is happy, sad, angry, calm, worried, scared, neutral." +
        "\nTweet: " + f"{p}\nSentiment: ",
        temperature=0.5,
        max_tokens=250,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )
    text = res['choices'][0]['text'].strip()
    append_file('emotions.txt', text + "\n")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    conversation = open_file('prompt.txt')
    userText = request.args.get('msg')
    get_sentiment(userText)
    append_file('prompt.txt', f"{userText}\nAI: ")
    conversation = open_file('prompt.txt')
    print(conversation)
    botresponse = bot(p=conversation)
    append_file('prompt.txt', f"{botresponse}\nHuman: ")
    return str(botresponse)


if __name__ == "__main__":
    app.run(debug=True)
