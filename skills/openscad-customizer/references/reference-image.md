# Reference images (user input)

User-attached photos, CAD views, and drawings are **input**. The six OpenSCAD views are **output**. Do not mix them up.

## When this file applies

The user attached, pasted, or named a local path for one or more images as the thing to copy. **Open and read every image before Brief or SCAD.** Ignoring an attachment is a process failure.

Same skill, same gates, same Customizer `.scad`. This is not a new skill and not image-to-mesh.

## Hard rules

1. **Topology and proportions from the image. Millimetres from text, the in-skill tables, or a question.** A photo is not a millimetre source. Do not “measure” pixels into mm unless the image itself has a stated scale **and** you Confirm those numbers.
2. **Do not skip Confirm because you saw the picture.** Image-derived geometry is easier to misread than a size list. Show what you read; wait for OK.
3. **Numbers read off a drawing are hypotheses.** Put them in the brief, then Confirm every critical size. A misread dimension is not a table value.
4. **Do not reconstruct a mesh, trace a bitmap to DXF, or write a measuring script** unless the user asked for that as a separate task. The deliverable is parametric CSG.

## Classify

```text
User attached image(s)
  ├─ product photo / render / style ref
  │     topology, style, rough assembly — not sizes
  ├─ orthographic 3-view (no dimensions)
  │     sketches for the Plan; ask 1 scale size (or the in-skill table for a named mating part)
  ├─ CAD screenshot (Fusion / SolidWorks / Onshape / …)
  │     same as 3-view; on-screen dimensions count only after Confirm
  └─ dimensioned drawing / blueprint
        extract numbers as hypotheses; Confirm every critical size
```

Several images: classify each. A photo plus a dimensioned view → topology from the photo, millimetres from the view (still Confirm).

## Route

**Stay simple** only when the structure is one plate plus holes **and** every needed size is in the text, an in-skill table, or a fully dimensioned view you have already read. Do not write brief/plan for ceremony.

**Promote to complex** (Confirm, then Plan) when:

- the image is a product photo or an undimensioned drawing (spatial relations from a picture)
- more than one body, a cut that is not a simple hole, or the projection / section is ambiguous
- you had to guess a scale

A fully labelled three-view of a washer is still simple. A phone-stand photo is not.

## Research

Use the in-skill tables and Confirm-gated sizes the same way as without an image. The picture does not skip Research.

If there is no scale and no table value:

- ask **1** scale dimension (overall length, or one hole diameter you can see), **or**
- ask **1–3** critical sizes plus usage context (same as brief-plan.md)

State the defaults you used. Do not invent millimetres from perspective.

## Brief and Confirm

Cite each attachment in `brief.json` `sources`:

```json
"sources": [
  "user-attached: front.png",
  "user-attached: side.png",
  "M5 clearance hole: ISO 273 normal fit (5.3 mm)"
]
```

Put MUST features you took from the image in `special_features` (boss kept solid, rib on the upright, no fillet on the bed face, …).

On Confirm, show the usual summary **plus** the reading:

1. What you took as topology (bodies, holes, which face is which)
2. Which millimetres did **not** come from the picture
3. What is still unclear (wall thickness, hidden back, first- vs third-angle, a section you cannot resolve)

Ask in the user’s language whether that reading is right. Wait. Then write Plan / SCAD.

## Plan

Orthographic views map onto `sketches[]` (front → XZ or YZ, top → XY). Name the source view in `notes`. Do not invent a third projection the user did not give; ask or keep that face simple.

## Verify

After six views, show **iso + top and the reference image(s)** together. Ask in the user’s language whether the shape matches the photo or drawing — not only whether it “looks right”.

Wrong structure vs the reference → back to Plan (complex) or rethink geometry (simple). Wrong numbers → edit SCAD. Same issue for 3 rounds without converging: stop and ask.

## Out of scope

- Photogrammetry / point clouds / organic sculpture from photos
- Automatic blueprint OCR or GD&T as a hard gate
- Vary3D packaging (`info.json`, covers) — that is **vary3d-package**; it does not ingest reference photos
- Copying attachments into `models/<slug>/refs/` unless the user asked to keep them
