from fastapi import FastAPI

from app import crane
from app.schemas import CraneInputs

app = FastAPI(title="Crane Drawing Generator")


@app.get("/api/health")
def health():
    """Tiny endpoint to check the server is alive."""
    return {"status": "ok"}


@app.get("/api/limits")
def limits():
    """Allowed input ranges, so the web page doesn't have to copy them."""
    return {
        "span_m": {"min": crane.SPAN_M_RANGE[0], "max": crane.SPAN_M_RANGE[1]},
        "capacity_t": {"min": crane.CAPACITY_T_RANGE[0], "max": crane.CAPACITY_T_RANGE[1]},
        "lifting_height_m": {"min": crane.LIFT_M_RANGE[0], "max": crane.LIFT_M_RANGE[1]},
        "duty_groups": list(crane.DUTY_GROUPS),
    }


@app.post("/api/preview")
def preview(inputs: CraneInputs):
    """Calculate dimensions for the given inputs without saving anything."""
    return crane.compute_design(**inputs.model_dump())