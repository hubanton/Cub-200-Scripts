import json

import torch
import torch.nn as nn
from torchaudio.models import wav2vec2_model


class AvesTorchaudioWrapper(nn.Module):

    def __init__(self, config_path, model_path):
        super().__init__()

        # reference: https://pytorch.org/audio/stable/_modules/torchaudio/models/wav2vec2/utils/import_fairseq.html

        self.config = self.load_config(config_path)
        self.model = wav2vec2_model(**self.config, aux_num_out=None)
        self.model.load_state_dict(torch.load(model_path))
        self.model.feature_extractor.requires_grad_(False)

    def load_config(self, config_path):
        with open(config_path, 'r') as ff:
            obj = json.load(ff)

        return obj

    def forward(self, sig):
        # extract_feature in the sorchaudio version will output all 12 layers' output, -1 to select the final one
        out = self.model.extract_features(sig)[0][-1]
        out = out.mean(dim=1)
        return out


def get_aves_model():
    torchaudio_model = AvesTorchaudioWrapper('util-audio/aves-base-bio.torchaudio.model_config.json',
                                             'util-audio/aves-base-bio.torchaudio.pt')
    torchaudio_model.eval()
    return torchaudio_model
