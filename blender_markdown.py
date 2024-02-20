import bpy
import textwrap
import re


bl_info = {
    "name": "Blender Markdown",
    "author": "Patrick W. Crawford <moo-ack@theduckcow.com>, Spectral Vectors",
    "version": (0, 0, 2),
    "blender": (2, 90, 0),
    "location": "",
    "description": "Display markdown formatted text in Blender panels",
    "warning": "",
    "doc_url": "",
    "category": "",
}


sample_md = """

# Primary title

## Secondary title

### Tertiary title

#### Click the button below to directly download MCprep
_By downloading and installing, you agree to the following [privacy policy](theduckcow.com/privacy-policy) including anonymous data tracking clause. Do not download the zip file from the readme page, you must click the button above_

### New in this (3.0.2) release:
- Added brand new feature: Meshswap block spawning!
  - You can now directly append meshswap groups into your scene from either the Shift-A menu, or the spawner panel
  - Future versions will expand blocks available significantly.
    - More indentation! Like a whooole ton, seriously! There is sooooo much indentation here.
  - Automatically can snap blocks to grid and auto prep materials (into cycles format or BI)
  - Demo link [available here](https://twitter.com/TheDuckCow/status/865971279979048961)
- Last version claimed compatibility improvement - this one actually makes it work properly for everyone. Enjoy your blending down to 2.72, for real this time!

### Numbered lists
1. This is number 1
2. This is number 2
   - With bullet 1
   - With bullet 2
3. This is number 3
   1. With sub 1
   2. With sub 2

Demo Usage
======

*[Mob spawner demo](https://www.youtube.com/watch?v=C3YoZx-seFE)*


"""


class MarkdownPanel(bpy.types.Panel):
    """Blender Markdown panel"""
    bl_label = "Markdown Panel"
    bl_idname = "OBJECT_PT_markdowndemo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def display_markdown(self, container, markdown, width=100):

        # apply scale factor for retina screens etc
        preferences = bpy.context.preferences
        pixel_size = preferences.system.pixel_size
        width /= pixel_size

        # padding to account for some kerning
        self.wrap = width / 7

        # create an isolated subview, and space it closer together
        container = container.column()
        container.scale_y = 0.7

        # convert text, ignoring special characters beyond ascii
        markdown = str(markdown).replace('*', '').replace('_', '')
        markdown = markdown.encode('utf-8').decode('ascii', 'ignore')
        label_lines = markdown.split("\n")
        lines = len(label_lines)

        for i, line in enumerate(label_lines):
            nx_line_srp = pv_line_srp = ""
            if i < lines - 2:
                nx_line_srp = label_lines[i + 1].rstrip()
            if i != 0:
                pv_line_srp = label_lines[i - 1].rstrip()

            if len(line) == 0:
                continue
            elif line.startswith('#') and not line.startswith('#' * 7):
                # headers defined from 1-6 #'s, 7+ will display as-is
                self.format_headers(line, container)
            elif nx_line_srp == len(nx_line_srp) * '=' and nx_line_srp != '':
                self.format_headers(line, container)
                continue
            elif line == len(line) * '=':
                continue  # skip this, previously already recognized as header
            elif line.lstrip().startswith('- '):
                self.format_bullets(line, container)
            else:
                sub_lines = textwrap.fill(line, self.wrap)
                split = sub_lines.split("\n")
                for string in split:
                    row = container.row()
                    row.label(text=string)
                    # row.enabled = False

        row = container.row()
        row.scale_y = 0.5
        row.label(text="")

    def format_headers(self, text, row):
        container = row
        line = text

        # get the <h#> level
        if text.startswith("######"):
            header_level = 6
            header_icon = 'SEQUENCE_COLOR_06'
            header_scale = 1
        elif text.startswith("#####"):
            header_level = 5
            header_icon = 'SEQUENCE_COLOR_05'
            header_scale = 1.2
        elif text.startswith("####"):
            header_level = 4
            header_icon = 'SEQUENCE_COLOR_04'
            header_scale = 1.4
        elif text.startswith("###"):
            header_level = 3
            header_icon = 'SEQUENCE_COLOR_03'
            header_scale = 1.6
        elif text.startswith("##"):
            header_level = 2
            header_icon = 'SEQUENCE_COLOR_02'
            header_scale = 1.8
        elif text.startswith("#"):
            header_level = 1
            header_icon = 'SEQUENCE_COLOR_01'
            header_scale = 2
        else:
            header_level = 6  # e.g. if it's based on === full header
            header_icon = 'SEQUENCE_COLOR_07'
            header_scale = 1

        split = line.split("#")
        line = ""
        for y in split:
            line += y

        sub_lines = textwrap.fill(line, self.wrap)  # ERRORS occur here sometiems..

        row = container.row()
        row.scale_y = 0.5
        row.label(text="")

        row = container.row()
        row.scale_y = 0.5
        #row.label(text="." * len(text))
        if header_level == 1:
            row.label(text="." * 1000)
        elif header_level < 4:
            row.label(text="." * 150)
        else:
            row.label(text="." * 150)

        sub_lines = sub_lines.split("\n")
        row = container.row()
        row.label(text=sub_lines[0], icon=header_icon)
        row.scale_y = header_scale
        #row.alignment = 'CENTER'
        row.label(text='', icon=header_icon)
        if len(sub_lines) > 1:
            for string in sub_lines[1:]:
                row = container.row()
                row.label(text=string, icon="RIGHTARROW")

        row = container.row()
        row.scale_y = 0.2
        # row.label(text="." * len(text))
        if header_level == 1:
            row.label(text="." * 1000)
        elif header_level < 4:
            row.label(text="." * 150)

        row = container.row()
        row.scale_y = 0.5
        row.label(text="")

    # def display_links(self, text, row):

    #     reg = "!\[[^\]]+\]\([^)]+\)"
    
    # \[(.+?)\]\(\s*(https?:\/\/[^)]+)\s*\)/g

    def format_bullets(self, text, row):
        # some kind of bullet
        line = text
        container = row
        row = container.row()

        # determine indentation level
        indent = len(line) - len(line.lstrip())
        indent = int(indent / 2) - indent % 2  # a creative way to do "floor"

        # now draw leading indents (ie sums of 2 spaces in a row)
        row = container.row()
        for i in range(indent):
            row.label(text="", icon="BLANK1")

        # draw first bullet
        sub_lines = textwrap.fill(
            line.lstrip()[2:],
            int(self.wrap - 2 * indent - 2)
        )
        split = sub_lines.split("\n")
        row.label(text=split[0], icon="DOT")
        # row.enabled = False
        if len(split) != 1:
            for s in split[1:]:
                row = container.row()
                for i in range(indent):
                    row.label(text="", icon="BLANK1")
                row.label(text=s, icon="BLANK1")
                # row.enabled = False

    def draw(self, context):
        for region in context.area.regions:
            width = region.width
            
        layout = self.layout
        col = layout.column()
        box = col.box()
        margin = 50  # this accounts for scrollbar of panel+ margins left/right of a box
        self.display_markdown(
            container=box, 
            markdown=sample_md, 
            width=width - margin
        )


def register():
    bpy.utils.register_class(MarkdownPanel)


def unregister():
    bpy.utils.unregister_class(MarkdownPanel)


if __name__ == "__main__":
    register()
