from tkinter import font as tk_font


class Font:
    """
    A class to represent a font with various attributes such as family, size, weight, and slant.
    """

    def __init__(
        self, family="Times New Roman", size=14, weight="normal", slant="roman"
    ):
        self.family = family
        self.size = size
        self.weight = weight
        self.slant = slant
        # print(tk_font.families())

    def get_font(self, new_style: dict = {}):
        return tk_font.Font(
            family=new_style["family"] if "family" in new_style else self.family,
            size=new_style["size"] if "size" in new_style else self.size,
            weight=new_style["weight"] if "weight" in new_style else self.weight,
            slant=new_style["slant"] if "slant" in new_style else self.slant,
            underline=new_style.get("underline", False),
        )
