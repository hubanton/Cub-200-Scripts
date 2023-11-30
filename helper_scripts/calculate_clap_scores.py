import os

import pandas as pd
from sklearn.metrics import f1_score, recall_score, accuracy_score


# Function to calculate metrics and return a dictionary
def calculate_metrics(y_true, y_pred):
    f1 = f1_score(y_true, y_pred, average='macro')
    uar = recall_score(y_true, y_pred, average='macro')
    accuracy = accuracy_score(y_true, y_pred)

    metrics_dict = {
        'F1_Score': f1,
        'UAR': uar,
        'Accuracy': accuracy
    }

    return metrics_dict


# Directory containing the files
results_directory = 'clap_results'

# Loop through files
num_files = 5
all_metrics = []

for i in range(num_files):
    ground_truths_path = os.path.join(results_directory, f'{i}_ground_truths')
    predictions_path = os.path.join(results_directory, f'{i}_predictions')

    # Load ground truth and predictions
    ground_truths = pd.read_csv(ground_truths_path)
    predictions = pd.read_csv(predictions_path)

    # Convert dataframes to lists
    y_true = ground_truths['Species'].tolist()
    y_pred = predictions['Species'].tolist()

    # Calculate metrics
    metrics_dict = calculate_metrics(y_true, y_pred)

    # Add split index to metrics_dict
    metrics_dict['Split'] = i

    # Append metrics to the list
    all_metrics.append(metrics_dict)

# Calculate average metrics
average_metrics = {}
for metric_dict in all_metrics:
    for metric in metric_dict.keys():
        if metric in average_metrics:
            average_metrics[metric] += metric_dict[metric]
        else:
            average_metrics[metric] = metric_dict[metric]

for key in all_metrics[0].keys():
    print(average_metrics[key], len(all_metrics))
    average_metrics[key] = average_metrics[key] / len(all_metrics)

# Append average metrics to the list
average_metrics['Split'] = 'Average'
all_metrics.append(average_metrics)

# Convert metrics to a DataFrame and save to a CSV file
output_file_name = 'clap_results/CLAP_MODEL_XENO-CANTO_audio_metrics.csv'
metrics_df = pd.DataFrame(all_metrics)
metrics_df.to_csv(output_file_name, index=False)
