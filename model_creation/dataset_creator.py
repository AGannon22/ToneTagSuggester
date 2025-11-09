import pandas as pd
import numpy as np
import os
import re
import io

# Use script directory so the script works regardless of current working directory
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

reg_data = read_csv_with_fallback(ds1_path)
data2 = read_csv_with_fallback(ds2_path)
joke_database = read_csv_with_fallback(dad_path)

#reformat reg_data, this has pos, neu, and neg 
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
# reformat joke database, this will be 3
joke_database = joke_database[["Joke"]]
joke_database = joke_database.rename(columns={"Joke":"Text"})
joke_database["Sentiment"] = 3
# reformat data2, this has 0 and 1
emotions = ["anger", "fear", "happy", "sadness"]
data2 = data2[data2["Emotion"].isin(emotions)]
data2 = data2[["Emotion","Text"]]
data2 = data2.rename(columns={"Emotion":"Sentiment"})
mask_exact_neg2 = data2["Sentiment"].astype(str).str.strip().str.lower().isin(["anger", "sadness", "fear", "disgust"])
data2.loc[mask_exact_neg2, "Sentiment"] = 2
mask_exact_pos2 = data2["Sentiment"].astype(str).str.strip().str.lower() == "happy"
data2.loc[mask_exact_pos2, "Sentiment"] = 0
dataset = pd.concat([reg_data, joke_database,data2], ignore_index=True)
print(dataset.head())
print("dataset sentiment counts:\n", dataset["Sentiment"].value_counts(dropna=False))


# save combined dataset to datasets directory (non-destructive overwrite of combined_dataset.csv)
out_path = os.path.join(DATA_DIR, 'combined_dataset.csv')
dataset.to_csv(out_path, index=False, encoding='utf-8')


