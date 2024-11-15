from math import fabs
import tkinter
import tkinter.font

from CSSParser import CSSParser
from Globals import DEFAULT_STYLE_SHEET, SCROLL_STEP, VSTEP, WIDTH, HEIGHT
from HTMLParser import HTMLParser
from Layout import DocumentLayout
from Types import Element, Text
from URL import URL
from utils import cascade_priority, paint_tree, style, tree_to_list  
    
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.scroll = 0
        self.display_list = []
        self.nodes = []
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mscroll)
        self.window.bind("<Configure>", self.on_resize)
        self.scrollbar_width = 10
        self.max_scroll = 0

    def load(self, url):
        # if not isinstance(url, URL): return
        body = url.request()
        
        if url.is_blank:
            self.display_blank_page()
        elif url.view_source_mode:
            self.display_source_code(body)
        else:
            self.nodes = HTMLParser(body).parse()
            rules = DEFAULT_STYLE_SHEET.copy()
            links = [node.attributes["href"]
                    for node in tree_to_list(self.nodes, [])
                    if isinstance(node, Element)
                    and node.tag == "link"
                    and node.attributes.get("rel") == "stylesheet"
                    and "href" in node.attributes]
            for link in links:
                style_url = url.resolve(link)
                try:
                    body = style_url.request()
                except:
                    continue
                rules.extend(CSSParser(body).parse())
            style(self.nodes, sorted(rules, key=cascade_priority))
            # style(self.nodes, rules)
            # style(self.nodes)
            self.document = DocumentLayout(self.nodes)
            self.document.layout()
            self.display_list = []
            paint_tree(self.document, self.display_list)
            self.max_scroll = max(self.document.height + 2*VSTEP - HEIGHT, 0)
        
        self.draw()

    def display_blank_page(self):
        self.nodes = []
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        self.max_scroll = 0

    def display_source_code(self, source):
        # Create a text element to display the source code
        text_element = Element("div", {}, None)
        text_element.children.append(Text(source, text_element))
        self.document = DocumentLayout(text_element)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.max_scroll = max(self.document.height + 2*VSTEP - HEIGHT, 0)

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)
        self.draw_scrollbar()
    
    def draw_scrollbar(self):
        if self.max_scroll == 0:
            return  # Don't draw scrollbar if document fits onscreen

        # Calculate scrollbar dimensions
        scrollbar_height = (HEIGHT / (self.document.height + 2*VSTEP)) * HEIGHT
        scrollbar_y = (self.scroll / self.max_scroll) * (HEIGHT - scrollbar_height)

        # Draw scrollbar
        self.canvas.create_rectangle(
            WIDTH - self.scrollbar_width, scrollbar_y,
            WIDTH, scrollbar_y + scrollbar_height,
            fill="blue", outline="")

    def scrollup(self, e):
        self.scroll = max(self.scroll  - SCROLL_STEP, VSTEP)
        self.draw()

    def scrolldown(self, e):
        self.scroll = min(self.scroll + SCROLL_STEP, self.max_scroll)
        self.draw()

    def mscroll(self, e):
        if e.delta > 0:
            # Scroll up
            self.scrollup(e)
        elif e.delta < 0:
            # Scroll down
            self.scrolldown(e)
    
    def on_resize(self, event):
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = event.width, event.height  # Update global size
        self.document.clear()
        self.document.layout()  # Re-layout content with new size
        self.display_list.clear()
        paint_tree(self.document, self.display_list)
        self.max_scroll = max(self.document.height + 2*VSTEP - HEIGHT, 0)
        self.draw()  # Redraw the canvas

if __name__ == "__main__":
    import sys
    # body = URL(sys.argv[1]).request()
    # nodes = HTMLParser(body).parse()
    # Browser().load
    # print_tree(nodes)
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()