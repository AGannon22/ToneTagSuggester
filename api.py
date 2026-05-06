from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tensorflow as tf
from keras.models import load_model
import uvicorn

tone_mapping = {
    0: "Neutral",
    1: "Happy",
    2: "Sad",
    3: "Jokes"
}

model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    try:
        model = load_model(r"model_creation\saved_model.keras")
        model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"]
        )
        print("Model loaded successfully")
    except Exception as e:
        print(f"Failed to load model: {e}")
    yield
    print("Shutting down...")

app = FastAPI(title="tonetagapi", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    predicted_tone: str
    predicted_number: int

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        text_tensor = tf.convert_to_tensor([request.text], dtype=tf.string)
        prediction = model.predict(text_tensor)
        predicted_number = int(prediction.argmax(axis=-1)[0])
        predicted_tone = tone_mapping.get(predicted_number, "Unknown")
        return PredictResponse(predicted_tone=predicted_tone, predicted_number=predicted_number)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)