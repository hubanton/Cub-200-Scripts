import os

import audiofile
import pandas as pd
import torch
from tqdm import tqdm
from transformers import ClapModel, RobertaTokenizerFast, ClapFeatureExtractor

audio_directory = '../xeno_canto_data/Recordings'
text_directory = '../botw_data/Sounds_and_Vocal_Behavior/v3'
cub_200_directory = './cub-200'

device = "cuda:0" if torch.cuda.is_available() else "cpu"

model = ClapModel.from_pretrained("laion/clap-htsat-unfused").to(device)

text_encoder = RobertaTokenizerFast.from_pretrained("laion/clap-htsat-unfused")
audio_extractor = ClapFeatureExtractor.from_pretrained("laion/clap-htsat-unfused")


# Function to load audio samples from a directory
def load_audio_from_path(path):
    waveform = audiofile.read(path, always_2d=True)[0]
    waveform = waveform.mean(0, keepdims=True)
    return waveform


def write_list_to_csv(file_path, data):
    df = pd.DataFrame(data, columns=["Species"])
    df.to_csv(file_path, index=False)


def load_text_from_directory(directory):
    with open(directory, "r") as f:
        text = f.read()
    return text


for split in range(1, 5):
    predictions = []
    labels = []

    split_directory = os.path.join(cub_200_directory, str(split))
    test_csv_path = os.path.join(split_directory, 'test.csv')

    labels_in_split = pd.read_csv(test_csv_path)['species'].tolist()
    results = []

    text_descriptions = [load_text_from_directory(os.path.join(text_directory, species + '.txt')) for species in
                         labels_in_split]

    # Iterate over species folders in the split
    for index, species_folder in enumerate(tqdm(labels_in_split)):
        bird_folder_path = os.path.join(audio_directory, species_folder)

        birds_from_species = os.listdir(bird_folder_path)

        for bird in tqdm(birds_from_species):
            bird_path = os.path.join(bird_folder_path, bird)

            audio_sample = load_audio_from_path(bird_path)

            with torch.no_grad():
                # Note that we could also use ClapProcessor which wraps the tokenizer and the feature extractor
                # However setting truncation throws an error (present on both parts) so we do it manually.

                encoding = text_encoder(text_descriptions, padding=True, max_length=512, truncation=True,
                                        return_tensors="pt")

                encoding["input_features"] = audio_extractor(audio_sample, sampling_rate=48000,
                                                             return_tensors="pt").input_features

                encoding.to(device)

                outputs = model(**encoding)
                logits_per_audio = outputs.logits_per_audio
                probs = logits_per_audio.softmax(dim=-1).squeeze()

            ground_truth = index

            predicted_label = torch.argmax(probs).cpu().item()

            labels.append(ground_truth)
            predictions.append(predicted_label)

    write_list_to_csv(f'{split}_predictions', predictions)
    write_list_to_csv(f'{split}_ground_truths', labels)
