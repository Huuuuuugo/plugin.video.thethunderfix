#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cache_manager.py - plugin.video.thethunder
- Limpa arquivos de cache e mostra notificação.
- Mostra o tamanho atual do cache.
- Funciona dentro e fora do Kodi.
"""

import sys
import os

try:
    import xbmc
    import xbmcgui
    import xbmcvfs
    import xbmcaddon
except ImportError:
    xbmc = xbmcgui = xbmcvfs = xbmcaddon = None


# --- Utilidades ---
def is_kodi():
    return xbmc is not None and xbmcgui is not None


def notify(title, message, duration=3000):
    try:
        if is_kodi():
            xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, duration)
        else:
            print(f"[{title}] {message}")
    except Exception:
        print(f"[{title}] {message}")


def log(msg):
    try:
        if is_kodi():
            xbmc.log(f"[thethunder][cache_manager] {msg}", xbmc.LOGINFO)
        else:
            print(f"[thethunder][cache_manager] {msg}")
    except Exception:
        print(f"[thethunder][cache_manager] {msg}")


# --- Diretório de Cache ---
def get_cache_dir():
    """Retorna diretório de cache do thethunder (Kodi ou standalone)."""
    if is_kodi():
        try:
            addon = xbmcaddon.Addon("plugin.video.thethunder")
            profile_dir = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
            return os.path.join(profile_dir, "cache")
        except Exception:
            pass

    # Fallback fora do Kodi
    if os.name == "nt":  # Windows
        base = os.getenv("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":  # macOS
        base = os.path.expanduser("~/Library/Caches")
    else:  # Linux / Android
        base = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

    return os.path.join(base, "thethunder", "cache")


def ensure_dir(path):
    try:
        if is_kodi() and xbmcvfs:
            if not xbmcvfs.exists(path):
                xbmcvfs.mkdirs(path)
        else:
            os.makedirs(path, exist_ok=True)
    except Exception as e:
        log(f"Erro ao criar diretório: {e}")


# --- Operações de Cache ---
def _list_cache_files(path):
    files = []
    try:
        if is_kodi() and xbmcvfs:
            _, listing = xbmcvfs.listdir(path)
            files = [os.path.join(path, entry) for entry in listing]
        else:
            for root, _, filenames in os.walk(path):
                for name in filenames:
                    files.append(os.path.join(root, name))
    except Exception as e:
        log(f"Erro ao listar cache: {e}")
    return files


def _delete_file(filepath):
    try:
        if is_kodi() and xbmcvfs:
            if xbmcvfs.exists(filepath):
                xbmcvfs.delete(filepath)
        else:
            if os.path.exists(filepath):
                os.remove(filepath)
    except Exception as e:
        log(f"Erro ao deletar {filepath}: {e}")


def clear_cache():
    cache_dir = get_cache_dir()
    ensure_dir(cache_dir)

    files = _list_cache_files(cache_dir)
    count = 0
    for fpath in files:
        _delete_file(fpath)
        count += 1

    notify("TheThunder", f"Cache limpo ({count} arquivos removidos)")
    log(f"Cache limpo ({count} arquivos)")


# --- Medição de tamanho ---
def human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"


def get_cache_size_local():
    total_size = 0
    cache_dir = get_cache_dir()
    if is_kodi() and xbmcvfs and xbmcvfs.exists(cache_dir):
        _, files = xbmcvfs.listdir(cache_dir)
        for file in files:
            try:
                fpath = os.path.join(cache_dir, file)
                stat = xbmcvfs.Stat(fpath)
                total_size += stat.st_size()
            except Exception:
                pass
    else:
        for root, _, files in os.walk(cache_dir):
            for file in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, file))
                except Exception:
                    pass
    return total_size


def show_cache():
    size = get_cache_size_local()
    size_str = human_readable_size(size)
    notify("TheThunder", f"Tamanho atual do cache: {size_str}", 4000)
    log(f"Tamanho atual do cache: {size_str}")


# --- Execução via RunScript ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("clear_cache", "--clear-cache", "-c"):
            clear_cache()
        elif arg in ("show_cache", "--show-cache", "-s"):
            show_cache()
    else:
        clear_cache()