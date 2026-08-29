# Examples

Write where the user asked. If they did not, write `models/<slug>/model.scad`. [examples/m5-flange.scad](examples/m5-flange.scad) is a compiled-size sample (copy it into that path). MIT snippets: inline marked modules from `examples/*.scad` — do not `use` those files and do not `use <MCAD>`.

## Simple — flange (no JSON)

User: “M5 flange, OD 40, thickness 4, PCD 28, 4 holes.”

1. Route simple: one plate + center hole + bolt holes.
2. Write `models/m5-flange/model.scad` (or copy the sample and adjust):
   - `/* [Dimensions] */`: `outer_dia` `thickness` `inner_dia` `pcd` `bolt_count`. Hidden literals: `bolt_clearance_dia` (M5 table), `bed_chamfer`. One `flange_color`. No extra top-level formulas.
   - 2D `circle` difference, then `linear_extrude`
   - Small bed chamfer, no Minkowski
3. `validate.py`; if OD was given, `--expect 40 40 4`
4. Six views: `top` to confirm holes on the PCD
5. Do not write `brief.json`. Skip snapshot if the first pass is enough.
6. Do not write `info.json`, covers, or `packages/`.
7. `open-gui.py models/m5-flange/model.scad` so the user lands on the part.
8. Deliver: **One piece; no split.** Flange on the bed; no supports.

## Simple — holder for a known object (no JSON)

User: “Stand for a 40×3 mm souvenir coin, one piece, no supports.”

1. Route simple: one pedestal + cradle. **Mate holder** — the coin is the object; the stand follows.
2. Visible: `coin_d`, `coin_t`, one `*_color`. Add `tilt_deg` or `label_text` only if they said they will retune those.
3. **Do not** expose `arm_w`, `plate_t`, `lip_h`, `reveal_ratio`, `gap`, `base_h`, `label_size`, `push_hole`, `weight_save`, or a `part` enum (no ghost coin / section / interference in Customizer). Derive those in the module from `coin_d` / `coin_t`.
4. Wrong: a comment “everything keys off coin_d and coin_t” plus 14 sliders. That file is not Done — `extract-params.py` must print no warnings.
5. `validate.py --single-body`; six views; **One piece; no split.** Pedestal on the bed.

## Complex — spur gear pair (inline MIT modules)

User: “Module-1 spur gears, 20T and 40T, 8 mm face, 5 mm bore.”

1. Route complex: two printable meshes + mesh kinematics.
2. Read [references/spur-gear.md](references/spur-gear.md). Copy the marked block from [examples/spur-gear.scad](examples/spur-gear.scad) into `models/<slug>/model.scad`. Do not `use <MCAD>`.
3. `part = "all"` meshed preview; Print 1× pinion, 1× gear. Center distance `spur_center_distance`; large gear `spur_mesh_rotate`.
4. `validate.py --expect 62 42 8 --tol 1` on `all`. Skip `--single-body` on `all`; run it per token.
5. Deliver: Print 1× pinion, 1× gear; do not slice `all`.

## Complex — trapezoid thread (inline MIT modules)

User: “Threaded stud and nut, major 20, pitch 2.5.”

1. Read [references/trap-thread.md](references/trap-thread.md). Copy `male_thread` / `thread_tooth` from [examples/trap-thread.scad](examples/trap-thread.scad). Female = enlarged male; `fit_gap` on the nut only.
2. Do not `use <BOSL2/threading.scad>` for this.
3. Deliver: Print 1× stud, 1× nut.

## Simple — FDM holes (inline MIT modules)

- Vertical bolt hole → [polyhole.md](references/polyhole.md) / [examples/polyhole.scad](examples/polyhole.scad)
- Horizontal hole (shaft in XY) → [teardrop.md](references/teardrop.md) / [examples/teardrop.scad](examples/teardrop.scad)
- Machine screw into plastic (no insert) → [selftap.md](references/selftap.md) / [examples/selftap.scad](examples/selftap.scad)

Do not `use <MCAD/polyholes.scad>` or `teardrop.scad`. Heat-set brass still uses a round insert-OD hole, not `selftap_hole`.

## Complex — honeycomb angle bracket (JSON required)

User: “90° honeycomb lightening bracket, 80×80, thickness 5, M5 holes.”

1. Route complex: patterned cut + fillets + several holes.
2. Write `brief.json` next to the entry: bbox `[80,80,80]` (two 80 mm wings, 5 mm thick → 80³ AABB), MUST “honeycomb stays out of the solid ring around each hole”.
3. Write `plan.json`: base profile (inner-corner `offset` + honeycomb 2D cut) → extrude → upright same profile → `union` → through holes.
4. Write `models/angle-bracket/model.scad`: Customizer groups Dimensions / Features / Rendering. M5 hole diameter is Hidden (table), not a Holes group.
5. `validate.py --expect 80 80 80 --tol 1 --single-body` (one piece; no `part` enum).
6. Six views: `top` / `left` must show honeycomb and solid hole bosses.
7. `snapshot.py` iso + `top` (complex stores round 1). If honeycomb is invisible → fix the 2D mask only → render → snapshot; open `002/` vs `001/` of the same view. No random decoration.
8. Deliver: **One piece; no split.** Print on the back of one wing (or say which face); no `part` enum.

## Complex — box + lid (split for print)

User: “Box with a lid, 80×60×40, no supports if we can split.”

1. Soft wording (“no supports”) plus a **hard** driver: closed interior roof after reorient. Confirm: recommend **split** (lid / base); wait for OK. Do not skip Confirm because they said split.
2. Brief: `print.strategy` `split`; parts `base` qty 1, `lid` qty 1; joint `rabbet on the rim; host wall 2.0; lip 1.0 high × 0.8 wide; gap 0.25 on the groove`.
3. Plan notes: cut at the rim; copy that joint string; do not add a new CSG step type. Derived `fit_gap` / lip sizes, not Customizer knobs.
4. Write `models/split-box/model.scad`: `part = "all"; // [all:All, base:Base, lid:Lid]`. No `show_base` / `show_lid`. `lid_geom()` only for `all`; `part="lid"` calls `lid_print()` at the origin.
5. `validate.py --expect … --tol 1` on the default file (`all`). **Skip** `--single-body` on `all`. Then `--single-body --openscad-arg=-D --openscad-arg='part="base"'` and the same for `lid`.
6. Six views of the assembly; iso of each token in print pose. **2D section through the rim** (`section.py --plane xz --2d`) — do not use a 3D iso cutaway to judge the joint.
7. Deliver: Print 1× base, 1× lid; do not export STL from `all`.

## Simple — funnel (user asked to split; stay one piece)

User: “Funnel, split it so it prints without supports.”

1. Soft driver. From sizes: `atan(|r_top − r_bottom| / height)` ≈ 30° from vertical; wide end on the bed.
2. Confirm in the user’s language: **One piece (recommended)** — wall ~30°, no supports. Split only for a small bed. Wait.
3. User picks one piece → **stay simple** (one shell). No `brief.json`, no `part` enum.
4. Write `models/funnel/model.scad`. Deliver: **One piece; no split.** Wide end on the bed; wall ~30° from vertical; no supports.

## Research — iPhone 15 Pro case

User: “Design an iPhone 15 Pro case.”

1. **Research**: prefer user mm; else the in-skill table (146.6 × 70.6 × 8.25 mm) or quote those candidates in Confirm. Do not write SCAD from an unconfirmed page. Note camera bump position and USB-C port.
2. Route complex: mates to a real object, multiple cutouts.
3. Write `brief.json`: bbox from confirmed sizes, MUST “camera cutout does not block lens”, `sources` cites the skill table (or the Confirm’d numbers).
4. **Confirm**: show user “iPhone 15 Pro: 146.6 × 70.6 × 8.25 mm, camera cutout top-left, USB-C bottom. Does that match?” (in the user’s language). **One piece; no split** unless they asked to split *and* Confirm still picks split (a case is not a split trigger by default). Say the one-piece line even if they never mentioned split.
5. Write `plan.json`: back plate + raised edges + camera/USB cutouts.
6. Write `models/iphone-case/model.scad`: expose `wall_thickness`, `case_color`. `corner_radius` Hidden. No `part` enum.
7. `validate.py --expect 146.6 70.6 10 --tol 1 --single-body` (bbox includes case walls).
8. Six views + section through camera cutout.
9. Show user iso + top; ask in the user’s language whether the shape looks right.
10. `open-gui.py`; ask whether they can see it and whether the shape looks right.

## Research — 608 bearing holder (skill table)

User: “Design a 608 bearing holder.”

1. **Research**: in-skill table → 8 × 22 × 7 mm (bore × OD × width). Cite “skill table”. Do not ask how big a 608 is.
2. Route simple: one block + bearing pocket.
3. Write `models/bearing-holder/model.scad`: expose body size + color. 608 pocket (22 + clearance, depth 7 + extra) is derived / Hidden — not a main knob.
4. `validate.py --expect 32 32 12 --tol 1` (holder bbox, not bearing).
5. Six views: `top` shows pocket center.
6. Show user iso + top; ask in the user’s language whether the shape looks right.
7. `open-gui.py`; ask whether they can see it.

## Reference image — bracket from a photo

User: “Make this bracket” + a product photo (no dimensions).

1. **Open the photo first.** Route complex: spatial relations from a picture. Read [reference-image.md](references/reference-image.md).
2. Topology from the image (L-shape, two holes on the upright). Millimetres: in-skill bolt table, or ask **1** overall size. Do not measure pixels.
3. Write `brief.json`: `sources` includes `user-attached: <filename>`; MUST features from the photo in `special_features`.
4. **Confirm the reading** (in the user’s language): what you took as topology, which numbers did not come from the picture, what is unclear. Wait for OK.
5. Write `plan.json` / `models/<slug>/model.scad`.
6. Six views: show **iso + top and the photo**; ask whether it matches.
7. `open-gui.py`; ask whether they can see it and whether the shape looks right.

A fully dimensioned three-view of a flange may stay **simple** (same as the flange example). Do not promote just because there is an image.

## Small-edit

User: “Change the phone-stand default tilt to 70.”

Edit only the top-level `viewing_angle` on the existing file. Do not rewrite the profile, do not add Brief, do not snapshot unless geometry intent changed. **Still run `open-gui.py` at the end** so the user sees the new default in the Customizer.
