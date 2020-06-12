import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")

from resources.settings import BKG, LARGE_FONT, MEDIUM_FONT, SMALL_FONT
from frames.home_page import HomePage


def draw_graph(f, ax, data=None):
    return f


class ChromatographyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        #tk.Tk.iconbitmap(self,default='clienticon.ico')
        tk.Tk.wm_title(self, "Chromatography Toolkit")

        self.frame = None
        self.show_frame(HomePage)

    def show_frame(self, frame_class):
        new_frame = frame_class(self)
        if self.frame is not None:
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.frame.destroy()
        self.frame = new_frame
        self.frame.pack()



app = ChromatographyApp()
app.mainloop()
