# Ky_Browser

`Tech Stack`: **Python**, **Tkinter**, **Sockets**

Want to create a simple browser using Python and Tkinter? This project is a great starting point. It demonstrates how to use the tkinter library to create a basic web browser interface.

Read the [wiki](https://github.com/karanBRAVO/ky_browser/wiki) for more information on how to use this project.

## Features

Everything built in this project is done from scratch.

- `URL Parser` - Parses URLs and handles different protocols (http, https, file, view-source, data etc.)
- `HTML Parser` - Parses HTML documents and builds a Document Object Model (DOM) tree.
- `CSS Parser` - Parses CSS stylesheets and applies styles to the DOM.
- `Layout Tree` - Generates a layout tree from the DOM and applies styles.
- `Renderer` - Renders the layout tree to the screen.
- `History` - Keeps track of visited URLs and allows navigation through history.
- `Bookmarks` - Allows users to bookmark URLs for quick access.
- `Shortcuts` - Provides keyboard shortcuts for common actions like back, forward, reload.

## Getting Started

To run this project, you need to have Python installed on your machine. You can download Python from the [official website](https://www.python.org/downloads/).

You also have to install the `tkinter` library, which is usually included with Python installations. If it's not installed, you can install it using pip:

```bash
pip install tk
```

After installing Python, you can clone this repository and run the `window.py` file to start the browser.

```bash
git clone https://github.com/karanBRAVO/ky_browser

cd ky_browser

python window.py
```
