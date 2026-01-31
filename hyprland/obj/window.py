from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..socket import ClientJson, monitors, workspaces

if TYPE_CHECKING:
    from .monitor import Monitor
    from .workspace import Workspace, WorkspaceIdentity


@dataclass
class WindowRule:
    rule: str

    # static rules

    @staticmethod
    def float():
        """floats a window"""
        return WindowRule("float")

    @staticmethod
    def tile():
        """tiles a window"""
        return WindowRule("tile")

    @staticmethod
    def fullscreen():
        """fullscreens a window"""
        return WindowRule("fullscreen")

    @staticmethod
    def fake_fullscreen():
        """fakefullscreens a window"""
        return WindowRule("fakefullscreen")

    @staticmethod
    def maximize():
        """maximizes a window"""
        return WindowRule("maximize")

    @staticmethod
    def move(x: str, y: str):
        """moves a floating window (x,y -> int or %, e.g. 20% or 100.
        You are also allowed to do 100%- for the right/bottom anchor, e.g. 100%-20.
        In addition, the option supports the subtraction of the window size with 100%-w-, e.g. 100%-w-20.
        This results in a gap at the right/bottom edge of the screen to the window with the defined subtracted size).
        Additionally, you can also do cursor [x] [y] where x and y are either pixels or percent.
        Percent is calculated from the window’s size.
        Specify onscreen before other parameters to force the window into the screen (e.g. move onscreen cursor 50% 50%)
        """
        return WindowRule(f"move {x} {y}")

    @staticmethod
    def size(x: str, y: str):
        """resizes a floating window (x,y -> int or %, e.g. 20% or 100)"""
        return WindowRule(f"size {x} {y}")

    @staticmethod
    def center(respect_reserved: bool = False):
        """centers a floating window"""
        return WindowRule(f"center {1 if respect_reserved else 0}")

    @staticmethod
    def pseudo():
        """pseudotiles a window"""
        return WindowRule("pseudo")

    @staticmethod
    def monitor(id: str):
        """moves a window to a specific monitor"""
        return WindowRule(f"monitor {id}")

    @staticmethod
    def workspace(w: "WorkspaceIdentity", silent: bool = False):
        """sets the workspace on which a window should open"""
        return WindowRule(f"workspace {w.identifier}{' silent' if silent else ''}")

    @staticmethod
    def unset_workspace_rules():
        """unsets the workspace rule"""
        return WindowRule("workspace unset")

    @staticmethod
    def no_focus():
        """disables focus to the window"""
        return WindowRule("nofocus")

    @staticmethod
    def no_initial_focus():
        """disables initial focus to the window"""
        return WindowRule("noinitialfocus")

    @staticmethod
    def force_input():
        """forces an XWayland window to receive input, even if it requests not to do so. (Might fix issues like e.g. Game Launchers not receiving focus for some reason)"""
        return WindowRule("forceinput")

    @staticmethod
    def window_dance():
        """orces an XWayland window to never refocus, used for games/applications like Rhythm Doctor"""
        return WindowRule("windowdance")

    @staticmethod
    def pin():
        """pins the window (i.e. show it on all workspaces) note: floating only"""
        return WindowRule("pin")

    @staticmethod
    def unset(params: str):
        """removes all previously set rules for the given parameters. Please note it has to match EXACTLY."""
        return WindowRule(f"unset {params}")

    @staticmethod
    def no_max_size():
        """removes max size limitations. Especially useful with windows that report invalid max sizes (e.g. winecfg)"""
        return WindowRule("nomaxsize")

    @staticmethod
    def stay_focused():
        """forces focus on the window as long as it’s visible"""
        return WindowRule("stayfocused")

    @staticmethod
    def group(options: str):
        """set window group properties. See the note below."""
        return WindowRule(f"group {options}")

    @staticmethod
    def suppress_events(
        fullscreen: bool = False,
        maximize: bool = False,
        activate: bool = False,
        activatefocus: bool = False,
    ):
        """ignores specific events from the window. Events are space separated, and can be: fullscreen,maximize,activate,activatefocus"""
        return WindowRule(
            f"suppress_events {','.join([x for x in [fullscreen, maximize, activate, activatefocus] if x])}"
        )

    # dynamic rules

    @staticmethod
    def opacity(
        opacity: int,
        inactive_opacity: int | None = None,
        fullscreen_opacity: int | None = None,
    ):
        """additional opacity multiplier. Options for a: float -> sets an overall opacity OR float float -> sets activeopacity and inactiveopacity respectively, OR float float float -> sets activeopacity, inactiveopacity and fullscreenopacity respectively."""
        if inactive_opacity and fullscreen_opacity:
            return WindowRule(
                f"opacity {opacity} {inactive_opacity} {fullscreen_opacity}"
            )
        elif inactive_opacity:
            return WindowRule(f"opacity {opacity} {inactive_opacity}")
        else:
            return WindowRule(f"opacity {opacity}")

    @staticmethod
    def opaque():
        """forces the window to be opaque (can be toggled with the toggleopaque dispatcher)"""
        return WindowRule("opaque")

    @staticmethod
    def force_rgbx():
        """makes Hyprland ignore the alpha channel of all the window’s surfaces, effectively making it actually, fully 100% opaque"""
        return WindowRule("forcergbx")

    @staticmethod
    def animation(style: str, opt: str | None = None):
        """orces an animation onto a window, with a selected opt. Opt is optional."""
        return WindowRule(f"animation {style}{' '+opt if opt else ''}")

    @staticmethod
    def rounding(x: int):
        """forces the application to have X pixels of rounding, ignoring the set default (in decoration:rounding). Has to be an int."""
        return WindowRule(f"rounding {x}")

    @staticmethod
    def min_size(x: int, y: int):
        """sets the minimum size (x,y -> int)"""
        return WindowRule(f"minsize {x} {y}")

    @staticmethod
    def max_size(x: int, y: int):
        """sets the maximum size (x,y -> int)"""
        return WindowRule(f"maxsize {x} {y}")

    @staticmethod
    def no_blur():
        """disables blur for the window"""
        return WindowRule("noblur")

    @staticmethod
    def no_border():
        """disables borders for the window"""
        return WindowRule("noborder")

    @staticmethod
    def border_size(x: int):
        """sets the border"""
        return WindowRule(f"bordersize {x}")

    @staticmethod
    def no_dim():
        """disables window dimming for the window"""
        return WindowRule("nodim")

    @staticmethod
    def no_shadow():
        """disables shadow for the window"""
        return WindowRule("noshadow")

    @staticmethod
    def no_animations():
        """disables animations for the window"""
        return WindowRule("noanimations")

    @staticmethod
    def keep_aspect_ratio():
        """forces aspect ratio when resizing window with the mouse"""
        return WindowRule("keepaspectratio")

    @staticmethod
    def focus_on_activate(focus: bool):
        """whether Hyprland should focus an app that requests to be focused (an activate request)"""
        return WindowRule(f"focusonactivate {int(focus)}")

    @staticmethod
    def border_color(color: str):
        """sets the border color"""
        return WindowRule(f"bordercolor {color}")

    @staticmethod
    def idle_inhibit(mode: str):
        """sets an idle inhibit rule for the window. If active, apps like hypridle will not fire. Modes: none, always, focus, fullscreen"""
        return WindowRule(f"idleinhibit {mode}")

    @staticmethod
    def dim_around():
        """dims everything around the window . Please note this rule is meant for floating windows and using it on tiled ones may result in strange behavior."""
        return WindowRule("dimaround")

    @staticmethod
    def xray(enabled: bool):
        """sets blur xray mode for the window"""
        return WindowRule(f"xray {int(enabled)}")

    @staticmethod
    def xray_unset():
        """unsets xray mode for the window"""
        return WindowRule("xray unset")

    @staticmethod
    def immediate():
        """forces the window to allow to be torn."""
        return WindowRule("immediate")

    @staticmethod
    def nearest_neighbor():
        """forces the window to use the nearest neigbor filtering."""
        return WindowRule("nearestneighbor")


@dataclass
class WindowIdentity:
    key: str | None = None
    value: int | str | None = None
    identifier: str = ""

    def __post_init__(self) -> None:
        if self.key and self.value:
            self.identifier = f"{self.key}:{self.value}"
        elif self.identifier:
            self.key, self.value = self.identifier.split(":")
        else:
            raise AttributeError(
                "WindowIdentity must have a key and value or an identifier"
            )

    @classmethod
    def from_window(cls, window: Window) -> WindowIdentity:
        return cls(key="address", value=window.address)

    @classmethod
    def from_address(cls, address: int) -> WindowIdentity:
        return cls(key="address", value=address)

    @classmethod
    def from_title(cls, title: str) -> WindowIdentity:
        return cls(key="title", value=title)

    @classmethod
    def from_class_name(cls, class_name: str) -> WindowIdentity:
        return cls(key="class", value=class_name)

    @classmethod
    def from_pid(cls, pid: int) -> WindowIdentity:
        return cls(key="pid", value=pid)


@dataclass
class Window:
    address: str
    mapped: bool
    hidden: bool
    at: tuple[int, int]
    size: tuple[int, int]
    workspace_id: int
    workspace_name: str
    floating: bool
    monitor_id: int
    class_name: str
    title: str
    initial_class_name: str
    initial_title: str
    pid: int
    xwayland: bool
    fullscreen: bool
    fullscreen_client: int
    grouped: Sequence[str]
    swallowing: int
    focus_history_id: int

    def fetch_workspace(self) -> Workspace | None:
        for workspace in workspaces():
            if workspace["id"] == self.workspace_id:
                return Workspace.from_json(workspace)
        return None

    def fetch_monitor(self) -> Monitor | None:
        for monitor in monitors():
            if monitor["id"] == self.monitor_id:
                return Monitor.from_json(monitor)
        return None

    def fetch_decorations(self): ...

    def identifier(self) -> "WindowIdentity":
        return WindowIdentity.from_window(self)

    @staticmethod
    def from_json(data: ClientJson):
        return Window(
            address=data["address"],
            mapped=data["mapped"],
            hidden=data["hidden"],
            at=data["at"],
            size=data["size"],
            workspace_id=data["workspace"]["id"],
            workspace_name=data["workspace"]["name"],
            floating=data["floating"],
            monitor_id=data["monitor"],
            class_name=data["class"],
            title=data["title"],
            initial_class_name=data["initialClass"],
            initial_title=data["initialTitle"],
            pid=data["pid"],
            xwayland=data["xwayland"],
            fullscreen=bool(data["fullscreen"]),
            fullscreen_client=data["fullscreenClient"],
            grouped=data["grouped"],
            swallowing=data["swallowing"],
            focus_history_id=data["focusHistoryID"],
        )
