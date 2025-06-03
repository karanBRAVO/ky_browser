from tkinter import Canvas, font


class DrawText:
    """
    Class to draw text on a canvas.
    """

    def __init__(self, x: int, y: int, text: str, font: font.Font, color="white"):
        self.x = x
        self.y = y
        self.text = text
        self.font = font
        self.color = color

    def execute(self, canvas: Canvas, scroll_x: int = 0, scroll_y: int = 0):
        canvas.create_text(
            self.x - scroll_x,
            self.y - scroll_y,
            text=self.text,
            font=self.font,
            anchor="nw",
            fill=self.color,
        )


class DrawRect:
    """
    Class to draw a rectangle on a canvas.
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        border="yellow",
        backgound="black",
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.border = border
        self.backgound = backgound

    def execute(self, canvas: Canvas, scroll_x: int = 0, scroll_y: int = 0):
        canvas.create_rectangle(
            self.x - scroll_x,
            self.y - scroll_y,
            self.x + self.width - scroll_x,
            self.y + self.height - scroll_y,
            outline=self.border,
            fill=self.backgound,
        )
