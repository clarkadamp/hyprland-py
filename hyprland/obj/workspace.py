from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from ..socket import WorkspaceJson, command_send


@dataclass
class WorkspaceIdentity:
    key: str | None = None
    value: int | str | None = None
    identifier: str = ""

    def __post_init__(self):
        if self.key and self.value:
            self.identifier = f"{self.key}:{self.value}"
        else:
            raise AttributeError(
                "WorkspaceIdentity must have a key and value or an identifier"
            )

    @classmethod
    def from_id(cls, id: int) -> WorkspaceIdentity:
        return cls(key="id", value=id)

    @classmethod
    def from_name(cls, name: str) -> WorkspaceIdentity:
        return cls(key="name", value=name)

    @classmethod
    def from_special_name(cls, name: str) -> WorkspaceIdentity:
        return cls(key="special", value=name)

    @classmethod
    def relative_monitor(
        cls, offset: int = 0, include_empty: bool = False
    ) -> WorkspaceIdentity:
        return cls(identifier=f"{'r' if include_empty else 'm'}{offset}")

    @classmethod
    def absolute_monitor(
        cls, offset: int = 0, include_empty: bool = False
    ) -> WorkspaceIdentity:
        return cls(identifier=f"{'r' if include_empty else 'm'}~{offset}")

    @classmethod
    def relative(
        cls, offset: int = 0, include_empty: bool = False
    ) -> WorkspaceIdentity:
        return cls(identifier=f"{'r' if include_empty else 'w'}{offset}")

    @classmethod
    def absolute(
        cls, offset: int = 0, include_empty: bool = False
    ) -> WorkspaceIdentity:
        return cls(identifier=f"{'r' if include_empty else 'w'}~{offset}")

    @classmethod
    def next(cls, count: int = 1) -> WorkspaceIdentity:
        return cls(identifier=f"+{count}")

    @classmethod
    def previous(cls, count: int = 1) -> WorkspaceIdentity:
        return cls(identifier=f"-{count}")

    @classmethod
    def first_empty_monitor(cls) -> WorkspaceIdentity:
        return cls(identifier="emptym")

    @classmethod
    def first_empty(cls) -> WorkspaceIdentity:
        return cls(identifier="empty")

    @classmethod
    def next_empty_monitor(cls) -> WorkspaceIdentity:
        return cls(identifier="emptynm")

    @classmethod
    def next_empty(cls) -> WorkspaceIdentity:
        return cls(identifier="emptyn")


@dataclass
class Workspace:
    id: int
    name: str
    monitor_id: int
    windows: int
    has_fullscreen: bool = False
    last_active_window_id: str | None = None
    last_active_window_title: str | None = None

    @staticmethod
    def from_json(data: WorkspaceJson):
        return Workspace(
            id=data["id"],
            name=data["name"],
            windows=data["windows"],
            monitor_id=data["monitorID"],
            has_fullscreen=data["hasfullscreen"],
            last_active_window_id=data["lastwindow"],
            last_active_window_title=data["lastwindowtitle"],
        )

    @staticmethod
    def workspaces() -> Sequence[WorkspaceJson]:
        return cast(Sequence[WorkspaceJson] | None, command_send("workspaces")) or []

    @classmethod
    def from_id(cls, id: int) -> Workspace | None:
        for workspace in cls.workspaces():
            if id and workspace["id"] == id:
                return cls.from_json(workspace)
        return None
