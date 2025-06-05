from tkinter import Canvas, font


class Scrollbar:
    """
    A class representing a scrollbar.
    """

    SCROLL_STEP = 100
    HSTEP, VSTEP = 13, 18
    MIN_V_SCROLL, MIN_H_SCROLL = 0, 0
    SCROLLBAR_WIDTH = 15
    SCROLLBAR_COLOR = "#444444"
    SCROLLBAR_THUMB_COLOR = "#888888"
    SCROLLBAR_THUMB_HOVER_COLOR = "#AAAAAA"

    def __init__(self, screen_width: int, screen_height: int, draw_callback=None):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.v_scroll = 0
        self.h_scroll = 0
        self.MAX_V_SCROLL = 0
        self.MAX_H_SCROLL = 0
        self.dragging_v_scrollbar = False
        self.dragging_h_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_x = 0
        self.drag_start_scroll = 0

        self.draw_callback = draw_callback

    def update_screen_dimensions(self, screen_width: int, screen_height: int):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height

    def scroll_left(
        self,
    ):
        if self.h_scroll - self.SCROLL_STEP < self.MIN_H_SCROLL:
            self.h_scroll = self.MIN_H_SCROLL
        else:
            self.h_scroll -= self.SCROLL_STEP
        if self.draw_callback:
            self.draw_callback()

    def scroll_right(
        self,
    ):
        if self.h_scroll + self.SCROLL_STEP > self.MAX_H_SCROLL:
            self.h_scroll = self.MAX_H_SCROLL
        else:
            self.h_scroll += self.SCROLL_STEP
        if self.draw_callback:
            self.draw_callback()

    def scroll_down(
        self,
    ):
        if self.v_scroll + self.SCROLL_STEP > self.MAX_V_SCROLL:
            self.v_scroll = self.MAX_V_SCROLL
        else:
            self.v_scroll += self.SCROLL_STEP
        if self.draw_callback:
            self.draw_callback()

    def scroll_up(
        self,
    ):
        if self.v_scroll - self.SCROLL_STEP < self.MIN_V_SCROLL:
            self.v_scroll = self.MIN_V_SCROLL
        else:
            self.v_scroll -= self.SCROLL_STEP
        if self.draw_callback:
            self.draw_callback()

    def get_v_scrollbar_bounds(self):
        if self.MAX_V_SCROLL <= 0:
            return None

        # Scrollbar track area
        track_x = self.SCREEN_WIDTH - self.SCROLLBAR_WIDTH
        track_y = 0
        track_width = self.SCROLLBAR_WIDTH
        track_height = self.SCREEN_HEIGHT - (
            self.SCROLLBAR_WIDTH if self.MAX_H_SCROLL > 0 else 0
        )

        # Scrollbar thumb (the draggable part)
        content_height = self.MAX_V_SCROLL + self.SCREEN_HEIGHT
        thumb_height = max(
            20, int((self.SCREEN_HEIGHT / content_height) * track_height)
        )
        thumb_y = (
            int((self.v_scroll / self.MAX_V_SCROLL) * (track_height - thumb_height))
            if self.MAX_V_SCROLL > 0
            else 0
        )

        return {
            "track": (track_x, track_y, track_width, track_height),
            "thumb": (track_x, thumb_y, track_width, thumb_height),
        }

    def get_h_scrollbar_bounds(self):
        if self.MAX_H_SCROLL <= 0:
            return None

        # Scrollbar track area
        track_x = 0
        track_y = self.SCREEN_HEIGHT - self.SCROLLBAR_WIDTH
        track_width = self.SCREEN_WIDTH - (
            self.SCROLLBAR_WIDTH if self.MAX_V_SCROLL > 0 else 0
        )
        track_height = self.SCROLLBAR_WIDTH

        # Scrollbar thumb (the draggable part)
        content_width = self.MAX_H_SCROLL + self.SCREEN_WIDTH
        thumb_width = max(20, int((self.SCREEN_WIDTH / content_width) * track_width))
        thumb_x = (
            int((self.h_scroll / self.MAX_H_SCROLL) * (track_width - thumb_width))
            if self.MAX_H_SCROLL > 0
            else 0
        )

        return {
            "track": (track_x, track_y, track_width, track_height),
            "thumb": (thumb_x, track_y, thumb_width, track_height),
        }

    def is_point_in_rect(self, x, y, rect_x, rect_y, rect_width, rect_height):
        return (
            rect_x <= x <= rect_x + rect_width and rect_y <= y <= rect_y + rect_height
        )

    def scrollbar_click(
        self,
        x: int,
        y: int,
    ):
        # Check vertical scrollbar
        v_bounds = self.get_v_scrollbar_bounds()
        if v_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = v_bounds["thumb"]
            if self.is_point_in_rect(x, y, thumb_x, thumb_y, thumb_width, thumb_height):
                self.dragging_v_scrollbar = True
                self.drag_start_y = y
                self.drag_start_scroll = self.v_scroll
                return

            # Click on track (but not thumb) - jump to position
            track_x, track_y, track_width, track_height = v_bounds["track"]
            if self.is_point_in_rect(x, y, track_x, track_y, track_width, track_height):
                # Calculate new scroll position based on click position
                relative_y = y - track_y
                scroll_ratio = relative_y / track_height
                new_scroll = int(scroll_ratio * self.MAX_V_SCROLL)
                self.v_scroll = max(
                    self.MIN_V_SCROLL, min(self.MAX_V_SCROLL, new_scroll)
                )
                if self.draw_callback:
                    self.draw_callback()
                return

        # Check horizontal scrollbar
        h_bounds = self.get_h_scrollbar_bounds()
        if h_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = h_bounds["thumb"]
            if self.is_point_in_rect(x, y, thumb_x, thumb_y, thumb_width, thumb_height):
                self.dragging_h_scrollbar = True
                self.drag_start_x = x
                self.drag_start_scroll = self.h_scroll
                return

            # Click on track (but not thumb) - jump to position
            track_x, track_y, track_width, track_height = h_bounds["track"]
            if self.is_point_in_rect(x, y, track_x, track_y, track_width, track_height):
                # Calculate new scroll position based on click position
                relative_x = x - track_x
                scroll_ratio = relative_x / track_width
                new_scroll = int(scroll_ratio * self.MAX_H_SCROLL)
                self.h_scroll = max(
                    self.MIN_H_SCROLL, min(self.MAX_H_SCROLL, new_scroll)
                )
                if self.draw_callback:
                    self.draw_callback()
                return

    def scrollbar_drag(
        self,
        x: int,
        y: int,
    ):
        if self.dragging_v_scrollbar:
            v_bounds = self.get_v_scrollbar_bounds()
            if v_bounds:
                track_x, track_y, track_width, track_height = v_bounds["track"]
                thumb_height = v_bounds["thumb"][3]

                # Calculate how much the mouse moved
                delta_y = y - self.drag_start_y

                # Convert mouse movement to scroll movement
                usable_track_height = track_height - thumb_height
                if usable_track_height > 0:
                    scroll_delta = (delta_y / usable_track_height) * self.MAX_V_SCROLL
                    new_scroll = self.drag_start_scroll + scroll_delta
                    self.v_scroll = max(
                        self.MIN_V_SCROLL, min(self.MAX_V_SCROLL, int(new_scroll))
                    )
                    if self.draw_callback:
                        self.draw_callback()

        elif self.dragging_h_scrollbar:
            h_bounds = self.get_h_scrollbar_bounds()
            if h_bounds:
                track_x, track_y, track_width, track_height = h_bounds["track"]
                thumb_width = h_bounds["thumb"][2]

                # Calculate how much the mouse moved
                delta_x = x - self.drag_start_x

                # Convert mouse movement to scroll movement
                usable_track_width = track_width - thumb_width
                if usable_track_width > 0:
                    scroll_delta = (delta_x / usable_track_width) * self.MAX_H_SCROLL
                    new_scroll = self.drag_start_scroll + scroll_delta
                    self.h_scroll = max(
                        self.MIN_H_SCROLL, min(self.MAX_H_SCROLL, int(new_scroll))
                    )
                    if self.draw_callback:
                        self.draw_callback()

    def scrollbar_release(self):
        self.dragging_v_scrollbar = False
        self.dragging_h_scrollbar = False

    def scrollbar_hover(self, x: int, y: int, canvas: Canvas):
        cursor = "arrow"

        # Check if hovering over scrollbars
        v_bounds = self.get_v_scrollbar_bounds()
        if v_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = v_bounds["thumb"]
            track_x, track_y, track_width, track_height = v_bounds["track"]
            if self.is_point_in_rect(
                x, y, thumb_x, thumb_y, thumb_width, thumb_height
            ) or self.is_point_in_rect(
                x, y, track_x, track_y, track_width, track_height
            ):
                cursor = "hand2"

        h_bounds = self.get_h_scrollbar_bounds()
        if h_bounds:
            thumb_x, thumb_y, thumb_width, thumb_height = h_bounds["thumb"]
            track_x, track_y, track_width, track_height = h_bounds["track"]
            if self.is_point_in_rect(
                x, y, thumb_x, thumb_y, thumb_width, thumb_height
            ) or self.is_point_in_rect(
                x, y, track_x, track_y, track_width, track_height
            ):
                cursor = "hand2"

        canvas.config(cursor=cursor)

    def calc_max_scroll(self, display_list: list, font: font.Font):
        effective_height = self.SCREEN_HEIGHT - (
            self.SCROLLBAR_WIDTH if self.MAX_H_SCROLL > 0 else 0
        )
        effective_width = self.SCREEN_WIDTH - (
            self.SCROLLBAR_WIDTH if self.MAX_V_SCROLL > 0 else 0
        )

        self.MAX_V_SCROLL = max(
            0,
            (
                display_list[-1].y - effective_height + font.metrics()["linespace"]
                if display_list
                else 0
            ),
        )
        self.MAX_H_SCROLL = max(
            0,
            (
                max([item.x for item in display_list]) - effective_width
                if display_list
                else 0
            ),
        )

    def draw_scrollbars(self, canvas: Canvas):
        # Draw vertical scrollbar
        v_bounds = self.get_v_scrollbar_bounds()
        if v_bounds:
            track_x, track_y, track_width, track_height = v_bounds["track"]
            thumb_x, thumb_y, thumb_width, thumb_height = v_bounds["thumb"]

            # Draw track
            canvas.create_rectangle(
                track_x,
                track_y,
                track_x + track_width,
                track_y + track_height,
                fill=self.SCROLLBAR_COLOR,
                outline=self.SCROLLBAR_COLOR,
            )

            # Draw thumb
            canvas.create_rectangle(
                thumb_x,
                thumb_y,
                thumb_x + thumb_width,
                thumb_y + thumb_height,
                fill=self.SCROLLBAR_THUMB_COLOR,
                outline=self.SCROLLBAR_THUMB_COLOR,
            )

        # Draw horizontal scrollbar
        h_bounds = self.get_h_scrollbar_bounds()
        if h_bounds:
            track_x, track_y, track_width, track_height = h_bounds["track"]
            thumb_x, thumb_y, thumb_width, thumb_height = h_bounds["thumb"]

            # Draw track
            canvas.create_rectangle(
                track_x,
                track_y,
                track_x + track_width,
                track_y + track_height,
                fill=self.SCROLLBAR_COLOR,
                outline=self.SCROLLBAR_COLOR,
            )

            # Draw thumb
            canvas.create_rectangle(
                thumb_x,
                thumb_y,
                thumb_x + thumb_width,
                thumb_y + thumb_height,
                fill=self.SCROLLBAR_THUMB_COLOR,
                outline=self.SCROLLBAR_THUMB_COLOR,
            )

        # Draw corner piece if both scrollbars are present
        if v_bounds and h_bounds:
            corner_x = self.SCREEN_WIDTH - self.SCROLLBAR_WIDTH
            corner_y = self.SCREEN_HEIGHT - self.SCROLLBAR_WIDTH
            canvas.create_rectangle(
                corner_x,
                corner_y,
                corner_x + self.SCROLLBAR_WIDTH,
                corner_y + self.SCROLLBAR_WIDTH,
                fill=self.SCROLLBAR_COLOR,
                outline=self.SCROLLBAR_COLOR,
            )
