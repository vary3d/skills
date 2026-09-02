# Examples

Golden folder (no cover PNGs in git — generate them with `cover.py`): [examples/m5-flange/](examples/m5-flange/).

## Pack an existing flange

User: “Make this `flange.scad` importable on Vary3D, plus M5 and M4 presets.”

1. Confirm a Customizer `.scad` already exists. If not, stop. The user needs **openscad-customizer**. Do not install it for them.
2. Baseline: `validate.py` on `flange.scad`; record `size`; `extract-params.py`.
3. Copy from the source (typical: `models/m5-flange/model.scad`) into `packages/m5-flange/model.scad` (or `include <flange.scad>` from `model.scad` if relatives would break).
4. Keep existing slider labels (do not rewrite to English). Add `flange_color = "#2A9D90"; // color` if missing; `"yes"`/`"no"` enums if the source used booleans. New listing copy in `info.json` is English unless the user asked otherwise.
5. `info.json`: `description` leads with object + mate (e.g. round flange, M5 holes); more sentences optional. Category `practical_gadgets`; tags from object / mate / feature (`flange`, `m5`, `bolt` — about 3, max 5). `validate-info.py`.
6. `variants.json` with M5 / M4 (`bolt_clearance_dia` + `pcd`). `bolt_clearance_dia` is Hidden on the default panel; presets may still override it.
7. `validate.py packages/m5-flange/model.scad --expect … --tol 1` using the baseline size.
8. `cover.py` then `cover-variants.py` (preset `-D` plus extra build roots). `validate-variants.py`. Open covers.
9. `generate-readme.py` (original Source; no Global bucket unless `params.scad` exists). Add README `## Print` if generate did not preserve one. Leave `models/` (or the original `flange.scad`) untouched.

## Fork from a public model

User: “Package this MIT GitHub file for Import from folder.”

Same as above, plus:

- Copy upstream `LICENSE` verbatim
- `ORIGIN.md` with Forked from URL, author, “presets and listing text only”
- `originType`: `fork` and source fields in `info.json`
- `generate-readme.py` uses the fork Source (not Vary3D original)
- Do **not** invent `parentModelId`

## Do not use this skill

User: “Design an M5 flange from scratch.”

That is **openscad-customizer** (separate skill; do not install it for them). After the `.scad` compiles, they can ask to pack.

User: “I only have an STL.”

Stop. This skill cannot make a site-importable folder from a mesh.
