from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is working"}

@app.post("/")
def predict(data: dict):
    return {"received": data}
