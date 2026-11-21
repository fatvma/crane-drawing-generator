from fastapi import FastAPI

app = FastAPI(title="Crane Drawing Generator")


@app.get("/api/health")
def health():
    """Tiny endpoint to check the server is alive."""
    return {"status": "ok"}