import hashlib
import json
import os
import sys
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

import downloader
import extract

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
MANIFEST_URL = 'https://thokodi.github.io/repo/builds.json'
USER_AGENT = 'Kodi/%s %s' % (xbmc.getInfoLabel('System.BuildVersion').split(' ')[0], ADDON_ID)


def log(message, level=xbmc.LOGINFO):
    xbmc.log('[%s] %s' % (ADDON_ID, message), level)


def show_error(message):
    log(message, xbmc.LOGERROR)
    xbmcgui.Dialog().ok(ADDON_NAME, message)


def build_url(base_url, **query):
    return base_url + '?' + urllib.parse.urlencode(query)


def parse_params(paramstring):
    return dict(urllib.parse.parse_qsl(paramstring.lstrip('?')))


def load_manifest():
    req = urllib.request.Request(MANIFEST_URL, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode('utf-8'))
    builds = data.get('builds', []) if isinstance(data, dict) else []
    return [b for b in builds if isinstance(b, dict) and b.get('name') and b.get('url')]


def list_menu(handle, base_url):
    try:
        builds = load_manifest()
    except Exception as exc:
        log('Failed to load manifest: %s' % exc, xbmc.LOGERROR)
        xbmcgui.Dialog().ok(ADDON_NAME, 'Unable to load the build list.\n%s' % exc)
        xbmcplugin.endOfDirectory(handle, succeeded=False)
        return

    for index, build in enumerate(builds):
        item = xbmcgui.ListItem(label=build['name'])
        icon = build.get('icon') or ADDON.getAddonInfo('icon')
        fanart = build.get('fanart') or ADDON.getAddonInfo('fanart')
        item.setArt({'icon': icon, 'thumb': icon, 'fanart': fanart})
        tag = item.getVideoInfoTag()
        tag.setTitle(build['name'])
        tag.setPlot(build.get('description', ''))
        xbmcplugin.addDirectoryItem(handle, build_url(base_url, action='install', index=index),
                                    item, isFolder=False)
    xbmcplugin.setContent(handle, 'files')
    xbmcplugin.endOfDirectory(handle)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def install_build(params):
    try:
        build = load_manifest()[int(params.get('index', -1))]
    except Exception as exc:
        show_error('Unable to find the selected build.\n%s' % exc)
        return

    name = build['name']
    if not xbmcgui.Dialog().yesno(ADDON_NAME, 'Install "%s"?\nThis will overwrite files in your Kodi profile.' % name):
        return

    packages = xbmcvfs.translatePath('special://home/addons/packages')
    home = xbmcvfs.translatePath('special://home')
    os.makedirs(packages, exist_ok=True)
    archive = os.path.join(packages, 'thokodi_build.zip')

    progress = xbmcgui.DialogProgress()
    progress.create(ADDON_NAME, 'Downloading...')
    try:
        downloader.download(build['url'], archive, progress)
        expected = (build.get('sha256') or '').lower()
        if expected and sha256_of(archive) != expected:
            raise ValueError('Checksum mismatch, download discarded.')
        progress.update(0, 'Extracting files...')
        if not extract.all(archive, home, progress):
            raise ValueError('Extraction failed.')
    except Exception as exc:
        progress.close()
        show_error('Install failed: %s' % exc)
        return
    finally:
        progress.close()
        if os.path.exists(archive):
            os.remove(archive)

    log('Installed build %s' % name)
    xbmcgui.Dialog().ok(ADDON_NAME, 'Install complete.\nPlease restart Kodi manually to apply the build.')


def router(argv):
    base_url = argv[0]
    handle = int(argv[1])
    params = parse_params(argv[2] if len(argv) > 2 else '')
    action = params.get('action')
    log('action=%s' % action, xbmc.LOGDEBUG)

    if action == 'install':
        install_build(params)
        xbmcplugin.endOfDirectory(handle, succeeded=False)
    else:
        list_menu(handle, base_url)


if __name__ == '__main__':
    router(sys.argv)
