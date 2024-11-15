import tkinter
from Draw import DrawRect, DrawText
from Globals import BLOCK_ELEMENTS, FONTS, HSTEP, VSTEP, WIDTH
from Types import Element, Text

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = WIDTH - 2*HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height

    def paint(self):
        return []
    
    def clear(self):
        self.children.clear()

class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.cursor_x = 0
        self.cursor_y = 0
        self.weight = "normal"
        self.style = "roman"
        self.size = 12
        self.display_list = []
        self.line = []
        self.is_centered = False
        self.is_superscript = False

    def layout(self):
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y
        self.x = self.parent.x
        self.width = self.parent.width

        self.is_centered = (isinstance(self.node, Element) and
                            self.node.tag == "h1" and
                            self.node.attributes.get("class") == "title")
        
        mode = self.layout_mode()
        if mode == "block":
            self.layout_intermediate()
        else:
            self.adjust_layout_for_tag()
            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def word(self, node, word):
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        color = node.style["color"]
        if style == "normal": style = "roman"
        size = int(float(node.style["font-size"][:-2]) * .75)
        font = self.get_font(size, weight, style)
        # font = self.get_font(self.size, self.weight, self.style)
        w = font.measure(word)
        if self.cursor_x + w > self.width:
            self.flush()
        self.line.append((self.cursor_x, word, font, self.is_superscript, color))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font, is_sup, color in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        if self.is_centered:
            line_width = sum([font.measure(word) for _, word, font, _,_  in self.line]) + \
                         sum([font.measure(" ") for _, _, font, _, _ in self.line[:-1]])
            offset = (self.width - line_width) / 2
        else:
            offset = 0

        for rel_x, word, font, is_sup, color in self.line:
            x = self.x + rel_x + offset
            if is_sup:
                y = self.y + baseline - 1.5 * font.metrics("ascent")
            else:
                y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font, color))
        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent        
        self.cursor_x = 0
        self.line = []

    def get_font(self, size, weight, style):
        key = (size, weight, style)
        if key not in FONTS:
            font = tkinter.font.Font(size=size, weight=weight,
                slant=style)
            label = tkinter.Label(font=font)
            FONTS[key] = (font, label)
        return FONTS[key][0]

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "sup":
            self.is_superscript = True
            self.size = max(6, self.size // 2)  # Reduce size, but not smaller than 6

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "br":
            self.flush()
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "sup":
            self.is_superscript = False
            self.size *= 2  # Restore original size
    
    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            self.open_tag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node.tag)

    def layout_intermediate(self):
        previous = None
        children = self.node if isinstance(self.node, list) else self.node.children
        for child in children:
            if isinstance(child, Element) and child.tag == "head":
                continue
            if isinstance(child, Element) and child.tag == "nav" and child.attributes.get("id") == "toc":
                # Create a new Element for the "Table of Contents" header
                toc_header = Element("div", {"class": "toc-header"}, self.node)
                toc_header.children.append(Text("Table of Contents", toc_header))
                
                # Add the header as a new BlockLayout
                header_layout = BlockLayout(toc_header, self, previous)
                self.children.append(header_layout)
                previous = header_layout

            next_layout = BlockLayout(child, self, previous)
            self.children.append(next_layout)
            previous = next_layout

    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif isinstance(self.node, Element):
            if any(isinstance(child, Element) and child.tag in BLOCK_ELEMENTS
                   for child in self.node.children):
                return "block"
            elif self.node.children:
                return "inline"
            else:
                return "block"
        else:
            return "block"

    def adjust_layout_for_tag(self):
        if isinstance(self.node, Text): return
        # Default indentation for normal inline elements
        indentation_x = 0
        indentation_y = 0

        # Define custom indentations for specific tags
        if self.node.tag == "li":
            indentation_x = 8  # Indentation for list items
        elif self.node.tag == "blockquote":
            indentation_x = 40  # Indentation for blockquotes or quotes
        
        # Adjust cursor_x based on the computed indentation
        self.cursor_x += indentation_x
        self.cursor_y += indentation_y


    def paint(self):
        cmds = []
        bgcolor = self.node.style.get("background-color",
                                      "transparent")
        print("bgColor ", bgcolor)
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, bgcolor)
            cmds.append(rect)

        if isinstance(self.node, Element):
            print(self.node)
            if self.node.tag == "nav": 
                if self.node.attributes.get("class") == "links":
                    x2, y2 = self.x + self.width, self.y + self.height
                    rect = DrawRect(self.x, self.y, x2, y2, "yellow")
                    cmds.append(rect)
            elif self.node.tag == "div" and self.node.attributes.get("class") == "toc-header":
                # Add gray background for the "Table of Contents" header
                x2, y2 = self.x + self.width, self.y + self.height
                rect = DrawRect(self.x, self.y, x2, y2, "lightgray")
                cmds.append(rect)    
            # elif self.node.tag == "pre":
            #     x2, y2 = self.x + self.width, self.y + self.height
            #     rect = DrawRect(self.x, self.y, x2, y2, "gray")
            #     cmds.append(rect)
            elif self.node.tag == "li":
                # Draw a bullet as a small rectangle or circle
                bullet_x = self.x
                bullet_y = self.y + self.height / 2
                bullet_width = 4  # width of the bullet
                bullet_height = 4  # height of the bullet
                
                # Draw the bullet (you could also create a circle instead of a rectangle)
                rect = DrawRect(bullet_x, bullet_y - bullet_height/2, bullet_x + bullet_width, bullet_y + bullet_height/2, "black")
                cmds.append(rect)

        if self.layout_mode() == "inline":
            for x, y, word, font, is_sup, color  in self.display_list:
                cmds.append(DrawText(x, y, word, font, color))
        return cmds