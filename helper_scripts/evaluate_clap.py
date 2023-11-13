import os

import pandas as pd
import yaml
from sklearn.metrics import accuracy_score, f1_score, recall_score
from transformers import AutoProcessor, ClapModel


class AudioProcessor:
    def __init__(self, audio_directory, text_directory):
        self.audio_directory = audio_directory
        self.text_directory = text_directory

    def load_labels_from_yaml(self, yaml_path):
        with open(yaml_path, 'r') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)
            return [str(i) for i in range(len(data['species']))]

    def load_audio_samples(self, labels):
        audio_samples = []
        label_mapping = {label: str(i) for i, label in enumerate(labels)}

        for label in os.listdir(self.audio_directory):
            label_directory = os.path.join(self.audio_directory, label)
            if os.path.isdir(label_directory) and label in label_mapping:
                for filename in os.listdir(label_directory):
                    filepath = os.path.join(label_directory, filename)
                    audio_samples.append({"filename": filepath, "label": label_mapping[label]})

        return audio_samples


class ClapEvaluator:
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor

    def calculate_uar(self, y_true, y_pred):
        recall_per_class = recall_score(y_true, y_pred, average=None)
        uar = sum(recall_per_class) / len(recall_per_class)
        return uar

    def evaluate(self, audio_samples, labels_for_split):
        y_true_list = []
        y_pred_list = []

        for sample in audio_samples:
            text_filepath = os.path.join(self.processor.text_directory, sample["label"], "description.txt")
            with open(text_filepath, 'r', encoding='utf-8') as file:
                input_text = [file.read()]

            inputs = self.processor.processor(text=input_text, audios=sample["filename"], return_tensors="pt",
                                              padding=True)
            outputs = self.model(**inputs)
            logits_per_audio = outputs.logits_per_audio
            predicted_labels = logits_per_audio.argmax(dim=-1).cpu().numpy().tolist()

            true_label = sample["label"]
            y_true_list.append(true_label)
            y_pred_list.append(predicted_labels[0])

        accuracy = accuracy_score(y_true_list, y_pred_list)
        f1 = f1_score(y_true_list, y_pred_list, average="macro")
        uar = self.calculate_uar(y_true_list, y_pred_list)

        return accuracy, f1, uar


def main():
    # Directory paths
    audio_directory = '../xeno_canto_data/Recordings'
    text_directory = '../botw_data/Sounds_and_Vocal_Behavior/v3'
    cub_200_directory = '../cub-200'

    audio_processor = AudioProcessor(audio_directory, text_directory)
    clap_model = ClapModel.from_pretrained("laion/clap-htsat-unfused")
    clap_processor = AutoProcessor.from_pretrained("laion/clap-htsat-unfused")

    # Load labels from the test.yaml file
    label_list = []
    for split_folder in os.listdir(cub_200_directory):
        split_folder_path = os.path.join(cub_200_directory, split_folder)
        if os.path.isdir(split_folder_path):
            yaml_path = os.path.join(split_folder_path, 'test.yaml')
            label_list.extend(audio_processor.load_labels_from_yaml(yaml_path))

    # Create a DataFrame to store the results
    results_df = pd.DataFrame(columns=['Split', 'Accuracy', 'F1 Score', 'UAR'])

    clap_evaluator = ClapEvaluator(clap_model, clap_processor)

    # Evaluate for each split
    for split_folder in os.listdir(cub_200_directory):
        split_folder_path = os.path.join(cub_200_directory, split_folder)
        if os.path.isdir(split_folder_path):
            print(f"Evaluating for split: {split_folder}")

            yaml_path = os.path.join(split_folder_path, 'test.yaml')
            labels_for_split = audio_processor.load_labels_from_yaml(yaml_path)

            audio_samples_for_split = audio_processor.load_audio_samples(labels_for_split)

            accuracy, f1, uar = clap_evaluator.evaluate(audio_samples_for_split, labels_for_split)

            # Print and store the results in the DataFrame
            print(f"Accuracy: {accuracy:.4f}")
            print(f"F1 Score: {f1:.4f}")
            print(f"Unweighted Average Recall (UAR): {uar:.4f}")
            print()

            results_df = results_df.append({
                'Split': split_folder,
                'Accuracy': accuracy,
                'F1 Score': f1,
                'UAR': uar
            }, ignore_index=True)

    # Write the results to a CSV file
    results_df.to_csv('evaluation_results.csv', index=False)
    print("Results written to 'evaluation_results.csv'")


if __name__ == "__main__":
    main()
