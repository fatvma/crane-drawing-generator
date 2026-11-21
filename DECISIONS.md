# DECISIONS

## 1. Who is the user, and what do they need?

The main user I had in mind was a sales or estimating engineer. They need a quick preliminary crane drawing that can help them understand a configuration during the quotation process.

The application is not intended for manufacturing or final engineering design because it does not perform structural calculations or safety checks.

The main risk is that someone might treat estimated dimensions as final. This could result in an incorrect quotation or, more seriously, someone using unverified dimensions for manufacturing.

To reduce this risk, the drawing marks estimated values with `(est.)`, displays warnings for certain configurations and includes a notice saying it is preliminary and not for manufacture.

The API also returns notes explaining the basis of dimensions, but these notes are not currently visible on the web page.

## 2. What assumptions did I make?

Some of the initial scope and implementation choices were suggested by Claude. I reviewed them, discussed the reasoning and agreed to use them for this first version.

**Crane type**

I kept the application limited to a single-girder, top-running overhead crane. The provided reference drawing showed this configuration, so it was a practical starting point. Supporting other crane types would require additional rules and calculations.

This does not mean that a single-girder crane is suitable for every application.

**Inputs**

The application accepts four inputs:

- Span
- Capacity
- Lifting height
- Duty group

These were chosen to keep the first version simple while including basic crane information.

One important limitation is that not all inputs change the drawing:
- Span changes the drawing geometry.
- Lifting height changes the displayed value.
- Capacity is shown in the data table and is also used for warnings.
- Duty group is shown in the data table but does not affect the geometry.

I kept capacity and duty group because they are important information for a sales engineer, even though the current version does not use them for engineering calculations.

**Input ranges**

The supported ranges are:

| Input | Range |
|---|---|
| Capacity | 1–20 tonnes |
| Span | 7.5–30 metres |
| Lifting height | 3–30 metres |

These ranges were proposed using published specifications from different suppliers. Since supplier ranges differ, I treated them as limits for this application, not universal engineering limits.

Inputs outside these ranges are rejected by the backend. This does not mean that a crane outside these ranges cannot be built.

**Units**

I used metres for span and lifting height, tonnes for capacity and millimetres for drawing dimensions. These units match the reference drawing and make the inputs easier to understand.

## 3. Where did the dimensional rules come from?

The provided reference drawing was the main source for the initial dimensions. Claude helped interpret the drawing, and I checked the measurements against the original myself.

The rules used are:

- Overall length = span + 270 mm
- Wheel base = span / 6.6
- End carriage length = wheel base + 510 mm
- Hook approach = 920 mm / 1150 mm

These values came from one reference crane. They should not be treated as proven rules for every crane size.

For example, the reference drawing has a 25 m span and approximately 3800 mm wheel base. This is where the span / 6.6 relationship comes from.

Claude also searched for other published information. One source gave a minimum wheel base guideline, while a scanned example from another source showed a different relationship. This raised doubts about whether the same formula works for smaller cranes. I have kept the value as an estimate because there is not enough reliable information to establish a better formula.

**Girder depth**

The girder depth is calculated using:

`girder_depth = span / 20`

This is the weakest assumption in the application. It was a guess suggested by Claude to make the drawing look plausible. It has no verified source, even though the value is printed as a dimension.

I would not rely on this value for an actual crane design. It needs to be checked by an experienced engineer.

**Span warning**

The application also uses a table from Mazzella, a US crane supplier, as a loose guideline for maximum cost-effective spans at different capacities.

Straight-line interpolation between the table values was used as an assumption. This is only a warning, not a safety check. Interestingly, the 25 m reference crane also triggers this warning, which shows why it should not be treated as a strict engineering limit.

Duty group information is based on a supplier comparison table. The application displays this information but does not perform a full duty-cycle assessment.

## 4. What did I leave out?

I kept the first version focused on generating and saving preliminary drawings.

I did not implement:

- Double-girder, underhung or gantry cranes.
- Structural strength, deflection or safety calculations.
- Crane and trolley weights or wheel-load calculations.
- Hoisting, travelling and traversing speeds.
- Power and electrical specifications.
- Different hook approaches for different hoist models.
- True vertical scaling of the drawing.
- User accounts, design deletion or version history.
- PDF and DXF exports.

The main reason for leaving out engineering calculations was that I did not have enough verified information or reliable rules to calculate them for different crane configurations.

Other features, such as authentication, version history and additional export formats, were outside the scope of the initial assessment.

## 5. What would I ask an experienced crane engineer?

I would ask these three questions:

1. How should wheel base, end carriage length and girder depth change with different crane spans and capacities?

2. Which engineering standards and calculations should be used to check whether a crane is suitable for its capacity and duty group?

3. How do different hoist and trolley models affect hook approach and other dimensions?

These answers would help replace the current assumptions with more reliable engineering rules.

## 6. What would I improve with another week?

My priorities would be:

1. Collect more verified crane drawings and improve the dimensional formulas, especially wheel base and girder depth.
2. Show the basis of each dimension on the web page so users can understand which values come from reference data and which are estimates.
3. Make it clearer that capacity and duty group do not currently drive the drawing geometry, although capacity is used for warnings.
4. Work with an experienced engineer to introduce proper engineering calculations and validation.
5. After improving the calculations, consider additional crane types, PDF/DXF export, user accounts and design version history.

I would focus on improving the accuracy and reliability of the dimensions before adding more features.