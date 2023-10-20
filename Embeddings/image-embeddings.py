import os

import pandas as pd
import torch
import transformers
from PIL import Image
from tqdm.contrib import tzip
from transformers import AutoImageProcessor, AutoModel

transformers.logging.set_verbosity_error()

device = "cuda:0" if torch.cuda.is_available() else "cpu"

cub_200_names_file = '../shared/cub-200-folder-names.txt'
latin_names_file = '../shared/latin_names.txt'

data_source = 'cub-200'
# data_source = 'botw'

root_directory = '../botw_data/MEDIA/Images' if data_source == 'botw' else '../CUB_200_2011/images'

# 'microsoft/resnet-34', 'microsoft/focalnet-tiny'
used_models = ['google/vit-base-patch16-224-in21k']


def readfile(path):
    with open(path, 'r') as f:
        return f.read().splitlines()


def store_as_csv(embedding_dict, path):
    embedding_dim = len(list(embedding_dict.values())[0])

    columns = [f'Neuron_{x + 1}' for x in range(embedding_dim)]
    df = pd.DataFrame.from_dict(embedding_dict, orient='index', columns=columns)

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'species'}, inplace=True)

    df.to_csv(path, index=False)


def get_image_embeddings(image, model, preprocessor):
    image = preprocessor(images=image, return_tensors="pt").to(device)
    outputs = model(**image)

    return outputs.pooler_output.squeeze().detach().cpu().numpy()


def get_mean_embeddings(model, preprocessor, root_dir, folder_names, save_names):
    mean_embeddings = {}

    for folder, save_name in tzip(folder_names, save_names):
        subdirectory = os.path.join(root_dir, folder)
        class_files = os.listdir(subdirectory)

        class_embeddings = []

        for img_path in class_files:
            file_path = os.path.join(subdirectory, img_path)
            image = Image.open(file_path).convert('RGB')

            embedding = get_image_embeddings(image, model, preprocessor)

            class_embeddings.append(embedding)

        mean_embedding = sum(class_embeddings) / len(class_embeddings)

        mean_embeddings[save_name] = mean_embedding

    return mean_embeddings


latin_names = readfile(latin_names_file)
folder_names = readfile(latin_names) if data_source == 'botw' else readfile(cub_200_names_file)

for model_name in used_models:
    proc = AutoImageProcessor.from_pretrained(model_name)
    mod = AutoModel.from_pretrained(model_name).to(device)

    class_reps = get_mean_embeddings(mod, proc, root_directory, folder_names, latin_names)
    store_as_csv(class_reps, f'Image/{model_name.replace("/", "-").split("-")[1]}-{data_source}.csv')
