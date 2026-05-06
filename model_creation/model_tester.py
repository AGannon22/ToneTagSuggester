import tkinter as tk
from tkinter import messagebox
import tensorflow as tf
from keras.models import load_model

tone_mapping = {
    0: "Neutral",
    1: "Happy",
    2: "Sad",
    3: "Jokes"
}

model = None

def load_model_on_start():
    global model
    try:
        model = load_model(r"model_creation\saved_model.keras")
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
        status_label.config(text="Model loaded successfully", fg="green")
    except Exception as e:
        status_label.config(text=f"Failed to load model: {e}", fg="red")

def predict_tone():
    if model is None:
        messagebox.showwarning("Warning", "No model loaded!")
        return

    text_input = text_entry.get("1.0", tk.END).strip()
    if not text_input:
        messagebox.showwarning("Warning", "Please enter some text")
        return

    try:
        text_tensor = tf.convert_to_tensor([text_input], dtype=tf.string)
        prediction = model.predict(text_tensor)
        predicted_number = int(prediction.argmax(axis=-1)[0])
        predicted_tone = tone_mapping.get(predicted_number, "Unknown")
        result_label.config(text=f"Predicted Tone: {predicted_tone} ({predicted_number})")
    except Exception as e:
        messagebox.showerror("Error", f"Prediction failed:\n{e}")

root = tk.Tk()
root.title("Tone Classifier (.h5 compatible)")

text_entry = tk.Text(root, height=5, width=50)
text_entry.pack(pady=10)

predict_button = tk.Button(root, text="Predict Tone", command=predict_tone)
predict_button.pack(pady=10)

result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack(pady=10)

status_label = tk.Label(root, text="Loading model...", fg="orange")
status_label.pack(pady=5)

# Load AFTER the UI widgets exist so status_label can be updated
root.after(100, load_model_on_start)

root.mainloop()