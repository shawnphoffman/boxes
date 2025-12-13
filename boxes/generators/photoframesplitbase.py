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

from boxes import BoolArg, Boxes, Color, edges

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
    frame_overlap: float
    split_front_param: bool
    split_middle_param: bool
    split_base_param: bool
    guide_fudge: float = 2.0

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
    def back_window_x(self):
        """Width of the window in the back/base layer (reduced to contain art piece)"""
        return self.art_piece_x - 2 * self.frame_overlap

    @property
    def back_window_y(self):
        """Height of the window in the back/base layer (reduced to contain art piece)"""
        return self.art_piece_y - 2 * self.frame_overlap

    @property
    def back_frame_w(self):
        """Width of the frame border on sides for back/base layer"""
        return (self.outside_x - self.back_window_x) / 2

    @property
    def back_frame_h(self):
        """Height of the frame border on top/bottom for back/base layer"""
        return (self.outside_y - self.back_window_y) / 2

    @property
    def pocket_x(self):
        """Width of the pocket in middle layer for art piece"""
        return self.art_piece_x + self.guide_fudge

    @property
    def pocket_y(self):
        """Height of the pocket in middle layer for art piece"""
        return self.art_piece_y + self.guide_fudge

    @property
    def guide_w(self):
        """Width of the guide walls in middle layer"""
        return (self.outside_x - self.pocket_x) / 2

    @property
    def guide_h(self):
        """Height of the guide walls in middle layer"""
        return (self.outside_y - self.pocket_y) / 2

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
    def split_base(self):
        return self.split_base_param

    @property
    def unsplit_base(self):
        return not self.split_base_param

    @property
    def split_middle(self):
        return self.split_middle_param

    @property
    def unsplit_middle(self):
        return not self.split_middle_param

    @property
    def split_front(self):
        return self.split_front_param

    @property
    def unsplit_front(self):
        return not self.split_front_param

    def check(self):
        art_info = f"Art piece: {self.art_piece_x:.0f} x {self.art_piece_y:.0f}"
        window_info = f"Viewing window: {self.window_x:.0f} x {self.window_y:.0f}"
        outside_info = f"Outside dimensions: {self.outside_x:.0f} x {self.outside_y:.0f}"
        frame_info = f"Frame border: {self.frame_w:.0f} x {self.frame_h:.0f}"
        back_window_info = f"Back window: {self.back_window_x:.0f} x {self.back_window_y:.0f}"
        back_frame_info = f"Back frame border: {self.back_frame_w:.0f} x {self.back_frame_h:.0f}"
        pocket_info = f"Pocket for art: {self.pocket_x:.0f} x {self.pocket_y:.0f} (fudge {self.guide_fudge:.0f})"

        info = [
            art_info,
            window_info,
            outside_info,
            frame_info,
            back_window_info,
            back_frame_info,
            pocket_info,
        ]

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
        if self.back_window_x > self.outside_x:
            issues.append(f"Back window width {self.back_window_x:.0f} cannot be larger than outside width {self.outside_x:.0f}")
        if self.back_window_y > self.outside_y:
            issues.append(f"Back window height {self.back_window_y:.0f} cannot be larger than outside height {self.outside_y:.0f}")

        if issues:
            info_str = "\n".join(info)
            issues_str = "\n".join(issues)
            raise ValueError(f"Invalid dimensions:\n{issues_str}\n{info_str}")


class PhotoFrameSplit(Boxes):
    """
    Simplified 3-layer photo frame generator.
    """

    ui_group = "Misc"

    description = """
Simplified photo frame generator.

This generator creates a 3-layer photo frame with simplified measurements:

* **Art piece dimensions**: Total size of your art piece including any border content
* **Window dimensions**: Size of the visible window in the front layer (what shows through)
* **Outside dimensions**: Total outside size of the frame

The frame consists of:
* **Front layer**: Has a window cutout showing your artwork. Can be split into puzzle pieces to save material.
* **Middle layer**: Creates a rectangular pocket to hold the art piece in place.
* **Back/base layer**: Has a smaller window than the front to ensure the art piece is contained. Can be split to save material.

Features:
* Split front and base layers into thin rectangles to save material
* Middle layer creates a pocket for the art piece
* Adds holes for hanging the frame on the wall
"""

    art_piece_x = 100
    art_piece_y = 150
    window_x = 90
    window_y = 140
    outside_x = 130
    outside_y = 180
    frame_overlap = 5.0
    split_base = False
    split_middle = True  # not exposed in the UI
    split_front = True
    mount_hole_dia = 6.0
    guide_fudge = 2.0

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
            frame_overlap=self.frame_overlap,
            split_base_param=self.split_base,
            split_middle_param=self.split_middle,
            split_front_param=self.split_front,
            guide_fudge=self.guide_fudge,
        )

        self.render_base()
        self.render_middle()
        self.render_front()
        self.render_photo()

    def render_middle(self):
        """
        Render the middle layer of the frame, which creates a rectangular pocket for the art piece.
        """

        stack_n = 1

        if self.d.unsplit_middle:
            for _ in range(stack_n):
                self.middle_unsplit()

        if self.d.split_middle:
            for _ in range(stack_n):
                self.middle_split()

    def middle_split(self):
        lyr = "Middle"
        d = self.d
        edge_types = "DeD"
        edge_lengths = (d.guide_w, d.base_x - 2 * d.guide_w, d.guide_w)
        e = edges.CompoundEdge(self, edge_types, edge_lengths)
        move = "up"
        self.rectangularWall(d.base_x, d.guide_h, ["e", "e", e, "e"], move=move, label=f"{lyr} btm {d.base_x:.0f}x{d.guide_h:.0f}")
        self.rectangularWall(d.pocket_y, d.guide_w, "edee", move=move, label=f"{lyr} side {d.guide_w:.0f}x{d.pocket_y:.0f}")
        self.rectangularWall(d.pocket_y, d.guide_w, "edee", move=move, label=f"{lyr} side {d.guide_w:.0f}x{d.pocket_y:.0f}")

    def middle_unsplit(self):
        lyr = "Middle"
        d = self.d
        dims_str = f"{lyr} {d.base_x:.0f}x{d.base_y:.0f} with pocket {d.pocket_x:.0f}x{d.pocket_y:.0f} for art {d.art_piece_x:.0f}x{d.art_piece_y:.0f}"
        border_str = f"Widths {d.guide_w:.0f}x {d.guide_h:.0f}y fudge {d.guide_fudge:.0f}"
        label = f"{dims_str}\n{border_str}"

        # start at bottom left
        poly = [d.base_x, 90, d.base_y, 90, d.guide_w, 90, d.pocket_y, -90, d.pocket_x, -90, d.pocket_y, 90, d.guide_w, 90, d.base_y, 90]
        self.polygonWall(poly, "eeee", move="up", label=label)

    # FRONT LAYER
    def render_front(self):
        if self.d.unsplit_front:
            self.front_unsplit()

        if self.d.split_front:
            self.front_split()

    def front_unsplit(self):
        lyr = "Front"
        d = self.d
        dims_str = f"{lyr} {d.base_x:.0f}x{d.base_y:.0f} - {d.window_x:.0f}x{d.window_y:.0f}"
        border_str = f"Widths {d.frame_w:.0f}x {d.frame_h:.0f}y {d.frame_overlap:.0f} overlap"
        label = f"{dims_str}\n{border_str}"

        callback = [lambda: self.rectangularHole(d.centre_x, d.centre_y, d.window_x, d.window_y)]
        self.rectangularWall(d.base_x, d.base_y, "eeee", callback=callback, move="up", label=label)

    def front_split(self):
        lyr = "Front"
        d = self.d
        hypo_h = math.sqrt(2 * d.frame_h**2)
        hypo_w = math.sqrt(2 * d.frame_w**2)

        tops = [d.base_x, 90 + 45, hypo_h, 90 - 45, d.base_x - 2 * d.frame_h, 90 - 45, hypo_h, None]
        sides = [d.base_y, 90 + 45, hypo_w, 90 - 45, d.base_y - 2 * d.frame_w, 90 - 45, hypo_w, None]

        for bit in ("top", "btm"):
            label = f"{lyr} {bit} {d.base_x:.0f}x{d.frame_h:.0f}"
            self.polygonWall(tops, "eded", move="up", label=label)

        for bit in "LR":
            label = f"{lyr} side {bit} {d.frame_w:.0f}x{d.base_y:.0f}"
            self.polygonWall(sides, "eDeD", move="up", label=label)

    # BASE LAYER
    def render_base(self):
        if self.d.unsplit_base:
            self.base_unsplit()

        if self.d.split_base:
            self.base_split()

    def base_split(self):
        lyr = "Base"
        d = self.d
        label = f"{lyr} (split) {d.base_x:.0f}x{d.base_y:.0f} for art {d.art_piece_x:.0f}x{d.art_piece_y:.0f}"

        # Use back_frame dimensions which are thicker to contain the art piece
        new_frame_h = d.back_frame_h
        new_frame_w = d.back_frame_w

        hypo_h = math.sqrt(2 * new_frame_h**2)
        hypo_w = math.sqrt(2 * new_frame_w**2)

        tops = [d.base_x, 90 + 45, hypo_h, 90 - 45, d.base_x - 2 * new_frame_h, 90 - 45, hypo_h, None]
        sides = [d.base_y, 90 + 45, hypo_w, 90 - 45, d.base_y - 2 * new_frame_w, 90 - 45, hypo_w, None]

        for bit in ("top", "btm"):
            label = f"{lyr} {bit} {d.base_x:.0f}x{new_frame_h:.0f}"
            self.polygonWall(tops, "eded", move="up", label=label)

        for bit in "LR":
            label = f"{lyr} side {bit} {new_frame_w:.0f}x{d.base_y:.0f}"
            self.polygonWall(sides, "eDeD", move="up", label=label)

    def base_unsplit(self):
        d = self.d
        label = f"Base {d.base_x:.0f}x{d.base_y:.0f} for art {d.art_piece_x:.0f}x{d.art_piece_y:.0f}"

        callback = [lambda: self.photo_registration_rectangle(), None, None, None]
        holes = self.edgesettings.get("Mounting", {}).get("num", 0)
        self.rectangularWall(d.base_x, d.base_y, "eeGe" if holes else "eeee", callback=callback, move="up", label=label)

        # I can't work out the interface for roundedPlate with edge settings other than "e"
        # so no rounded corners for you!
        # self.roundedPlate(d.base_x, d.base_y, d.corner_radius, "e", callback, extend_corners=False, move="up", label=label)

    def photo_registration_rectangle(self):
        """
        Draw a rectangle with registration marks for the art piece
        """

        d = self.d
        self.set_source_color(Color.ETCHING)
        self.rectangular_etching(d.centre_x, d.centre_y, d.art_piece_x, d.art_piece_y)
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
            "--frame_overlap",
            action="store",
            type=float,
            default=self.frame_overlap,
            help="Frame overlap for back window reduction to contain art piece",
        )
        self.argparser.add_argument(
            "--guide_fudge",
            action="store",
            type=float,
            default=self.guide_fudge,
            help="Clearance in the middle layer pocket for the art piece",
        )
        self.argparser.add_argument(
            "--split_front",
            action="store",
            type=BoolArg(),
            default=self.split_front,
            help="Split front into thin rectangles to save material",
        )
        # self.argparser.add_argument(
        #     "--split_middle",
        #     action="store",
        #     type=BoolArg(),
        #     default=self.split_middle,
        #     help="Split middle into thin rectangles to save material",
        # )
        self.argparser.add_argument(
            "--split_base",
            action="store",
            type=BoolArg(),
            default=self.split_base,
            help="Split base into thin rectangles to save material",
        )

    def render_photo(self):
        d = self.d
        self.set_source_color(Color.ANNOTATIONS)
        label = f"Art piece {d.art_piece_x:.0f}x{d.art_piece_y:.0f}"
        self.rectangularWall(d.art_piece_x, d.art_piece_y, "eeee", label=label, move="up")
        self.set_source_color(Color.BLACK)
