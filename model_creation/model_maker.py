import tensorflow as tf
import os
import subprocess
import re
import string
from tensorflow import keras
from keras import layers,models
import pandas as pd
import matplotlib.pyplot as plt
from keras import losses

#stupid stupid path stuff
dataset = pd.read_csv("model_creation\datasets\combined_dataset.csv")
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
num_classes = 4
embedding_dim = 16
embed_dim = 128
vectorize_layer.build((None,))  # or (None, 1)
model = models.Sequential([
  vectorize_layer,
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
print(model.summary())
epochs = 5
history = model.fit(
    train_texts,
    train_labels,
    validation_data=(test_texts, test_labels),
    epochs=epochs,
    batch_size=batch_size)

loss, accuracy = model.evaluate(test_texts, test_labels)

print("Loss: ", loss)
print("Accuracy: ", accuracy)
examples = tf.constant([
  "That was really funny!",
  "Can you get that to me by tommorow?",
  "The movie was terrible...",
  "Why did the chicken cross the road? To get to the other side!",
  "I love spending time with my family."
])
example_labels = tf.constant([0, 1, 2,3,0])

model.export("model_creation/saved_model")
print('\nSaved model:')