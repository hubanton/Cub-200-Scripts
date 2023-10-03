from transformers import ViTImageProcessor, ViTModel
from PIL import Image
import pandas as pd
import numpy as np
import os


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

    # Save the DataFrame to a CSV file
    df.to_csv(path, index=False)


def calculate_class_mean_embeddings(model, root_dir, folder_names, save_names, normalize=False):
    processor = ViTImageProcessor.from_pretrained(model_name)
    model = ViTModel.from_pretrained(model)

    mean_embeddings = {}

    for folder, save_name in zip(folder_names, save_names):
        subdirectory = root_dir + '/' + folder

        class_files = os.listdir(root_dir + '/' + folder)

        print(len(class_files), folder, save_name)

        class_embeddings = []

        for img_path in class_files:
            file_path = os.path.join(subdirectory, img_path)
            image = Image.open(file_path)
            image = processor(images=image, return_tensors="pt")

            outputs = model(**image)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()
            class_embeddings.append(embedding)

        mean_embedding = sum(class_embeddings) / len(class_embeddings)

        if normalize:
            mean_embedding /= np.linalg.norm(mean_embedding)

        mean_embeddings[save_name] = mean_embedding

    return mean_embeddings


model_name = 'google/vit-base-patch16-224-in21k'
root_directory = '../CUB_200_2011/images'
cub_200_names_file = '../shared/cub-200-folder-names.txt'
latin_names_file = '../shared/latin_names.txt'

cub_200_names = readfile(cub_200_names_file)[:3]
latin_names = readfile(latin_names_file)[:3]

class_representations = calculate_class_mean_embeddings(model_name, root_directory, cub_200_names, latin_names)

store_as_csv(class_representations, 'class_embeddings.csv')