import keras
import numpy as np

import configs

dataset_path = '../../testing/FINAL_RUSSIAN_RAP_DATASET.txt'

model_lstm = keras.models.load_model('../../testing/colab_lstm_4096/model59')

with open(dataset_path, encoding='utf-8') as f:
    text = f.read().lower()
print('corpus length:', len(text))
chars = sorted(list(set(text)))
print('total chars:', len(chars))
char_indices = dict((c, i) for i, c in enumerate(chars))
indices_char = dict((i, c) for i, c in enumerate(chars))


def sample(preds, temperature=1.0):
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def pred(sentence: str, model=model_lstm, diversity=configs.diversity):
    print()
    print('----- diversity:', diversity)
    generated = ''
    generated += sentence
    result = sentence
    for i in range(configs.rap_len):
        x_pred = np.zeros((1, len(sentence), len(chars)))
        for t, char in enumerate(sentence):
            x_pred[0, t, char_indices[char]] = 1.

        preds = model.predict(x_pred, verbose=0)[0]
        next_index = sample(preds, diversity)
        next_char = indices_char[next_index]

        sentence = sentence[1:] + next_char
        result += next_char
        if next_char == '>':
            break
    return result

