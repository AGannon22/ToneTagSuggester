import tkinter as tk
from tkinter import filedialog, messagebox
import tensorflow as tf
from keras.models import load_model
tone_mapping = {
    0: "Neutral",
    1: "Happy",
    2: "Sad",
    3: "Angry"
}
model = load_model("model_creation\saved_model.h5")
model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
def predict_tone():
    if model is None:
        messagebox.showwarning("Warning", "No model loaded!")
        return

    text_input = text_entry.get("1.0", tk.END).strip()
    if not text_input:
        messagebox.showwarning("Warning", "Please enter some text")
        return

    try:
        # Convert to rank-1 string tensor
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
status_label = tk.Label(root, text="No model loaded", fg="red")
status_label.pack(pady=5)

root.mainloop()
