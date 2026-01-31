import asyncio
import json
import os
import socket
from collections.abc import Sequence
from typing import TypedDict, cast


class UnknownRequest(Exception):
    """
    An unknown request
    """


ClientJson = TypedDict(
    "ClientJson",
    {
        "address": str,
        "mapped": bool,
        "hidden": bool,
        "at": tuple[int, int],
        "size": tuple[int, int],
        "workspace": "WorkspaceIdJson",
        "floating": bool,
        "psuedo": bool,
        "monitor": int,
        "class": str,
        "title": str,
        "initialClass": str,
        "initialTitle": str,
        "pid": int,
        "xwayland": bool,
        "pinned": bool,
        "fullscreen": int,
        "fullscreenClient": int,
        "grouped": Sequence[str],
        "tags": Sequence[str],
        "swallowing": int,
        "focusHistoryID": int,
        "inhibitingIdle": bool,
        "xdgTag": str,
        "xdgDescription": str,
    },
)


class WorkspaceIdJson(TypedDict):
    id: int
    name: str


class MonitorJson(TypedDict):
    id: int
    name: str
    description: str
    make: str
    model: str
    serial: str
    width: int
    height: int
    physicalWidth: int
    physicalHeight: int
    refreshRate: float
    x: int
    y: int
    activeWorkspace: WorkspaceIdJson
    specialWorkspace: WorkspaceIdJson
    reserved: Sequence[int]
    scale: float
    transform: int
    focused: bool
    dpmsStatus: bool
    vrr: bool
    solitary: str
    solitaryBlockedBy: Sequence[str]
    activelyTearing: bool
    tearingBlockedBy: Sequence[str]
    directScanoutTo: str
    directScanoutBlockedBy: Sequence[str]
    disabled: bool
    currentFormat: str
    mirrorOf: str
    availableModes: Sequence[str]
    colorManagementPreset: str
    sdrBrightness: float
    sdrSaturation: float
    sdrMinLuminance: float
    sdrMaxLuminance: int


class WorkspaceJson(TypedDict):
    id: int
    name: str
    monitor: str
    monitorID: int
    windows: int
    hasfullscreen: bool
    lastwindow: str
    lastwindowtitle: str
    ispersistent: bool


InfoReturnTypes = ClientJson | MonitorJson | WorkspaceJson


def workspaces() -> Sequence[WorkspaceJson]:
    return cast(Sequence[WorkspaceJson], command_send("workspaces")) or []


def monitors() -> Sequence[MonitorJson]:
    return cast(Sequence[MonitorJson], command_send("monitors all")) or []


def command_send(
    cmd: str, return_json: bool = True, check_ok: bool = False
) -> str | bool | InfoReturnTypes | None:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(
            f"{os.getenv('XDG_RUNTIME_DIR')}/hypr/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE')}/.socket.sock"
        )
        if return_json:
            cmd = f"[j]/{cmd}"
        _ = sock.send(cmd.encode())
        resp = sock.recv(8192)

        while True:
            new_data = sock.recv(8192)
            if not new_data:
                break
            resp += new_data

        match resp:
            case b"ok" if check_ok:
                return True
            case b"unknown request":
                raise UnknownRequest(f"{cmd.encode()!r} : {resp}")
            case _:

                if check_ok and resp != b"ok":
                    raise Exception(
                        f"Command failed: {cmd.encode()!r} : {resp.decode('utf-8')}"
                    )

                if return_json and not check_ok:
                    return cast(InfoReturnTypes, json.loads(resp.decode()))

                return resp.decode()


async def async_command_send(
    cmd: str, return_json: bool = True
) -> str | InfoReturnTypes:
    reader, writer = await asyncio.open_unix_connection(
        f"{os.getenv('XDG_RUNTIME_DIR')}/hypr/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE')}/.socket.sock"
    )
    if return_json:
        cmd = f"[j]/{cmd}"
    writer.write(cmd.encode())
    await writer.drain()
    resp = await reader.read(8192)

    while True:
        new_data = await reader.read(8192)
        if not new_data:
            break
        resp += new_data

    writer.close()

    match resp:
        case b"unknown request":
            raise UnknownRequest(f"{cmd.encode()!r} : {resp.decode('utf-8')}")
        case _:
            if return_json:
                return cast(InfoReturnTypes, json.loads(resp.decode()))
            return resp.decode()


class EventListener:
    async def start(self):
        reader, _ = await asyncio.open_unix_connection(
            f"{os.getenv('XDG_RUNTIME_DIR')}/hypr/{os.getenv('HYPRLAND_INSTANCE_SIGNATURE')}/.socket2.sock"
        )
        yield "connect"

        buffer = b""
        while True:
            new_data = await reader.read(8192)
            if not new_data:
                break
            buffer += new_data
            while b"\n" in buffer:
                data, buffer = buffer.split(b"\n", 1)
                yield data.decode("utf-8")
