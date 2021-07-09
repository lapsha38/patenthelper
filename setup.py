import os, site, sys
from cx_Freeze import setup, Executable

assert sys.platform == "win32"

common_include_files = [
"ui.glade",
"icon.png"
]

required_dll_search_paths = os.getenv("PATH", os.defpath).split(os.pathsep)
required_dlls = [
    'libgtk-3-0.dll',
    'libgdk-3-0.dll',
    'libepoxy-0.dll',
    'libgdk_pixbuf-2.0-0.dll',
    'libpango-1.0-0.dll',
    'libpangocairo-1.0-0.dll',
    'libpangoft2-1.0-0.dll',
    'libpangowin32-1.0-0.dll',
    'libatk-1.0-0.dll',
]

for dll in required_dlls:
    dll_path = None
    for p in required_dll_search_paths:
        p = os.path.join(p, dll)
        if os.path.isfile(p):
            dll_path = p
            break
    assert dll_path is not None, \
        "Unable to locate {} in {}".format(
            dll,
            dll_search_path,
        )
    common_include_files.append((dll_path, dll))
required_gi_namespaces = [
    "Gtk-3.0",
    "Gdk-3.0",
    "cairo-1.0",
    "Pango-1.0",
    "GObject-2.0",
    "GLib-2.0",
    "Gio-2.0",
    "GdkPixbuf-2.0",
    "GModule-2.0",
    "Atk-1.0",
    "HarfBuzz-0.0",
]

for ns in required_gi_namespaces:
    subpath = "lib/girepository-1.0/{}.typelib".format(ns)
    fullpath = os.path.join(sys.prefix, subpath)
    assert os.path.isfile(fullpath), (
        "Required file {} is missing" .format(
            fullpath,
        ))
    common_include_files.append((fullpath, subpath))

common_packages = [
    "gi",   # always seems to be needed
    "cairo",   # Only needed (for foreign structs) if no "import cairo"s
]

exe1 = Executable(
    script = "PatentHelper.py",
    targetName = "PatentHelper.exe",
    base = "Win32GUI",
    icon="icon.ico"
)
setup(
    name = "PatentHelper",
    author = "Andrey Golubev",
    version = "1.1",
    description = "PatentHelper",
    options = {
        "build_exe": dict(
            include_files = common_include_files,
            silent = True,
            packages = common_packages,
        ),
    },
    executables = [exe1],
)
