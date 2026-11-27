from fastapi import Depends, FastAPI, Response

from app.config import Settings, get_settings
from app.health import run_checks
from app.routers import runs, tasks

app = FastAPI(title="Security Assessment Service")
app.include_router(tasks.router)
app.include_router(runs.router)


@app.get("/health")
async def health(response: Response, settings: Settings = Depends(get_settings)) -> dict:
    checks = await run_checks(settings)
    healthy = all(result == "ok" for result in checks.values())
    if not healthy:
        response.status_code = 503
    return {"status": "ok" if healthy else "unavailable", "checks": checks}
