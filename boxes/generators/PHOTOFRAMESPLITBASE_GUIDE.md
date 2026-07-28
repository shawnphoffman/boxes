# Photo Frame Split Base Generator - Inputs and Outputs Guide

## Overview

The Photo Frame Split Base generator creates a 3-layer photo frame with simplified measurements. It generates laser-cuttable pieces that can be assembled into a frame to display artwork. The front and base layers are always split into puzzle-like pieces to save material.

## Input Parameters

### Core Dimensions

These three sets of measurements define your frame:

#### 1. Art Piece Dimensions
- **`art_piece_x`** (width): Total width of your art piece including any border content
- **`art_piece_y`** (height): Total height of your art piece including any border content

**Example:** If you have a photo that's 100mm × 150mm with a 5mm border on all sides, your art piece dimensions would be:
- `art_piece_x = 110mm` (100mm + 5mm + 5mm)
- `art_piece_y = 160mm` (150mm + 5mm + 5mm)

#### 2. Window Dimensions
- **`window_x`** (width): Width of the visible window in the front layer (what shows through)
- **`window_y`** (height): Height of the visible window in the front layer

**Example:** If you want a 90mm × 140mm viewing area:
- `window_x = 90mm`
- `window_y = 140mm`

#### 3. Frame Width
- **`frame_width`**: Width of the visible front border, applied equally to all four sides

The outside dimensions are **derived**, not entered:
- `outside_x = window_x + 2 × frame_width`
- `outside_y = window_y + 2 × frame_width`

This guarantees the border is the same width on the top, bottom and both sides
without having to work backwards from an overall size.

**Example:** With `window_x = 90mm`, `window_y = 140mm` and `frame_width = 20mm`:
- `outside_x = 90 + 2 × 20 = 130mm`
- `outside_y = 140 + 2 × 20 = 180mm`

### Units

Every length accepts an optional unit suffix. A bare number is millimetres:

| Input | Value |
|---|---|
| `150` | 150mm |
| `150mm` | 150mm |
| `15cm` | 150mm |
| `6in` | 152.4mm |
| `6"` | 152.4mm |

This works on the command line, in the web form, and in saved URLs.

### Advanced Parameters

#### 4. Base Overlap
- **`base_overlap`** (default: 10.0mm): How far the base layer laps over the art piece on each side

**How it works:** The base layer sits behind the art with a smaller opening than
the front, forming a lip that stops the art falling out the back. You specify
how much that lip grips the art; the base border width is **derived**:

```
base_thickness = max(art_gap_x, art_gap_y) + base_overlap
```

where `art_gap_x = (outside_x - art_piece_x) / 2` is the distance from the outer
edge in to the art piece edge (and likewise for y). The larger of the two gaps
is used, because an asymmetric mat leaves different gaps horizontally and
vertically and the lip has to hold on all four sides.

Everything else follows from it:
- `back_frame_w = base_thickness` (side borders)
- `back_frame_h = base_thickness` (top/bottom borders)
- `back_window_x = outside_x - 2 × base_thickness`
- `back_window_y = outside_y - 2 × base_thickness`

**Example:** With `art_piece = 100 × 150mm`, `outside = 130 × 180mm` and `base_overlap = 10mm`:
- `art_gap_x = (130 - 100) / 2 = 15mm`, `art_gap_y = (180 - 150) / 2 = 15mm`
- `base_thickness = max(15, 15) + 10 = 25mm`
- `back_window_x = 130 - 2 × 25 = 80mm` (art overlaps it by 10mm each side)
- `back_window_y = 180 - 2 × 25 = 130mm` (art overlaps it by 10mm each side)

Because the border width is derived, the grip on the art stays at `base_overlap`
no matter how you change `frame_width` or the art size. A wider frame simply
produces wider base pieces.

#### 5. Guide Fudge (Horizontal)
- **`guide_fudge_x`** (default: 2.0mm): Horizontal clearance in the middle layer pocket to help the art piece fit

**Example:** With `guide_fudge_x = 2mm` and `art_piece_x = 110mm`:
- Pocket width = `110mm + 2mm = 112mm`

**Note:** Vertical clearance is hardcoded to 0 and is no longer exposed as an
input, because any vertical fudge causes the artwork to miss the intended
window alignment. The front and base layers are always split into 4 puzzle
pieces (top, bottom, left, right) to save material. This is not configurable.

## Calculated Dimensions

The generator automatically calculates these values from your inputs:

### Outside Dimensions
- **`outside_x`** = `window_x + 2 × frame_width` - Total outside width
- **`outside_y`** = `window_y + 2 × frame_width` - Total outside height

### Frame Borders (Front Layer)
- **`frame_w`** = `frame_width` - Width of side borders
- **`frame_h`** = `frame_width` - Height of top/bottom borders

Both equal `frame_width`, which is what keeps the border consistent on all four sides.

### Back Frame Borders (Base Layer)
- **`art_gap_x`** = `(outside_x - art_piece_x) / 2` - Outer edge in to the art edge
- **`art_gap_y`** = `(outside_y - art_piece_y) / 2` - Same, vertically
- **`base_thickness`** = `max(art_gap_x, art_gap_y) + base_overlap` - Derived base border width
- **`back_frame_w`** = `base_thickness` - Width of side borders on back
- **`back_frame_h`** = `base_thickness` - Height of top/bottom borders on back

**Example:** With `art_piece = 100 × 150mm`, `outside = 130 × 180mm` and `base_overlap = 10mm`:
- `art_gap_x = 15mm`, `art_gap_y = 15mm`
- `base_thickness = 15 + 10 = 25mm`
- `back_frame_w = back_frame_h = 25mm`

### Back Window (Base Layer)
- **`back_window_x`** = `outside_x - 2 × base_thickness`
- **`back_window_y`** = `outside_y - 2 × base_thickness`

**Example:** With `outside_x = 130mm`, `outside_y = 180mm`, and `base_thickness = 25mm`:
- `back_window_x = 130mm - 2 × 25mm = 80mm`
- `back_window_y = 180mm - 2 × 25mm = 130mm`

### Middle Layer Pocket
- **`pocket_x`** = `art_piece_x + guide_fudge_x` - Pocket width
- **`pocket_y`** = `art_piece_y` - Pocket height (vertical fudge is fixed at 0)
- **`guide_w`** = `(outside_x - pocket_x) / 2` - Guide wall width
- **`guide_h`** = `(outside_y - pocket_y) / 2` - Guide wall height (top/bottom bars)
- **`middle_side_h`** = `outside_y - guide_h` - Height of the left/right side pieces (spans from top of bottom bar to top of frame)

**Example:** With `art_piece_x = 110mm`, `art_piece_y = 160mm`, `guide_fudge_x = 2mm`, `outside_x = 130mm`, and `outside_y = 180mm`:
- `pocket_x = 110mm + 2mm = 112mm`
- `pocket_y = 160mm + 0mm = 160mm`
- `guide_w = (130mm - 112mm) / 2 = 9mm` (each guide wall)
- `guide_h = (180mm - 160mm) / 2 = 10mm` (top/bottom bars)
- `middle_side_h = 180mm - 10mm = 170mm` (side pieces)

## Output Pieces

The generator creates pieces for three layers. Front and base layers are always split into puzzle pieces.

### Front Layer

- **4 pieces:** Puzzle-style border pieces
  - Top border: `outside_x × frame_h` with angled corners
  - Bottom border: `outside_x × frame_h` with angled corners
  - Left border: `frame_w × outside_y` with angled corners
  - Right border: `frame_w × outside_y` with angled corners

**Example Output:**
- Top border: 130mm × 20mm
- Bottom border: 130mm × 20mm
- Left border: 20mm × 180mm
- Right border: 20mm × 180mm

### Middle Layer

The middle layer is always split into 3 separate guide pieces, open at the top
so the art can slide in:
  - Bottom guide: `outside_x × guide_h`
  - Left guide: `guide_w × middle_side_h`
  - Right guide: `guide_w × middle_side_h`

**Example Output:** (with guide_fudge_x=2)
- Bottom guide: 130mm × 10mm
- Left guide: 9mm × 170mm
- Right guide: 9mm × 170mm

### Base/Back Layer

- **4 pieces:** Puzzle-style border pieces (thickness defined by `base_thickness`)
  - Top border: `outside_x × base_thickness` with angled corners
  - Bottom border: `outside_x × base_thickness` with angled corners
  - Left border: `base_thickness × outside_y` with angled corners
  - Right border: `base_thickness × outside_y` with angled corners

**Example Output:**
- Top border: 130mm × 15mm
- Bottom border: 130mm × 15mm
- Left border: 15mm × 180mm
- Right border: 15mm × 180mm

### Reference Piece
- **1 piece:** Art piece outline (for reference/planning)
  - Dimensions: `art_piece_x × art_piece_y`

**Example Output:**
- Art piece reference: 110mm × 160mm

## Complete Example

### Scenario: Framing a 4" × 6" Photo

**Inputs:**
```
art_piece_x = 110mm      (photo + border)
art_piece_y = 160mm      (photo + border)
window_x = 90mm          (visible area)
window_y = 140mm         (visible area)
frame_width = 20mm       (visible border, all four sides)
base_overlap = 10mm      (how far the base laps over the art)
guide_fudge_x = 2mm      (horizontal clearance)
```

**Calculated Values:**
```
outside_x = 90 + 2×20 = 130mm          (derived total width)
outside_y = 140 + 2×20 = 180mm         (derived total height)
frame_w = 20mm                          (side borders, = frame_width)
frame_h = 20mm                          (top/bottom borders, = frame_width)
art_gap_x = (130 - 110) / 2 = 10mm     (outer edge in to art edge)
art_gap_y = (180 - 160) / 2 = 10mm
base_thickness = max(10, 10) + 10 = 20mm  (derived from base_overlap)
back_frame_w = 20mm                     (back side borders, from base_thickness)
back_frame_h = 20mm                     (back top/bottom borders, from base_thickness)
back_window_x = 130 - 2×20 = 90mm      (art laps over it by 10mm each side)
back_window_y = 180 - 2×20 = 140mm     (art laps over it by 10mm each side)
pocket_x = 110 + 2 = 112mm              (pocket width)
pocket_y = 160mm                        (pocket height, no vertical fudge)
guide_w = (130 - 112) / 2 = 9mm        (guide wall width)
guide_h = (180 - 160) / 2 = 10mm       (top/bottom bar height)
middle_side_h = 180 - 10 = 170mm      (side piece height)
```

**Output Pieces:**

**Front Layer (Always Split):**
- Top border: 130mm × 20mm (with angled puzzle corners)
- Bottom border: 130mm × 20mm (with angled puzzle corners)
- Left border: 20mm × 180mm (with angled puzzle corners)
- Right border: 20mm × 180mm (with angled puzzle corners)

**Middle Layer (Split):**
- Bottom guide: 130mm × 10mm
- Left guide: 9mm × 170mm
- Right guide: 9mm × 170mm

**Base Layer (Always Split):**
- Top border: 130mm × 20mm (with angled puzzle corners)
- Bottom border: 130mm × 20mm (with angled puzzle corners)
- Left border: 20mm × 180mm (with angled puzzle corners)
- Right border: 20mm × 180mm (with angled puzzle corners)

**Reference:**
- Art piece outline: 110mm × 160mm

## Material Savings

Splitting layers saves material by allowing you to cut pieces from smaller scraps:

**Unsplit Front (not available):** Would require one 130mm × 180mm piece
**Split Front (always used):** Can use:
- Two 130mm × 20mm pieces (top/bottom)
- Two 20mm × 180mm pieces (sides)

**Unsplit Base (not available):** Would require one 130mm × 180mm piece
**Split Base (always used):** Can use:
- Two 130mm × 20mm pieces (top/bottom)
- Two 20mm × 180mm pieces (sides)

This allows you to use leftover material from other projects!

## Tips

1. **Art Piece Size:** Measure your actual artwork including any borders or mats you plan to include
2. **Window Size:** Should be smaller than art piece to create a border effect
3. **Frame Width:** Sets the visible border and, with the window, the overall frame size. Because it applies to all four sides, the border stays consistent without any arithmetic on your part.
4. **Base Overlap:** How much of the art the base lip grips. 10mm is comfortable for most work; go higher for heavy or thick pieces, lower only on small frames where 10mm would eat the opening. You no longer size the base pieces yourself - the border width is derived, so the grip stays put when you change the frame.
5. **Guide Fudge X:** 2mm provides enough horizontal clearance for easy insertion without being too loose.
6. **Units:** Enter any length in inches if that is how you measured it - `6in`, `6"`, `15cm` and `150mm` are all accepted, and a bare number means millimetres.

## Validation

The generator validates that:
- All dimensions are positive
- Window dimensions are smaller than the art piece
- `base_overlap` is greater than zero, so the base actually retains the art
- The derived back window is still positive
- The art piece (plus horizontal fudge) fits inside the derived outside dimensions

If validation fails, you'll get an error message with details about what's wrong.

Window and back-window dimensions no longer need checking against the outside
size: the outside size is derived from them, so they cannot exceed it.
