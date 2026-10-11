# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_NAME = ADDON.getAddonInfo("name")
ADDON_VERSION = ADDON.getAddonInfo("version")
HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else 1

# TODO: replace this with your real manifest endpoint
MANIFEST_URL = "https://thokodi.github.io/builds/manifest.json"


def log(message: str, level=xbmc.LOGINFO) -> None:
    xbmc.log(f"[{ADDON_ID}] {message}", level)


def notify(title: str, message: str, level=xbmcgui.NOTIFICATION_INFO) -> None:
    xbmcgui.Dialog().notification(title, message, level, 5000)


def build_url(**query) -> str:
    return sys.argv[0] + "?" + urllib.parse.urlencode(query)


def parse_params() -> dict:
    if len(sys.argv) < 3 or not sys.argv[2]:
        return {}
    query = sys.argv[2][1:] if sys.argv[2].startswith("?") else sys.argv[2]
    return dict(urllib.parse.parse_qsl(query))


def open_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Kodi"})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read()
    return data.decode("utf-8", errors="replace") if isinstance(data, bytes) else data


def add_item(label: str, action: str, folder: bool = True, art: dict | None = None, info: dict | None = None, **params) -> None:
    li = xbmcgui.ListItem(label=label)

    if art:
        li.setArt(art)

    if info:
        vtag = li.getVideoInfoTag()
        if info.get("title"):
            vtag.setTitle(info["title"])
        if info.get("plot"):
            vtag.setPlot(info["plot"])

    xbmcplugin.addDirectoryItem(HANDLE, build_url(action=action, **params), li, isFolder=folder)


def render_main_menu() -> None:
    add_item(
        label="Available builds",
        action="list_builds",
        folder=True,
        art={
            "icon": ADDON.getAddonInfo("icon"),
            "thumb": ADDON.getAddonInfo("icon"),
            "fanart": ADDON.getAddonInfo("fanart"),
        },
    )
    xbmcplugin.setContent(HANDLE, "files")
    xbmcplugin.endOfDirectory(HANDLE)


def load_manifest() -> dict:
    raw = open_url(MANIFEST_URL)
    return json.loads(raw)


def render_build_list() -> None:
    try:
        manifest = load_manifest()
    except Exception as exc:
        log(f"Failed to load manifest: {exc}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok(ADDON_NAME, "Failed to load build manifest.", str(exc))
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    builds = manifest.get("builds", [])
    if not builds:
        xbmcgui.Dialog().ok(ADDON_NAME, "No builds found in the manifest.")
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    for build in builds:
        label = build.get("name", "Unnamed build")
        add_item(
            label=label,
            action="install_build",
            folder=False,
            art={
                "icon": build.get("icon", ADDON.getAddonInfo("icon")),
                "thumb": build.get("icon", ADDON.getAddonInfo("icon")),
                "fanart": build.get("fanart", ADDON.getAddonInfo("fanart")),
            },
            info={
                "title": label,
                "plot": build.get("description", ""),
            },
            name=label,
            url=build.get("url", ""),
            checksum=build.get("checksum", ""),
        )

    xbmcplugin.setContent(HANDLE, "files")
    xbmcplugin.endOfDirectory(HANDLE)


def verify_checksum(local_path: Path, expected: str) -> bool:
    """
    Expected checksum format examples:
      - sha256:abcdef...
      - md5:abcdef...
    """
    if not expected:
        return True

    if ":" in expected:
        algo, expected_hash = expected.split(":", 1)
    else:
        algo, expected_hash = "sha256", expected

    algo = algo.lower().strip()
    expected_hash = expected_hash.strip().lower()

    if algo not in {"md5", "sha1", "sha256"}:
        raise ValueError(f"Unsupported checksum algorithm: {algo}")

    import hashlib

    h = hashlib.new(algo)
    with local_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest().lower() == expected_hash


def safe_extract_zip(zip_path: Path, destination: Path) -> None:
    import zipfile

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = (destination / member.filename).resolve()
            if not str(member_path).startswith(str(destination.resolve())):
                raise ValueError(f"Blocked unsafe zip entry: {member.filename}")
        zf.extractall(destination)


def install_build(url: str, checksum: str, name: str) -> None:
    if not url:
        xbmcgui.Dialog().ok(ADDON_NAME, "Missing build URL.")
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        return

    dialog = xbmcgui.DialogProgress()
    dialog.create(ADDON_NAME, f"Downloading {name}...")

    temp_dir = Path(tempfile.mkdtemp(prefix="thokodi_"))
    zip_path = temp_dir / "build.zip"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Kodi"})
        with urllib.request.urlopen(req, timeout=60) as response, zip_path.open("wb") as out:
            total = response.headers.get("Content-Length")
            total = int(total) if total and total.isdigit() else 0
            downloaded = 0

            while True:
                chunk = response.read(1024 * 64)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)

                percent = int((downloaded / total) * 100) if total else 0
                dialog.update(percent, f"Downloading {name}...", f"{downloaded} bytes")

                if dialog.iscanceled():
                    raise Exception("Download canceled")

        if checksum and not verify_checksum(zip_path, checksum):
            raise ValueError("Checksum verification failed")

        dialog.update(0, f"Installing {name}...")

        # Install into a controlled location, not blindly over special://home.
        # If you need a different target, adjust this path intentionally.
        install_target = Path(xbmcvfs.translatePath("special://home/addons"))
        safe_extract_zip(zip_path, install_target)

        dialog.close()
        xbmcgui.Dialog().ok(
            ADDON_NAME,
            f"{name} downloaded and installed.",
            "Please restart Kodi if the new files do not appear immediately.",
        )
        xbmc.executebuiltin("Container.Refresh")
    except Exception as exc:
        dialog.close()
        log(f"Install failed: {exc}", xbmc.LOGERROR)
        xbmcgui.Dialog().ok(ADDON_NAME, "Installation failed.", str(exc))
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
    finally:
        try:
            zip_path.unlink(missing_ok=True)
        except Exception:
            pass
        try:
            temp_dir.rmdir()
        except Exception:
            pass


def router() -> None:
    params = parse_params()
    action = params.get("action")

    log(f"version={ADDON_VERSION}, action={action}, params={params}")

    if not action:
        render_main_menu()
    elif action == "list_builds":
        render_build_list()
    elif action == "install_build":
        install_build(
            url=params.get("url", ""),
            checksum=params.get("checksum", ""),
            name=params.get("name", "build"),
        )
    else:
        xbmcgui.Dialog().ok(ADDON_NAME, f"Unknown action: {action}")
        xbmcplugin.endOfDirectory(HANDLE, succeeded=False)


if __name__ == "__main__":
    router()
