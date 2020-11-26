from transformers import AutoModelWithLMHead, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-small')
# model = AutoModelWithLMHead.from_pretrained('microsoft/DialoGPT-small')
# model = AutoModelWithLMHead.from_pretrained('model/output_animation')
# tokenizer = AutoModelWithLMHead.from_pretrained('model/output_animation')
model = AutoModelWithLMHead.from_pretrained('model/output_annie')
# tokenizer = AutoTokenizer.from_pretrained('model/output_annie')
# model = AutoModelWithLMHead.from_pretrained('model/output_all')
# tokenizer = AutoModelWithLMHead.from_pretrained('model/output_all')



def get_response(input, chat_history_ids):
    ''' input a string, return a string of response
    input:
        input (str): a string input
        chat_history_ids (tensor): a tensor of encoded chat history
    output:
        response (str): a string output as response
        chat_history_ids (tensor): a tensor of encoded chat history with the new input and response
    '''

    # encode the new user input, add the eos_token and return a tensor in Pytorch
    new_user_input_ids = tokenizer.encode(input + tokenizer.eos_token, return_tensors='pt')
    
    # append the new user input tokens to the chat history
    if chat_history_ids == None:
        bot_input_ids = new_user_input_ids
    else:
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) 

    # generated a response while limiting the total chat history to 1000 tokens, 
    chat_history_ids = model.generate(
        bot_input_ids, max_length=200,
        pad_token_id=tokenizer.eos_token_id,  
        no_repeat_ngram_size=3,       
        do_sample=True, 
        top_k=100, 
        top_p=0.7,
        temperature = 0.8
    )

    # pretty print last ouput tokens from bot
    response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    return response, chat_history_ids


def re_encode(input_string_ls):
    ''' use tokenizer to reencode the input string
    input:
        input_string_ls (string[]): a list of string in the conversation
    output:
        re_encode_input_ids (tensor): a tensor of encoded string
    '''
    new_seq = ''
    for input in input_string_ls:
        new_seq += input
        new_seq += tokenizer.eos_token
    re_encode_input_ids = tokenizer.encode(new_seq, return_tensors='pt')
    return re_encode_input_ids
    

if __name__ == "__main__":
    print(get_response("Hello", chat_history_ids=None))