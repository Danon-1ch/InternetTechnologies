from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def get_health():
    return { "message": "Hello community, я не хочу быть вашей частью." }