from transformers import AutoImageProcessor, AutoModel
from tqdm.contrib import tzip
from PIL import Image
import tensorrt
import pandas as pd
import numpy as np
import os
import torch
import transformers

transformers.logging.set_verbosity_error()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

cub_200_names_file = '../shared/cub-200-folder-names.txt'
latin_names_file = '../shared/latin_names.txt'
root_directory = '../CUB_200_2011/images'

used_models = ['google/vit-base-patch16-224-in21k', 'microsoft/resnet-34', 'microsoft/focalnet-tiny']


def readfile(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


def store_as_csv(embedding_dict, path):
    df = pd.DataFrame.from_dict(embedding_dict, orient='index')

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Name (Latin)'}, inplace=True)

    new_column_names = {'Name (Latin)': 'Name (Latin)'}
    for i in range(len(df.columns) - 1):
        new_column_names[i] = f'Neuron {i + 1}'
    df.rename(columns=new_column_names, inplace=True)

    df.to_csv(path, index=False)


def get_image_embeddings(image, model, preprocessor):
    image = preprocessor(images=image, return_tensors="pt").to(device)
    outputs = model(**image)

    return outputs.pooler_output.squeeze().detach().cpu().numpy()


def get_mean_embeddings(model, preprocessor, root_dir, folder_names, save_names, normalize=False):
    mean_embeddings = {}

    for folder, save_name in tzip(folder_names, save_names):
        subdirectory = root_dir + '/' + folder
        class_files = os.listdir(subdirectory)

        class_embeddings = []

        for img_path in class_files:
            file_path = os.path.join(subdirectory, img_path)
            image = Image.open(file_path).convert('RGB')

            embedding = get_image_embeddings(image, model, preprocessor)

            class_embeddings.append(embedding)

        mean_embedding = sum(class_embeddings) / len(class_embeddings)

        if normalize:
            mean_embedding /= np.linalg.norm(mean_embedding)

        mean_embeddings[save_name] = mean_embedding

    return mean_embeddings


cub_200_names = readfile(cub_200_names_file)
latin_names = readfile(latin_names_file)

for model_name in used_models:
    proc = AutoImageProcessor.from_pretrained(model_name)
    mod = AutoModel.from_pretrained(model_name).to(device)

    class_reps = get_mean_embeddings(mod, proc, root_directory, cub_200_names, latin_names)
    store_as_csv(class_reps, f'class_embeddings [{model_name.replace("/", "_")}].csv')
