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

#### 3. Outside Dimensions
- **`outside_x`** (width): Total outside width of the frame
- **`outside_y`** (height): Total outside height of the frame

**Example:** For a frame that's 130mm × 180mm overall:
- `outside_x = 130mm`
- `outside_y = 180mm`

### Advanced Parameters

#### 4. Base Thickness
- **`base_thickness`** (default: 15.0mm): Width/thickness of the base layer pieces

**How it works:** The base layer pieces have a specified thickness. The back window is calculated from the outside dimensions:
- `back_window_x = outside_x - 2 × base_thickness`
- `back_window_y = outside_y - 2 × base_thickness`
- `back_frame_w = base_thickness` (side borders)
- `back_frame_h = base_thickness` (top/bottom borders)

**Example:** With `base_thickness = 15mm`, `outside_x = 130mm`, and `outside_y = 180mm`:
- `back_window_x = 130mm - 2 × 15mm = 100mm`
- `back_window_y = 180mm - 2 × 15mm = 150mm`
- `back_frame_w = 15mm` (each side border)
- `back_frame_h = 15mm` (each top/bottom border)

#### 5. Guide Fudge
- **`guide_fudge`** (default: 2.0mm): Clearance added to the middle layer pocket to help the art piece fit

**Example:** With `guide_fudge = 2mm` and `art_piece_x = 110mm`:
- Pocket width = `110mm + 2mm = 112mm`

**Note:** The front and base layers are always split into 4 puzzle pieces (top, bottom, left, right) to save material. This is not configurable.

## Calculated Dimensions

The generator automatically calculates these values from your inputs:

### Frame Borders (Front Layer)
- **`frame_w`** = `(outside_x - window_x) / 2` - Width of side borders
- **`frame_h`** = `(outside_y - window_y) / 2` - Height of top/bottom borders

**Example:** With `outside_x = 130mm` and `window_x = 90mm`:
- `frame_w = (130mm - 90mm) / 2 = 20mm` (each side border)

### Back Frame Borders (Base Layer)
- **`back_frame_w`** = `base_thickness` - Width of side borders on back
- **`back_frame_h`** = `base_thickness` - Height of top/bottom borders on back

**Example:** With `base_thickness = 15mm`:
- `back_frame_w = 15mm` (each side border)
- `back_frame_h = 15mm` (each top/bottom border)

### Back Window (Base Layer)
- **`back_window_x`** = `outside_x - 2 × base_thickness`
- **`back_window_y`** = `outside_y - 2 × base_thickness`

**Example:** With `outside_x = 130mm`, `outside_y = 180mm`, and `base_thickness = 15mm`:
- `back_window_x = 130mm - 2 × 15mm = 100mm`
- `back_window_y = 180mm - 2 × 15mm = 150mm`

### Middle Layer Pocket
- **`pocket_x`** = `art_piece_x + guide_fudge` - Pocket width
- **`pocket_y`** = `art_piece_y + guide_fudge` - Pocket height
- **`guide_w`** = `(outside_x - pocket_x) / 2` - Guide wall width
- **`guide_h`** = `(outside_y - pocket_y) / 2` - Guide wall height

**Example:** With `art_piece_x = 110mm`, `guide_fudge = 2mm`, and `outside_x = 130mm`:
- `pocket_x = 110mm + 2mm = 112mm`
- `guide_w = (130mm - 112mm) / 2 = 9mm` (each guide wall)

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

#### Unsplit Mode (`split_middle = False`)
- **1 piece:** Frame with rectangular pocket
  - Outer dimensions: `outside_x × outside_y`
  - Pocket dimensions: `pocket_x × pocket_y`
  - Guide walls: `guide_w` wide on sides, `guide_h` tall on top/bottom

**Example Output:**
- Middle frame: 130mm × 180mm with 112mm × 162mm pocket
- Guide walls: 9mm wide on sides, 9mm tall on top/bottom

#### Split Mode (`split_middle = True`)
- **4 pieces:** Separate guide pieces
  - Bottom guide: `outside_x × guide_h`
  - Left guide: `guide_w × pocket_y`
  - Right guide: `guide_w × pocket_y`

**Example Output:**
- Bottom guide: 130mm × 9mm
- Left guide: 9mm × 162mm
- Right guide: 9mm × 162mm

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
art_piece_x = 110mm    (photo + border)
art_piece_y = 160mm    (photo + border)
window_x = 90mm        (visible area)
window_y = 140mm       (visible area)
outside_x = 130mm      (total frame width)
outside_y = 180mm      (total frame height)
base_thickness = 15mm  (thickness of base pieces)
guide_fudge = 2mm
```

**Calculated Values:**
```
frame_w = (130 - 90) / 2 = 20mm        (side borders)
frame_h = (180 - 140) / 2 = 20mm       (top/bottom borders)
back_frame_w = 15mm                     (back side borders, from base_thickness)
back_frame_h = 15mm                     (back top/bottom borders, from base_thickness)
back_window_x = 130 - 2×15 = 100mm     (back window width)
back_window_y = 180 - 2×15 = 150mm     (back window height)
pocket_x = 110 + 2 = 112mm              (pocket width)
pocket_y = 160 + 2 = 162mm              (pocket height)
guide_w = (130 - 112) / 2 = 9mm        (guide wall width)
guide_h = (180 - 162) / 2 = 9mm        (guide wall height)
```

**Output Pieces:**

**Front Layer (Always Split):**
- Top border: 130mm × 20mm (with angled puzzle corners)
- Bottom border: 130mm × 20mm (with angled puzzle corners)
- Left border: 20mm × 180mm (with angled puzzle corners)
- Right border: 20mm × 180mm (with angled puzzle corners)

**Middle Layer (Split):**
- Bottom guide: 130mm × 9mm
- Left guide: 9mm × 162mm
- Right guide: 9mm × 162mm

**Base Layer (Always Split):**
- Top border: 130mm × 15mm (with angled puzzle corners)
- Bottom border: 130mm × 15mm (with angled puzzle corners)
- Left border: 15mm × 180mm (with angled puzzle corners)
- Right border: 15mm × 180mm (with angled puzzle corners)

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
- Two 130mm × 15mm pieces (top/bottom)
- Two 15mm × 180mm pieces (sides)

This allows you to use leftover material from other projects!

## Tips

1. **Art Piece Size:** Measure your actual artwork including any borders or mats you plan to include
2. **Window Size:** Should be smaller than art piece to create a border effect
3. **Outside Size:** Determines the overall frame size - choose based on your display space
4. **Base Thickness:** Choose based on how much you want the base pieces to overlap the art piece. A thickness of 15-20mm is usually sufficient to hold the art piece securely. The back window will be `outside_x - 2 × base_thickness` wide.
5. **Guide Fudge:** 2mm provides enough clearance for easy insertion without being too loose

## Validation

The generator validates that:
- All dimensions are positive
- Window dimensions are smaller than outside dimensions
- Back window dimensions are smaller than outside dimensions
- Calculated frame borders are positive

If validation fails, you'll get an error message with details about what's wrong.
