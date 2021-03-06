# Chatbot

Chatbot is a fine-tuned dialogue generation model from [DialoGPT (small)](https://huggingface.co/transformers/model_doc/dialogpt.html)

## Installation

Under the main directory, run the following command to install the required package in requirements.txt

```bash
pip3 install -r requirements.txt
```

Download the trained model in this [Google Drive Link](https://drive.google.com/drive/folders/1k_PawTC_hLQ0RFwuzSTxs16VfBdkriTY?usp=sharing), unzip and put the models under ```/model``` directory. Change the model used in the ```/script/predict.py``` to adjust to the model you use.

## API
To test the REST API, run the following command in the main directory

```bash
python3 api.py
```

The run the following command in python, replace the ```host``` variable to your host address, and ```message``` variable to the input text you want to test.

```python
import requests
message = "hi"
host = ""
url = "http://{}/get_response?msg={}".format(host, message)
response = requests.get(url)
print(response.json())
```

## Web App
To access the webapp, run the following command in the main directory

```bash
python3 api.py
```
Copy and paste the web url into your browser to access the webapp.



## Training
Do perform the fine tuning, you need the following steps:
1. Download the zipped file from [Cornell movie dialogue corpus](https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html), unzip it and put the folder in the main directory
2. run the following command
```bash
cd script
python3 train.py
```

## Relevant Link

[ChatBot App Template](https://github.com/chamkank/flask-chatterbot)

[DialoGPT fine tuning tutorial](https://colab.research.google.com/drive/15wa925dj7jvdvrz8_z3vU7btqAFQLVlG)