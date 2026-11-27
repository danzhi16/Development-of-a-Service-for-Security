from fastapi import FastAPI

app = FastAPI(title="Security Assessment Service")


# Liveness only; DB and queue checks are added once they exist in Compose.
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
