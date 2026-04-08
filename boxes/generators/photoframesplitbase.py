# Copyright (C) 2013-2016 Florian Festi, 2024 marauder37
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import inspect
import logging
import math
from dataclasses import dataclass, fields

from boxes import Boxes, Color, boolarg, edges

logger = logging.getLogger(__name__)

@dataclass
class Dimensions:
    """
    Calculate the dimensions of a simplified photo frame.

    Uses three direct measurements:
    - art_piece_x, art_piece_y: Total size of art piece including border content
    - window_x, window_y: Size of visible window (what shows through front)
    - outside_x, outside_y: Total outside dimensions of frame
    """

    art_piece_x: float
    art_piece_y: float
    window_x: float
    window_y: float
    outside_x: float
    outside_y: float
    base_thickness: float
    guide_fudge_x: float = 2.0
    guide_fudge_y: float = 0.0
    backing_enabled: bool = False
    backing_margin: float = 5.0
    name: str = ""

    def __post_init__(self):
        self.check()

    @property
    def frame_w(self):
        """Width of the frame border on sides (calculated from outside and window)"""
        return (self.outside_x - self.window_x) / 2

    @property
    def frame_h(self):
        """Height of the frame border on top/bottom (calculated from outside and window)"""
        return (self.outside_y - self.window_y) / 2

    @property
    def base_x(self):
        """Width of the base layer, which is also the overall width of the piece"""
        return self.outside_x

    @property
    def base_y(self):
        """Height of the base layer, which is also the overall height of the piece"""
        return self.outside_y

    @property
    def back_frame_w(self):
        """Width of the frame border on sides for back/base layer"""
        return self.base_thickness

    @property
    def back_frame_h(self):
        """Height of the frame border on top/bottom for back/base layer"""
        return self.base_thickness

    @property
    def back_window_x(self):
        """Width of the window in the back/base layer"""
        return self.outside_x - 2 * self.base_thickness

    @property
    def back_window_y(self):
        """Height of the window in the back/base layer"""
        return self.outside_y - 2 * self.base_thickness

    @property
    def pocket_x(self):
        """Width of the pocket in middle layer for art piece"""
        return self.art_piece_x + self.guide_fudge_x

    @property
    def pocket_y(self):
        """Height of the pocket in middle layer for art piece"""
        return self.art_piece_y + self.guide_fudge_y

    @property
    def guide_w(self):
        """Width of the guide walls in middle layer"""
        return (self.outside_x - self.pocket_x) / 2

    @property
    def guide_h(self):
        """Height of the guide walls in middle layer"""
        return (self.outside_y - self.pocket_y) / 2

    @property
    def backing_x(self):
        """Width of the backing layer rectangle"""
        return self.outside_x - 2 * self.backing_margin

    @property
    def backing_y(self):
        """Height of the backing layer rectangle"""
        return self.outside_y - 2 * self.backing_margin

    @property
    def middle_side_h(self):
        """Height of the middle layer side pieces; spans from top of bottom to top of frame"""
        return self.outside_y - self.guide_h

    @property
    def centre_x(self):
        """
        Midpoint of the whole frame
        """
        return self.base_x / 2

    @property
    def centre_y(self):
        """
        Midpoint of the whole frame
        """
        return self.base_y / 2

    @property
    def design_name(self):
        """Human-readable name for the current design, e.g. 'projABC - Art piece 204x254'"""
        base = f"Art piece {self.art_piece_x:.0f}x{self.art_piece_y:.0f}"
        if self.name:
            return f"{self.name} - {base}"
        return base

    def check(self):
        art_info = f"Art piece: {self.art_piece_x:.0f} x {self.art_piece_y:.0f}"
        window_info = f"Viewing window: {self.window_x:.0f} x {self.window_y:.0f}"
        outside_info = f"Outside dimensions: {self.outside_x:.0f} x {self.outside_y:.0f}"
        frame_info = f"Frame border: {self.frame_w:.0f} x {self.frame_h:.0f}"
        back_window_info = f"Back window: {self.back_window_x:.0f} x {self.back_window_y:.0f}"
        back_frame_info = f"Back frame border (base thickness): {self.back_frame_w:.0f}"
        pocket_info = f"Pocket for art: {self.pocket_x:.0f} x {self.pocket_y:.0f} (fudge x={self.guide_fudge_x:.0f} y={self.guide_fudge_y:.0f})"

        info = [
            art_info,
            window_info,
            outside_info,
            frame_info,
            back_window_info,
            back_frame_info,
            pocket_info,
        ]

        if self.backing_enabled:
            info.append(f"Backing: {self.backing_x:.0f} x {self.backing_y:.0f} (margin={self.backing_margin:.0f})")

        issues = []

        for field in fields(self):
            if isinstance(getattr(self, field.name), float):
                v = getattr(self, field.name)
                if v < 0:
                    issues.append(f"{field.name} must be positive")

        # Check all properties
        for name, value in inspect.getmembers(self.__class__, lambda o: isinstance(o, property)):
            prop_value = getattr(self, name)
            if isinstance(prop_value, float):
                if prop_value < 0:
                    issues.append(f"{name} must be positive")

        # Validate dimensions make sense
        if self.window_x > self.outside_x:
            issues.append(f"Window width {self.window_x:.0f} cannot be larger than outside width {self.outside_x:.0f}")
        if self.window_y > self.outside_y:
            issues.append(f"Window height {self.window_y:.0f} cannot be larger than outside height {self.outside_y:.0f}")
        if self.window_x > self.art_piece_x:
            issues.append(f"Window width {self.window_x:.0f} cannot be larger than art piece width {self.art_piece_x:.0f}")
        if self.window_y > self.art_piece_y:
            issues.append(f"Window height {self.window_y:.0f} cannot be larger than art piece height {self.art_piece_y:.0f}")
        if self.back_window_x > self.outside_x:
            issues.append(f"Back window width {self.back_window_x:.0f} cannot be larger than outside width {self.outside_x:.0f}")
        if self.back_window_y > self.outside_y:
            issues.append(f"Back window height {self.back_window_y:.0f} cannot be larger than outside height {self.outside_y:.0f}")

        # Base layer window must be narrower than front layer window
        if self.back_window_x >= self.window_x:
            issues.append(
                f"Base window width {self.back_window_x:.0f} must be narrower than front window width {self.window_x:.0f}. "
                f"Increase base_thickness above {self.frame_w:.1f} (currently {self.base_thickness:.1f})"
            )
        if self.back_window_y >= self.window_y:
            issues.append(
                f"Base window height {self.back_window_y:.0f} must be narrower than front window height {self.window_y:.0f}. "
                f"Increase base_thickness above {self.frame_h:.1f} (currently {self.base_thickness:.1f})"
            )

        # Backing layer validation
        if self.backing_enabled:
            if self.backing_x <= 0:
                issues.append(f"Backing width {self.backing_x:.0f} must be positive. Decrease backing_margin (currently {self.backing_margin:.1f})")
            if self.backing_y <= 0:
                issues.append(f"Backing height {self.backing_y:.0f} must be positive. Decrease backing_margin (currently {self.backing_margin:.1f})")

        if issues:
            info_str = "\n".join(info)
            issues_str = "\n".join(issues)
            raise ValueError(f"Invalid dimensions:\n{issues_str}\n{info_str}")


class PhotoFrameSplit(Boxes):
    """
    Simplified 3-layer photo frame generator with split front and base to save material.
    """

    ui_group = "Misc"

    description = """
Photo frame generator that splits each layer into interlocking pieces to save material.

**Input dimensions:**

* **Art piece**: Total size of your art piece including any border or mat
* **Window**: Visible opening in the front layer
* **Outside**: Overall frame dimensions
* **Base thickness**: Border width of the base layer (must be wider than the front border so the base window is smaller)
* **Guide fudge x/y**: Extra clearance in the middle layer pocket for easy art insertion; vertical fudge defaults to 0 to keep alignment with the window
* **Name**: Optional label prefix for pieces (e.g. "projABC")

**Layers (front to back):**

* **Front** — 4 mitered pieces (top, bottom, left, right) forming the visible frame. Typically cut from decorative wood.
* **Middle** — 3 pieces (bottom rail + left/right sides) that create a pocket to hold the art piece. Open at the top for sliding the art in. Typically cut from MDF or draftboard.
* **Base** — 4 mitered pieces (top, bottom, left, right) with a smaller opening than the front, holding the art and middle layer in place. Typically cut from MDF or draftboard.
* **Backing** (optional) — A rectangle glued to the back of the base layer to enclose the frame. Typically cut from chipboard or similar thin stock.

**Output:** 11 pieces (+ 1 backing if enabled) plus an art piece outline with registration marks.
"""

    art_piece_x = 100
    art_piece_y = 150
    window_x = 90
    window_y = 140
    outside_x = 130
    outside_y = 180
    base_thickness = 25.0
    guide_fudge_x = 2.0
    guide_fudge_y = 0.0
    backing_enabled = False
    backing_margin = 5.0
    name = ""

    d = None

    def __init__(self) -> None:
        Boxes.__init__(self)

        self.add_arguments()

    def render(self):
        self.d = Dimensions(
            art_piece_x=self.art_piece_x,
            art_piece_y=self.art_piece_y,
            window_x=self.window_x,
            window_y=self.window_y,
            outside_x=self.outside_x,
            outside_y=self.outside_y,
            base_thickness=self.base_thickness,
            guide_fudge_x=self.guide_fudge_x,
            guide_fudge_y=self.guide_fudge_y,
            backing_enabled=self.backing_enabled,
            backing_margin=self.backing_margin,
            name=self.name,
        )

        self.render_base()
        if self.backing_enabled:
            self.render_backing()
        self.render_middle()
        self.render_front()
        self.render_photo()

        self.metadata["design_name"] = self.d.design_name

    def render_middle(self):
        """
        Render the middle layer of the frame, which creates a rectangular pocket for the art piece.
        """
        self.middle_split()

    def middle_split(self):
        lyr = "Middle"
        d = self.d
        edge_types = "DeD"
        edge_lengths = (d.guide_w, d.base_x - 2 * d.guide_w, d.guide_w)
        e = edges.CompoundEdge(self, edge_types, edge_lengths)
        move = "up"
        lbl_btm = f"{d.name} - {lyr} btm {d.base_x:.0f}x{d.guide_h:.0f}" if d.name else f"{lyr} btm {d.base_x:.0f}x{d.guide_h:.0f}"
        self.rectangularWall(d.base_x, d.guide_h, ["e", "e", e, "e"], move=move, label=lbl_btm)
        lbl_side = f"{d.name} - {lyr} side {d.guide_w:.0f}x{d.middle_side_h:.0f}" if d.name else f"{lyr} side {d.guide_w:.0f}x{d.middle_side_h:.0f}"
        self.rectangularWall(d.middle_side_h, d.guide_w, "edee", move=move, label=lbl_side)
        self.rectangularWall(d.middle_side_h, d.guide_w, "edee", move=move, label=lbl_side)

    # FRONT LAYER
    def render_front(self):
        self.front_split()

    def front_split(self):
        lyr = "Front"
        d = self.d
        hypo_h = math.sqrt(2 * d.frame_h**2)
        hypo_w = math.sqrt(2 * d.frame_w**2)

        tops = [d.base_x, 90 + 45, hypo_h, 90 - 45, d.base_x - 2 * d.frame_h, 90 - 45, hypo_h, None]
        sides = [d.base_y, 90 + 45, hypo_w, 90 - 45, d.base_y - 2 * d.frame_w, 90 - 45, hypo_w, None]

        for bit in ("top", "btm"):
            label = f"{d.name} - {lyr} {bit} {d.base_x:.0f}x{d.frame_h:.0f}" if d.name else f"{lyr} {bit} {d.base_x:.0f}x{d.frame_h:.0f}"
            self.polygonWall(tops, "eded", move="up", label=label)

        for bit in "LR":
            label = f"{d.name} - {lyr} side {bit} {d.frame_w:.0f}x{d.base_y:.0f}" if d.name else f"{lyr} side {bit} {d.frame_w:.0f}x{d.base_y:.0f}"
            self.polygonWall(sides, "eDeD", move="up", label=label)

    # BASE LAYER
    def render_base(self):
        self.base_split()

    def base_split(self):
        lyr = "Base"
        d = self.d

        # Use back_frame dimensions which are thicker to contain the art piece
        new_frame_h = d.back_frame_h
        new_frame_w = d.back_frame_w

        hypo_h = math.sqrt(2 * new_frame_h**2)
        hypo_w = math.sqrt(2 * new_frame_w**2)

        tops = [d.base_x, 90 + 45, hypo_h, 90 - 45, d.base_x - 2 * new_frame_h, 90 - 45, hypo_h, None]
        sides = [d.base_y, 90 + 45, hypo_w, 90 - 45, d.base_y - 2 * new_frame_w, 90 - 45, hypo_w, None]

        for bit in ("top", "btm"):
            label = f"{d.name} - {lyr} {bit} {d.base_x:.0f}x{new_frame_h:.0f}" if d.name else f"{lyr} {bit} {d.base_x:.0f}x{new_frame_h:.0f}"
            self.polygonWall(tops, "eded", move="up", label=label)

        for bit in "LR":
            label = f"{d.name} - {lyr} side {bit} {new_frame_w:.0f}x{d.base_y:.0f}" if d.name else f"{lyr} side {bit} {new_frame_w:.0f}x{d.base_y:.0f}"
            self.polygonWall(sides, "eDeD", move="up", label=label)

    # BACKING LAYER
    def render_backing(self):
        """
        Render the backing layer — a rectangle glued to the back of the base
        layer to enclose the frame. Inset by backing_margin on each side to
        leave room for glue around the edges.
        """
        d = self.d
        lyr = "Backing"
        label = f"{d.name} - {lyr} {d.backing_x:.0f}x{d.backing_y:.0f}" if d.name else f"{lyr} {d.backing_x:.0f}x{d.backing_y:.0f}"
        self.rectangularWall(d.backing_x, d.backing_y, "eeee", move="up", label=label)

    def photo_registration_rectangle(self):
        """
        Draw a rectangle with registration marks for the art piece.
        When used as a callback on the art piece wall, coordinates are local to that wall,
        so the centre must be (art_piece_x/2, art_piece_y/2), not the frame centre.
        """
        d = self.d
        self.set_source_color(Color.ETCHING)
        # Centre of the current wall (art piece), not the full frame
        cx = d.art_piece_x / 2.0
        cy = d.art_piece_y / 2.0
        self.rectangular_etching(cx, cy, d.art_piece_x, d.art_piece_y)
        self.ctx.stroke()

    def rectangular_etching(self, x, y, dx, dy, r=0.0, center_x=True, center_y=True):
        """
        Draw a rectangular etching (from GridfinityTrayLayout.rectangularEtching)
        Same as rectangularHole, but with no burn margin

        :param x: x position
        :param y: y position
        :param dx: width
        :param dy: height
        :param r:  (Default value = 0) radius of the corners
        :param center_x:  (Default value = True) if True, x position is the center, else the start
        :param center_y:  (Default value = True) if True, y position is the center, else the start
        """

        logger.debug(f"rectangular_etching: {x=} {y=} {dx=} {dy=} {r=} {center_x=} {center_y=}")

        r = min(r, dx / 2.0, dy / 2.0)
        x_start = x if center_x else x + dx / 2.0
        y_start = y - dy / 2.0 if center_y else y
        self.moveTo(x_start, y_start, 180)
        self.edge(dx / 2.0 - r)  # start with an edge to allow easier change of inner corners
        for d in (dy, dx, dy, dx / 2.0 + r):
            self.corner(-90, r)
            self.edge(d - 2 * r)

    def add_arguments(self):
        # landlords seem to love using 8GA screws in masonry sleeves for wall mounts
        self.addSettingsArgs(edges.MountingSettings, num=3, d_head=8.0, d_shaft=4.0)
        self.addSettingsArgs(edges.DoveTailSettings, size=2.0, depth=1.0)
        self.buildArgParser()
        self.argparser.add_argument(
            "--art_piece_x",
            action="store",
            type=float,
            default=self.art_piece_x,
            help="Width of the art piece including border content",
        )
        self.argparser.add_argument(
            "--art_piece_y",
            action="store",
            type=float,
            default=self.art_piece_y,
            help="Height of the art piece including border content",
        )
        self.argparser.add_argument(
            "--window_x",
            action="store",
            type=float,
            default=self.window_x,
            help="Width of the visible window in the front layer",
        )
        self.argparser.add_argument(
            "--window_y",
            action="store",
            type=float,
            default=self.window_y,
            help="Height of the visible window in the front layer",
        )
        self.argparser.add_argument(
            "--outside_x",
            action="store",
            type=float,
            default=self.outside_x,
            help="Total outside width of the frame",
        )
        self.argparser.add_argument(
            "--outside_y",
            action="store",
            type=float,
            default=self.outside_y,
            help="Total outside height of the frame",
        )
        self.argparser.add_argument(
            "--base_thickness",
            action="store",
            type=float,
            default=self.base_thickness,
            help="Thickness (width) of the base layer pieces. Must be larger than the front frame border to ensure the base window is narrower than the front window",
        )
        self.argparser.add_argument(
            "--guide_fudge_x",
            action="store",
            type=float,
            default=self.guide_fudge_x,
            help="Horizontal clearance in the middle layer pocket for the art piece",
        )
        self.argparser.add_argument(
            "--guide_fudge_y",
            action="store",
            type=float,
            default=self.guide_fudge_y,
            help="Vertical clearance in the middle layer pocket (0 recommended to align with window)",
        )
        self.argparser.add_argument(
            "--backing_enabled",
            action="store",
            type=boolarg,
            default=self.backing_enabled,
            help="Add a backing layer rectangle (glued to back of base to enclose the frame)",
        )
        self.argparser.add_argument(
            "--backing_margin",
            action="store",
            type=float,
            default=self.backing_margin,
            help="Inset from base layer edges for the backing rectangle (glue margin)",
        )
        self.argparser.add_argument(
            "--name",
            action="store",
            type=str,
            default=self.name,
            help="Name prefix for the design (e.g. 'projABC' yields 'projABC - Art piece 204x254')",
        )

    def render_photo(self):
        d = self.d
        self.set_source_color(Color.ANNOTATIONS)
        self.rectangularWall(
            d.art_piece_x,
            d.art_piece_y,
            "eeee",
            callback=[lambda: self.photo_registration_rectangle(), None, None, None],
            label=d.design_name,
            move="up",
        )
        self.set_source_color(Color.BLACK)
