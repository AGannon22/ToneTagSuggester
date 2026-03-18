import pandas as pd
import numpy as np
import os
import re
import io

ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT, "datasets")
def read_csv_with_fallback(path):
	encodings = ["utf-8", "cp1252", "latin-1"]
	last_exc = None
	for enc in encodings:
		try:
			return pd.read_csv(path, encoding=enc)
		except UnicodeDecodeError as e:
			last_exc = e
			continue
		except Exception:
			raise
	try:
		with open(path, "rb") as f:
			raw = f.read()
		text = raw.decode("utf-8", errors="replace")
		return pd.read_csv(io.StringIO(text))
	except Exception:
		if last_exc is not None:
			raise last_exc
		raise

ds1_path = os.path.join(DATA_DIR, "dataset1.csv")
ds2_path = os.path.join(DATA_DIR, "dataset2.csv")
dad_path = os.path.join(DATA_DIR, "dad-a-base.csv")
GOEMOTIONS_DIR = os.path.join(os.path.dirname(ROOT), "archive (6)", "data", "full_dataset")
goemotions_paths = [
    os.path.join(GOEMOTIONS_DIR, "goemotions_1.csv"),
    os.path.join(GOEMOTIONS_DIR, "goemotions_2.csv"),
    os.path.join(GOEMOTIONS_DIR, "goemotions_3.csv")
]

reg_data = read_csv_with_fallback(ds1_path)
data2 = read_csv_with_fallback(ds2_path)
joke_database = read_csv_with_fallback(dad_path)
goemotions_data = []
for path in goemotions_paths:
    if os.path.exists(path):
        df = read_csv_with_fallback(path)
        goemotions_data.append(df)

if goemotions_data:
    goemotions_df = pd.concat(goemotions_data, ignore_index=True)
else:
    goemotions_df = pd.DataFrame()

#reformat reg_data, this has /pos, /neu, and /neg 
#within our dataset, pos is 0, neu is 1, neg is 2, and j is 3
reg_data = reg_data[["sentiment","phrase"]]
reg_data = reg_data.rename(columns={"sentiment":"Sentiment"})
reg_data = reg_data.rename(columns={"phrase":"Text"})
mask_exact_neg = reg_data["Sentiment"].astype(str).str.strip().str.lower() == "negative"
reg_data.loc[mask_exact_neg, "Sentiment"] = 2
mask_exact_pos = reg_data["Sentiment"].astype(str).str.strip().str.lower() == "positive"
reg_data.loc[mask_exact_pos, "Sentiment"] = 0
mask_exact_neu = reg_data["Sentiment"].astype(str).str.strip().str.lower() == "neutral"
reg_data.loc[mask_exact_neu, "Sentiment"] = 1
print("reg_data sentiment counts:\n", reg_data["Sentiment"].value_counts(dropna=False))
# decided joke database should go bye bye
#joke_database = joke_database[["Joke"]]
#joke_database = joke_database.rename(columns={"Joke":"Text"})
#joke_database["Sentiment"] = 3
# reformat data2, this has 0 and 1
emotions = ["happy", "sadness"]
data2 = data2[data2["Emotion"].isin(emotions)]
data2 = data2[["Emotion","Text"]]
data2 = data2.rename(columns={"Emotion":"Sentiment"})
mask_exact_neg2 = data2["Sentiment"].astype(str).str.strip().str.lower().isin(["sadness"])
data2.loc[mask_exact_neg2, "Sentiment"] = 2
mask_exact_pos2 = data2["Sentiment"].astype(str).str.strip().str.lower() == "happy"
data2.loc[mask_exact_pos2, "Sentiment"] = 0

# Process GoEmotions data
if not goemotions_df.empty:
	joke_emotions = ["amusement"]
	positive_emotions = ['admiration', 'approval', 'caring', 'excitement', 'desire',
                       'gratitude', 'joy', 'love', 'optimism', 'pride']
	negative_emotions = ['disapproval', 'embarrassment', 'fear', 'grief', 'nervousness', 
                        'remorse', 'sadness']
	neutral_emotions = ['confusion', 'curiosity', 'relief', 'realization', 'surprise', 'neutral']    
	goemotions_processed = goemotions_df[['text']].copy()
	goemotions_processed = goemotions_processed.rename(columns={'text': 'Text'})
	goemotions_processed['Sentiment'] = 1  # Default to neutral
	# Check for positive emotions 
	positive_mask = goemotions_df[positive_emotions].sum(axis=1) > 0
	goemotions_processed.loc[positive_mask, 'Sentiment'] = 0
	# Check for sad
	negative_mask = (goemotions_df[negative_emotions].sum(axis=1) > 0) & ~positive_mask
	goemotions_processed.loc[negative_mask, 'Sentiment'] = 2
	#add jokes
	#funny_mask = (goemotions_df[joke_emotions].sum(axis=1) >0)
	#goemotions_processed.loc[funny_mask, 'Sentiment'] = 3
	emotion_columns = positive_emotions + negative_emotions + neutral_emotions
	has_any_emotion = goemotions_df[emotion_columns].sum(axis=1) > 0
	goemotions_processed = goemotions_processed[has_any_emotion]
else:
	goemotions_processed = pd.DataFrame()
dataset = pd.concat([reg_data, data2 ,goemotions_processed], ignore_index=True)
print(dataset['Sentiment'].value_counts())

out_path = os.path.join(DATA_DIR, 'combined_dataset.csv')
dataset.to_csv(out_path, index=False, encoding='utf-8')


