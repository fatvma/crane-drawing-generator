# AI_LOG

## Tools Used

I used **Claude (claude.ai, Sonnet 5.5)** as my AI assistant throughout this assessment.

I mainly used it as a technical tutor and coding assistant. It helped me with:

- **Development:** Building the FastAPI backend, input validation, SQLite database operations, SVG drawing generation, frontend and automated tests.
- **Debugging:** Understanding errors, identifying their causes and fixing issues during development. I shared terminal output, screenshots and relevant code when I got stuck.
- **Research:** Exploring crane configurations, supplier specifications, duty classifications and dimensional rules. I also checked measurements from the provided reference drawing myself.
- **Documentation:** Preparing an initial draft of the README and helping me organize the information needed for this log.

I used Claude to discuss and evaluate the decisions behind the project, but I am responsible for the final content of `DECISIONS.md`, which I wrote myself.

## Key Prompts and How I Used AI

### 1. Setting the working approach

I started by asking Claude to act as a step-by-step technical tutor and guide me through the assessment. I provided the assignment requirements and reference drawing.

Claude helped me understand the requirements, suggested a suitable technology stack (FastAPI, SQLite, SVG and plain JavaScript), and guided me through implementation in smaller steps.

I followed the guidance, ran the code locally and made decisions about the scope of the application along the way.

### 2. Debugging errors during development

When I encountered errors during test collection, I shared the terminal output with Claude.

For example, after receiving four collection errors, Claude suggested running:

`python -c "import app.crane"`

This helped identify an indentation error in `crane.py`.

Another issue occurred when I accidentally replaced a line in the `basis` block instead of adding a new one. This caused a `KeyError: 'wheel_base_mm'`. I corrected the code, and the test `test_every_dimension_has_a_basis_note` helped catch the issue.

### 3. Checking the project files

I shared a screenshot of my project folder and the contents of my existing `main.py` after encountering 404 errors.

Claude identified that the file still contained the older version with only the health endpoint. I replaced it with the updated implementation.

This helped me understand that sometimes the problem was not with the API logic itself, but with an outdated file in my project.

### 4. Verifying measurements from the reference drawing

Claude helped interpret the measurements in the provided reference drawing, including 4310, 3800, 25270, 920 and 1150 mm.

Since the image was small, I checked the measurements against the original drawing myself before using them.

I retained these values as reference points but treated them as estimates rather than universal rules, since they came from only one crane drawing.

### 5. Reviewing and documenting project decisions

I asked Claude to help me review the assumptions behind the application by asking questions about the intended user, crane configuration, dimensional rules, sources and limitations.

This helped me identify which decisions were supported by the reference drawing, which were based on supplier information, and which were assumptions that still needed engineering verification.

Claude provided feedback and helped organize the discussion into notes. I used those notes to inform my own `DECISIONS.md` rather than asking it to write the document for me.

## AI Mistakes and Limitations

### 1. Incorrect Python version recommendation

During setup, Claude initially recommended downloading Python 3.12 or 3.13.

I shared the Python download page with it, and we reviewed the release information. The available Windows installers and release status did not support the original recommendation in the way Claude had suggested.

I subsequently installed Python 3.14 alongside the newer version on my system and used `py -3.14` to run the project.

This was a reminder to check installation instructions against the actual official documentation instead of relying entirely on AI suggestions.

### 2. Wheel base estimation rule

The wheel base calculation in the application uses:

`wheel_base = span / 6.6`

This rule was derived from the provided reference drawing, which showed a 25 m span and an approximately 3800 mm wheel base.

During a later review of the assumptions, Claude identified another scanned reference containing a 25 ft span and a 7 ft 8 in wheel base. This produced a considerably different ratio and raised questions about whether the formula could be applied consistently across different crane sizes.

This evidence had not been highlighted when the original rule was proposed. It showed that relying on a single reference drawing was not sufficient to establish a general dimensional rule.

I kept the value marked as an estimate and documented it as an area requiring further verification rather than treating the formula as an established engineering rule.

## How I Verified the Work

I did not rely solely on Claude's explanations. I checked the implementation and tested the application during development.

My verification included:

- Comparing the measurements interpreted by Claude with the original reference drawing.
- Running the automated test suite, which contains 25 tests covering dimensional rules, input validation, database operations, drawing generation and application routes.
- Checking that invalid inputs are rejected by the backend and that validation errors are returned appropriately.
- Testing the creation, listing, reopening and editing of saved designs.
- Running the project from a clean repository clone using the documented setup instructions and checking that the tests passed.
- Reviewing the README against the actual implementation and correcting claims that did not match the code.

During the final review, I also identified limitations that needed to be stated more clearly. For example, the dimensional basis notes are returned by the API but are not currently displayed on the web page. Capacity and duty group are included in the data table but do not drive the geometric calculations.

These limitations are documented rather than presenting the application as a complete engineering design tool.

## Final Note

AI assistance was used extensively for implementation, debugging, research and documentation. I reviewed the generated code, ran the application and tests, checked important measurements and discussed the assumptions behind the dimensional rules.

The application is a preliminary drawing generator, not a substitute for engineering calculations or verification. Any estimated dimensions would need to be checked against appropriate engineering references before being used for an actual crane design or manufacture.