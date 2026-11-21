from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles

from app import crane, database, drawing
from app.schemas import CraneInputs, DesignIn

SVG = "image/svg+xml"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app):
    """Runs once when the server starts: make sure the table exists."""
    conn = database.connect()
    database.init_db(conn)
    conn.close()
    yield


app = FastAPI(title="Crane Drawing Generator", lifespan=lifespan)


def get_db():
    """Gives each request its own database connection, closed afterwards."""
    conn = database.connect()
    try:
        yield conn
    finally:
        conn.close()


def design_response(row):
    """A saved design = its stored inputs + freshly calculated dimensions."""
    inputs = {key: row[key] for key in
              ("span_m", "capacity_t", "lifting_height_m", "duty_group")}
    return {
        "id": row["id"],
        "name": row["name"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        **crane.compute_design(**inputs),
    }


def not_found(design_id):
    return HTTPException(status_code=404, detail=f"Design {design_id} not found")


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


@app.post("/api/preview/drawing")
def preview_drawing(inputs: CraneInputs, name: str = Query(default="", max_length=80)):
    """The drawing (SVG) for the given inputs, without saving anything.
    The optional ?name= is only used as the title on the drawing."""
    design = crane.compute_design(**inputs.model_dump())
    design["name"] = name.strip()
    return Response(drawing.build_svg(design), media_type=SVG)

@app.post("/api/designs", status_code=201)
def create_design(payload: DesignIn, conn=Depends(get_db)):
    inputs = payload.model_dump(exclude={"name"})
    row = database.create_design(conn, payload.name, inputs)
    return design_response(row)


@app.get("/api/designs")
def list_designs(conn=Depends(get_db)):
    return [dict(row) for row in database.list_designs(conn)]


@app.get("/api/designs/{design_id}")
def get_design(design_id: int, conn=Depends(get_db)):
    row = database.get_design(conn, design_id)
    if row is None:
        raise not_found(design_id)
    return design_response(row)


@app.get("/api/designs/{design_id}/drawing")
def design_drawing(design_id: int, conn=Depends(get_db)):
    """The drawing (SVG) of a saved design."""
    row = database.get_design(conn, design_id)
    if row is None:
        raise not_found(design_id)
    return Response(drawing.build_svg(design_response(row)), media_type=SVG)


@app.put("/api/designs/{design_id}")
def update_design(design_id: int, payload: DesignIn, conn=Depends(get_db)):
    inputs = payload.model_dump(exclude={"name"})
    row = database.update_design(conn, design_id, payload.name, inputs)
    if row is None:
        raise not_found(design_id)
    return design_response(row)



# The web page. This must stay LAST: it answers every address not matched above.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")