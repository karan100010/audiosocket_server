import io
import numpy as np
import torch
torch.set_num_threads(1)
import torchaudio
torchaudio.set_audio_backend("soundfile")

model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=True)
(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

# Taken from utils_vad.py
def validate(model,
             inputs: torch.Tensor):
    with torch.no_grad():
        outs = model(inputs)
    return outs

# Provided by Alexander Veysov
def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

def vad(audio_chunk, sample_rate):
    # Read audio file
   audio_int16 = np.frombuffer(audio_chunk, np.int16)

   audio_float32 = int2float(audio_int16)

   val=model(torch.from_numpy(audio_float32),sample_rate).item()
   return val

def is_speech(audio_chunk, sample_rate):
    return vad(audio_chunk, sample_rate) > 0.85


