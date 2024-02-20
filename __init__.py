import bpy
from .MarkdownPanel import MarkdownPanel

bl_info = {
    "name": "Blender Markdown",
    "author": "Patrick W. Crawford <moo-ack@theduckcow.com>, Spectral Vectors",
    "version": (0, 0, 2),
    "blender": (2, 90, 0),
    "location": "",
    "description": "Display markdown formatted text in Blender panels",
    "warning": "",
    "doc_url": "",
    "category": "Interface",
}


def register():
    bpy.utils.register_class(MarkdownPanel)


def unregister():
    bpy.utils.unregister_class(MarkdownPanel)


if __name__ == "__main__":
    register()
