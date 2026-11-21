# Parametric Overhead Crane Drawing Generator

A small full-stack web app that draws a dimensioned 2D drawing of a **single girder,
top-running overhead (EOT) crane** from a few inputs. Designs can be saved, listed,
reopened and edited. Built as a take-home assignment for Modern Crane Co.

**Drawings are preliminary.** Values marked "(est.)" are estimates, not engineering data.

## What it does

- Enter span, capacity, lifting height and duty group. A front view, a plan view and a
  data table are drawn live, with labelled dimensions.
- Save a design, see the saved list, reopen one and edit it. Designs live in SQLite.
- The server checks every input (ranges, types, unknown fields). The page does not
  validate anything itself, so you always see the server's real error messages.
- Each drawn dimension has a "basis" note (user input, from the reference drawing, or
  an estimate) and the drawing prints which values are estimates.

## Stack, and why

| Part | Choice | Why |
|---|---|---|
| Backend | Python + FastAPI | Validation and API docs come built in; small and readable |
| Validation | Pydantic (part of FastAPI) | One place to state the input rules; the server rejects bad input |
| Database | SQLite via Python's built-in `sqlite3` | No install, one file, enough for this size. No ORM, so SQL is visible |
| Drawing | SVG built as text in Python | Vector, labels stay sharp, no drawing library needed |
| Frontend | One HTML page + plain JavaScript, served by the same app | One command runs everything. No build step |
| Tests | pytest | 25 tests: rules, validation, database, drawing, endpoints |

## Run it

Needs **Python 3.11 or newer** (developed on 3.14, also tested on 3.13) and Git.

Windows (PowerShell):

```powershell
git clone https://github.com/fatvma/crane-drawing-generator.git
cd crane-drawing-generator
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app
```

If PowerShell blocks the activate script, run
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.

macOS / Linux:

```bash
git clone https://github.com/fatvma/crane-drawing-generator.git
cd crane-drawing-generator
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app
```

Then open **http://127.0.0.1:8000/**. API docs are at http://127.0.0.1:8000/docs.

The database file `crane_designs.db` is created automatically in the folder you start
the server from. Set the environment variable `CRANE_DB_PATH` to use another location.

## Run the tests

```
python -m pytest -v
```

## API

| Method and path | Purpose |
|---|---|
| `GET /api/health` | Is the server alive |
| `GET /api/limits` | Allowed input ranges (the page reads these) |
| `POST /api/preview` | Dimensions for given inputs, nothing saved |
| `POST /api/preview/drawing` | The SVG drawing for given inputs (`?name=` sets the title) |
| `POST /api/designs` | Save a design (201) |
| `GET /api/designs` | List saved designs, newest change first |
| `GET /api/designs/{id}` | Open one design with calculated dimensions |
| `PUT /api/designs/{id}` | Edit a design |
| `GET /api/designs/{id}/drawing` | The SVG drawing of a saved design |

Bad input gets HTTP 422 with the field and the reason. Unknown ids get 404.

## Project layout

```
app/
  crane.py      geometry rules (no web code); every rule says where it came from
  schemas.py    input validation rules
  database.py   all SQL
  drawing.py    builds the SVG
  main.py       the API and the web page
  static/       index.html, app.js
tests/          pytest tests
```

Only the **inputs** of a design are stored. Dimensions and the drawing are recalculated
when a design is opened, so a corrected rule also fixes old designs.

## Where the numbers come from

Rules are in `app/crane.py`, each with its source and a confidence level.

- **Reference drawing (the sample supplied with the assignment):** overall length =
  span + 270 mm; wheel base about span / 6.6; end carriage = wheel base + 510 mm; hook
  approach 920 / 1150 mm. Each is **one data point** from a single 10 t / 25 m crane,
  so it is an estimate for other sizes.
- **Input ranges** (1-20 t, 7.5-30 m span, 3-30 m lift): taken from several suppliers'
  published ranges. These differ between suppliers and are not a standard.
- **Soft span warning:** a US dealer's guideline table of maximum span per capacity
  (Mazzella Companies), interpolated in a straight line (my assumption). Warning only.
- **Girder depth = span / 20:** **my own guess, no source.** Only used to draw the girder.
- **Duty groups A3 to A6:** FEM/ISO labels, shown in the data table only.

Sources used:
- Mazzella Companies, single vs double girder guideline table: https://www.mazzellacompanies.com/?p=1917
- Supplier specification ranges: https://www.eotcranekit.com/specifications/single-girder-eot-crane-specifications.html and https://loadmate.in/product/single-girder-eot-cranes/
- Duty class comparison (A5 = M5 = FEM 2m): https://www.kinocranes.com/crane-hoist-duty-classification
- Lifting height definition (hook centre to ground): https://dgcrane.com/posts/overhead-crane-parameters-and-specific-classification
- Wheel base about span / 7 (blog-level source, only a loose cross-check): https://www.firgelliauto.com/blogs/mechanisms/travelling-crane

## Known limitations

- One crane type only: single girder, top-running. No double girder, underhung or gantry.
- The estimates above are not engineering data. Do not use drawings for manufacture.
- No weights, wheel loads, deflection, power or structural checks.
- Vertical sizes in the front view are schematic, not to scale (like the reference).
- Hook approach is fixed, because it really depends on the hoist model.
- No logins, so all designs are shared. No delete button and no versions of a design.
- Drawing is SVG only. There is no DXF or PDF output.
- Validation errors use FastAPI's default 422 format.
- The database has no migration tool; the table is created at start-up if missing.

## Time spent

**2.5 hours** (real time, including setup, learning and writing).

## Other documents

- `DECISIONS.md`: my own assumptions and judgments (written without AI).
- `AI_LOG.md`: how I used AI and how I checked it.