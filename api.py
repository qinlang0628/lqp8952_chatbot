from flask import Flask, render_template, request
from script.predict import get_response, re_encode
from flask import json

import string

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html", history=chat_history)

@app.route("/get_response", methods=['GET'])
def get_bot_response():
    input = request.args.get('msg')
    global chat_history_encoded
    message, chat_history_encoded = get_response(input, chat_history_encoded)

    # adjust the encoding for bad predictions
    if message == "":
        if len(chat_history) > 2:
            # restart conversation
            message, chat_history_encoded = get_response(input, None)
    
    elif sum([j in string.punctuation for j in message]) / len(message) > 0.5:
        chat_history_ls = [x["text"] for (i,x) in enumerate(chat_history) if i>2]
        chat_history_encoded = re_encode(chat_history_ls)
        message, chat_history_encoded = get_response(input, chat_history_encoded)

        if message == "":
            message, chat_history_encoded = get_response(input, None)

        if sum([j in string.punctuation for j in message]) / len(message) > 0.5:
            message, chat_history_encoded = get_response(input, None)
    
    # modify directly on output
    if message == "":
        message = "Umm..."

    # message = "I dont know what you are talking about"
    print("++++ chat history ++++", chat_history_encoded)
    chat_history.append({"name": "user", "text": input})
    chat_history.append({"name": "bot", "text": message})

    response = app.response_class(
        response=json.dumps(message),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/get_reset", methods=['GET', 'POST'])
def get_reset():
    print("==== reset ====")
    global chat_history
    global chat_history_encoded
    chat_history = []
    chat_history_encoded = None
    return "reset"

if __name__ == "__main__":
    global chat_history 
    global chat_history_encoded

    chat_history = []
    chat_history_encoded = None

    # app.run(debug=True, use_reloader=True)
    app.run()