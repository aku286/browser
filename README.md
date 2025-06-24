# Simple Python Browser Engine

A minimal browser engine written in Python. This project parses HTML and CSS, builds a DOM tree, applies styles, computes layout, and renders content using Tkinter.

## Features

- **HTML Parsing:** Converts HTML text into a DOM tree.
- **CSS Parsing:** Parses CSS rules and selectors.
- **Style Application:** Applies CSS rules and inline styles to DOM nodes.
- **Layout Engine:** Computes block and inline layout for elements.
- **Rendering:** Draws text and rectangles using Tkinter.
- **Basic CSS Support:** Tag selectors, descendant selectors, and basic properties (color, font-size, font-style, font-weight, background-color).
- **Navigation:** Handles URLs, including `http`, `https`, `file`, and `data`.

## File Structure

- `browser.py` — Main browser logic and URL handling.
- `HTMLParser.py` — HTML parsing to DOM.
- `CSSParser.py` — CSS parsing and selector logic.
- `Selectors.py` — Selector classes for CSS.
- `Types.py` — DOM node types.
- `Globals.py` — Global constants and default styles.
- `Layout.py` — Layout computation for block and inline elements.
- `Draw.py` — Drawing primitives for rendering.
- `utils.py` — Utility functions for styling and tree traversal.
- `browser.css` — Default stylesheet.
- `URL.py` — URL parsing and HTTP/file/data handling.

## Getting Started

### Prerequisites

- Python 3.7+
- Tkinter (usually included with Python)

### Running

1. Ensure all files are in the same directory.
2. Run the main script:

   ```sh
   python browser.py
   ```

## Example CSS

```css
a { color: blue; }
i { font-style: italic; }
b { font-weight: bold; }
small { font-size: 90%; }
big { font-size: 110%; }
```

## License

This project is for educational purposes.