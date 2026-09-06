# M5 Bolt Flange

Round flange with a center bore and four bolt holes on a pitch circle.

## Source

Vary3D original. No upstream CAD.

This folder is the import package: entry file, listing copy, and presets when present.

Libraries: none

## Files

### Models

#### M5 Bolt Flange

`model.scad`

| Name | Default | Range | What it does |
|---|---|---|---|
| outer_dia | 40 | [20:1:80] | Outer diameter of the flange. |
| thickness | 4 | [2:0.5:12] | Plate thickness. |
| inner_dia | 10 | [4:0.5:24] | Center bore. |
| pcd | 28 | [16:1:70] | Bolt circle diameter. |
| bolt_count | 4 | [3:1:12] | Number of bolt holes. |
| flange_color | #2A9D90 | color |  |

## Presets

### M5

Clearance for M5 hardware.

![M5](covers/m5.png)

| Name | Value |
|---|---|
| bolt_clearance_dia | 5.3 |
| pcd | 28 |

### M4

Clearance for M4 hardware.

![M4](covers/m4.png)

| Name | Value |
|---|---|
| bolt_clearance_dia | 4.3 |
| pcd | 24 |

## Print

- **Settings:** PLA, 0.2mm layer, 2 walls, 15% gyroid infill, no supports.
- **Orientation:** Place the large face on the bed.
- **Why:** Keeps the plate flat and the chamfer on the top.

## License

MIT.
