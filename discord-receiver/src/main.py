from fastapi import FastAPI

app = FastAPI(title="Discord Receiver")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
