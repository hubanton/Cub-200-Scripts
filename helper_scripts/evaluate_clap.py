import os

import pandas as pd
import torch
import torchaudio
from sklearn.metrics import f1_score, accuracy_score, recall_score
from transformers import AutoProcessor, ClapModel

audio_directory = '../xeno_canto_data/Recordings'
text_directory = '../botw_data/Sounds_and_Vocal_Behavior/v3'
cub_200_directory = './cub-200'
splits = [str(i) for i in range(5)]

model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
processor = AutoProcessor.from_pretrained("laion/clap-htsat-unfused")


# Function to load audio samples from a directory
def load_audio_from_directory(directory):
    audio_samples = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                waveform, _ = torchaudio.load(file_path)
                audio_samples.append(waveform)
    return audio_samples


def load_text_from_directory(directory):
    with open(directory, "r") as f:
        text = f.read()
    return text


# Initialize lists to store evaluation metrics for each split
f1_scores = []
accuracy_scores = []
uar_scores = []

for split in splits:
    split_directory = os.path.join(cub_200_directory, split)
    test_csv_path = os.path.join(split_directory, 'test.csv')

    labels_in_split = pd.read_csv(test_csv_path)['species'].tolist()
    results = []

    text_descriptions = [load_text_from_directory(os.path.join(text_directory, species + '.txt')) for species in
                         labels_in_split]

    # Iterate over species folders in the split
    for index, species_folder in enumerate(labels_in_split):
        text_folder_path = os.path.join(audio_directory, species_folder)
        # Load text descriptions for the current species
        audio_sample = load_audio_from_directory(text_folder_path)

        print(text_descriptions)
        print(len(text_descriptions))
        print(len(labels_in_split))
        inputs = processor(text=text_descriptions, audios=audio_sample, return_tensors="pt", padding=True)

        outputs = model(**inputs)
        logits_per_audio = outputs.logits_per_audio
        probs = logits_per_audio.softmax(dim=-1)

        # Assuming you have ground truth labels for each test sample
        ground_truth_labels = [species_folder] * len(audio_sample)

        # Convert probabilities to predicted labels
        predicted_labels = torch.argmax(probs, dim=-1).tolist()

        # Calculate F1 score
        f1 = f1_score(ground_truth_labels, predicted_labels, average='weighted')
        f1_scores.append(f1)

        # Calculate accuracy
        accuracy = accuracy_score(ground_truth_labels, predicted_labels)
        accuracy_scores.append(accuracy)

        # Calculate Unweighted Average Recall (UAR)
        uar = recall_score(ground_truth_labels, predicted_labels, average='macro')
        uar_scores.append(uar)

# Calculate the average scores across all splits
avg_f1 = sum(f1_scores) / len(f1_scores)
avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
avg_uar = sum(uar_scores) / len(uar_scores)

print(f"Average F1 Score: {avg_f1}")
print(f"Average Accuracy: {avg_accuracy}")
print(f"Average UAR: {avg_uar}")
