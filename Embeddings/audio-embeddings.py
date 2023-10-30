import os

import audiofile
import pandas as pd
import torch
import transformers
from tqdm import tqdm
from transformers import AutoModelForAudioClassification, ASTFeatureExtractor

from AvesModel import get_aves_model

transformers.logging.set_verbosity_error()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model_type = 'aves'

MODEL_NAME = "MIT/ast-finetuned-audioset-10-10-0.4593"

latin_names_file = '../shared/latin_names.txt'

root_directory = '../xeno_canto_data/Recordings'
# root_directory = '../botw_data/MEDIA/Audios'

target_directory = 'Audio/ast-embeddings-xeno-canto'


# target_directory = 'Audio/ast-embeddings-botw'


def readfile(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


def store_as_csv(embedding_dict, path):
    embedding_size = len(list(embedding_dict.values())[0])
    columns = [f'Neuron_{x + 1}' for x in range(embedding_size)]

    df = pd.DataFrame.from_dict(embedding_dict, orient='index', columns=columns)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'filename'}, inplace=True)

    df.to_csv(path, index=False)


def get_embedding(waveform, model, feature_extractor, model_type):
    if model_type == 'ast':
        extracted_features = feature_extractor(waveform, sampling_rate=16000, padding="max_length", return_tensors="pt")
        input_values = extracted_features.input_values.to(device)

        with torch.no_grad():
            output = model(input_values)
            return output['hidden_states'][-1].cpu().numpy()

    output = model(torch.from_numpy(waveform).to(device))
    return output.mean(dim=1).cpu().numpy()


def get_audio_embeddings(model, feature_extractor, root_dir: str, folder_names, model_type='ast'):
    # os.makedirs(target_directory, exist_ok=True)

    embeddings_collection = {}

    pbar = tqdm(folder_names)
    for folder_name in pbar:
        pbar.set_description(f'Processing {folder_name}...')

        # target_subdirectory = os.path.join(target_directory, folder_name)
        # os.makedirs(target_subdirectory, exist_ok=True)

        source_directory = os.path.join(root_dir, folder_name)
        audio_filenames = os.listdir(source_directory)

        for audio_filename in tqdm(audio_filenames):
            # base_filename = os.path.splitext(audio_filename)[0]
            # target_file_path = os.path.join(target_subdirectory, base_filename + '.npy')
            file_path = os.path.join(source_directory, audio_filename)

            waveform = audiofile.read(file_path, always_2d=True)[0]
            waveform = waveform.mean(0, keepdims=True)
            embedding = get_embedding(waveform, model, feature_extractor, model_type)

            # np.save(target_file_path, embedding)

            averaged_embedding = embedding.mean(1).squeeze()

            file_key = os.path.join(folder_name, audio_filename)
            embeddings_collection[file_key] = averaged_embedding

    return embeddings_collection


latin_names = readfile(latin_names_file)[:2]

if model_type == 'ast':
    ast_model = AutoModelForAudioClassification.from_pretrained(MODEL_NAME, output_hidden_states=True).to(device)
    ast_feature_extractor = ASTFeatureExtractor.from_pretrained(MODEL_NAME)

    results = get_audio_embeddings(ast_model, ast_feature_extractor, root_directory, latin_names, model_type)
else:
    complete_model = get_aves_model().to(device)
    results = get_audio_embeddings(complete_model, None, root_directory, latin_names, model_type)

store_as_csv(results, f'{target_directory}-{model_type}.csv')
