import bpy
import textwrap
import re
import os


class MarkdownPanel(bpy.types.Panel):
    """Blender Markdown panel"""
    bl_label = "Markdown Panel"
    bl_idname = "OBJECT_PT_markdowndemo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def display_markdown(self, container, md_path, width=100):

        with open(md_path) as file:
            markdown = file.read()

        # apply scale factor for retina screens etc
        preferences = bpy.context.preferences
        pixel_size = preferences.system.pixel_size
        width /= pixel_size

        # padding to account for some kerning
        self.wrap = width / 7

        # create an isolated subview, and space it closer together
        container = container.column()
        container.scale_y = 0.7

        # Format Links before splitting text into lines
        links = 0
        urls = []
        names = []
        link_name = "[^\[]+"
        link_url = "http[s]?://.+"
        markup_regex = f'\[({link_name})]\(\s*({link_url})\s*\)'

        for match in re.findall(markup_regex, markdown):
            name = match[0]
            names.append(name)
            url = match[1]
            urls.append(url)
            print(f'{name}: {url}')

            markdown = re.sub(repl=f'\nLINKname{links}\n', pattern=name, string=markdown)
            markdown = re.sub(repl='', pattern=url, string=markdown) 
            
            links += 1    

        markdown = str(markdown).replace('*', '').replace('_', '').replace('()', '').replace('[', '').replace(']', '')
        markdown = markdown.encode('utf-8').decode('ascii', 'ignore')
        label_lines = markdown.split("\n")
        lines = len(label_lines)

        for i, line in enumerate(label_lines):
            next_line = previous_line = ""
            if i < lines - 2:
                next_line = label_lines[i + 1].rstrip()
            if i != 0:
                previous_line = label_lines[i - 1].rstrip()

            if len(line) == 0:
                continue
            elif line.startswith('#') and not line.startswith('#' * 7):
                # headers defined from 1-6 #'s, 7+ will display as-is
                self.format_headers(line, container)
            elif next_line == len(next_line) * '=' and next_line != '':
                self.format_headers(line, container)
                continue
            elif line == len(line) * '=':
                continue  # skip this, previously already recognized as header
            elif line.lstrip().startswith('- '):
                self.format_bullets(line, container)
            elif line.startswith('LINKname'):
                line = line.replace('LINKname', '')
                i = int(line)

                row = container.split()#(factor=0.3)
#                row = container.row()
#                row.label(text=''*10)
                row.operator('wm.url_open', text=names[i], icon='URL').url=urls[i]
#                row.label(text=''*10)
                row.scale_y = 2
            else:
                sub_lines = textwrap.fill(line, self.wrap)
                split = sub_lines.split("\n")
                for string in split:
                    if string.replace('(', '').replace(')','') in urls:
                        continue
                    else:
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
            for string in split[1:]:
                row = container.row()
                for i in range(indent):
                    row.label(text="", icon="BLANK1")
                row.label(text=string, icon="BLANK1")
                # row.enabled = False

    def draw(self, context):
        for region in context.area.regions:
            region_width = region.width
        margin = 50  # this accounts for scrollbar of panel+ margins left/right of a box
        width = region_width - margin

        md_path = os.path.dirname(os.path.abspath(__file__))
        md_path = f'{md_path}\\sample.md'

        layout = self.layout
        col = layout.column()
        box = col.box()

        self.display_markdown(
            container=box, 
            md_path=md_path,
            width=width
        )
