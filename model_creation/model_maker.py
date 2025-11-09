import tensorflow as tf
import os
import re
import shutil
import string
from tensorflow import keras
from keras import layers,models
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras import losses

#stupid stupid path stuff
dataset = pd.read_csv("datasets/combined_dataset.csv")
ROOT = os.path.dirname(__file__)
data1_path = os.path.join(ROOT, "datasets", "dataset1.csv")
if os.path.exists(data1_path):
  data1 = pd.read_csv(data1_path)
else:
  data1 = None
out_path = os.path.join(ROOT, "datasets", "combined_dataset.csv")
dataset.to_csv(out_path, index=False)

dataset = dataset.dropna(subset=['Text', 'Sentiment'])
dataset['Text'] = dataset['Text'].astype(str)

# shuffle and split
dataset = dataset.sample(frac=1, random_state=42).reset_index(drop=True)
eighty_percent = int(0.8 * len(dataset))
train_set = dataset.iloc[:eighty_percent]
test_set = dataset.iloc[eighty_percent:]
train_texts = train_set['Text'].values
train_labels = train_set['Sentiment'].values
test_texts = test_set['Text'].values
test_labels = test_set['Sentiment'].values

print(len(train_texts), len(train_labels))
print(len(test_texts), len(test_labels))
batch_size = 64
print("dataset sentiment counts:\n", dataset["Sentiment"].value_counts(dropna=False))
def standardization_of_text(input):
    s = tf.strings.lower(input)
    s = tf.strings.regex_replace(s, r"#\w+", " ")
    s = tf.strings.regex_replace(s, r"@\w+", " ")
    s = tf.strings.regex_replace(s, "<br />", " ")
    s = tf.strings.regex_replace(s, f"[{re.escape(string.punctuation)}]", "")
    return s
max_features = 10000
sequence_length = 250
vectorize_layer = layers.TextVectorization(
    standardize=standardization_of_text,
    max_tokens=max_features,
    output_mode='int',
    output_sequence_length=sequence_length)
vectorize_layer.adapt(train_texts)

# create vectorized inputs (these are tensors)
x_train = vectorize_layer(train_texts)
x_test = vectorize_layer(test_texts)

print('Vectorized shape:', x_train.shape, x_test.shape)
print('Vocabulary size: {}'.format(len(vectorize_layer.get_vocabulary())))

# determine number of classes
num_classes = 4
embedding_dim = 16

    # multi-class classification

embed_dim = 128

model = models.Sequential([
  layers.Input(shape=(sequence_length,)),
  layers.Embedding(input_dim=max_features, output_dim=embed_dim),
  layers.Conv1D(128, 5, activation='relu'),
  layers.GlobalMaxPooling1D(),
  layers.Dense(64, activation='relu'),
  layers.Dropout(0.3),
  layers.Dense(4, activation='softmax')
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
epochs = 50
# train using vectorized numpy tensors
history = model.fit(
    x_train,
    train_labels,
    validation_data=(x_test, test_labels),
    epochs=epochs,
    batch_size=batch_size)

loss, accuracy = model.evaluate(x_test, test_labels)

print("Loss: ", loss)
print("Accuracy: ", accuracy)