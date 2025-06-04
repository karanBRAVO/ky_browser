# Ky_Browser

`Tech Stack`: **Python**, **Tkinter**, **Sockets**

Want to create a simple browser using Python and Tkinter? This project is a great starting point. It demonstrates how to use the tkinter library to create a basic web browser interface.

Read the [wiki](https://github.com/karanBRAVO/ky_browser/wiki) for more information on how to use this project.

## Features

Everything built in this project is done from scratch.

- `URL` parser - defined in `url.py`
  - `Source View` - load the source code of the webpage
  - `File View` - load local files
  - `data view` - load data from the URL
- `HTML` parser - defined in `html_parser.py`
- `CSS` parser - defined in `css_parser.py`
- `Layout Tree` generator and `Renderer` - defined in `layout.py`
- `Window` and `Event Loop` - defined in `window.py` (renders all the contents downloaded by the url parser)
  - `Syntax Highlighting`
  - `Webpage Rendering`
