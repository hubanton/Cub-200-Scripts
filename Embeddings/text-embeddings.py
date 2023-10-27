import os

import pandas as pd
import torch
import transformers
from tqdm.contrib import tzip
from transformers import BertTokenizer, BertModel, BigBirdModel, BigBirdTokenizer

transformers.logging.set_verbosity_error()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

latin_names_file = '../shared/latin_names.txt'

VERSION = 'v1'

used_model = 'bert' # bert | bird

root_directory = f'../botw_data/Sounds_and_Vocal_Behavior/{VERSION}'



bird = "google/bigbird-roberta-base"
bert = 'bert-base-uncased'

def readfile(path, as_array=True):
    with open(path, 'r') as f:
        file = f.read()
    return file.splitlines() if as_array == True else file


def store_as_csv(embedding_dict, path):
    embedding_dim = len(list(embedding_dict.values())[0])

    columns = [f'Neuron_{x + 1}' for x in range(embedding_dim)]
    df = pd.DataFrame.from_dict(embedding_dict, orient='index', columns=columns)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'species'}, inplace=True)

    df.to_csv(path, index=False)


def get_text_embeddings(text, model, tokenizer):
    max_tokens = 512 if used_model == 'bert' else 2000
    tokenized_text = tokenizer(text, max_length=max_tokens, return_tensors='pt').to(device)

    outputs = model(**tokenized_text)

    return outputs.pooler_output.squeeze().detach().cpu().numpy()


def get_embeddings(model, tokenizer, root_dir, text_names, save_names):
    mean_embeddings = {}

    for text_name, save_name in tzip(text_names, save_names):
        file_path = os.path.join(root_dir, text_name + '.txt')
        text_description = readfile(file_path, as_array=False)

        mean_embeddings[text_name] = get_text_embeddings(text_description, model, tokenizer)
    return mean_embeddings


latin_names = readfile(latin_names_file)

if used_model == 'bird':
    tokenizer = BigBirdTokenizer.from_pretrained(bird)
    mod = BigBirdModel.from_pretrained(bird).to(device)
else:
    tokenizer = BertTokenizer.from_pretrained(bert)
    mod = BertModel.from_pretrained(bert).to(device)

class_reps = get_embeddings(mod, tokenizer, root_directory, latin_names, latin_names)
store_as_csv(class_reps, f'Text/{VERSION}_{used_model}.csv')
