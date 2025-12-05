from fastapi import FastAPI

app = FastAPI(title="Main Server")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
