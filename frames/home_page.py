import tkinter as tk

from frames.fit_chromatogram import FitChromatogram
from frames.simulate_chromatogram import SimulateChromatogram
from frames.find_limits import FindLimits
from resources.settings import BKG, LARGE_FONT, MEDIUM_FONT, SMALL_FONT


class HomePage(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bg=BKG)
        label = tk.Label(self, text="Chromatography Toolkit", font=MEDIUM_FONT, bg=BKG, width=20, height=5)
        label.pack()

        button = tk.Button(self, text="Fit Chromatogram",
                           command=lambda: parent.show_frame(FitChromatogram))
        button.config(highlightbackground=BKG)
        button.pack(pady=2, padx=10)

        button2 = tk.Button(self, text="Simulate Chromatogram",
                            command=lambda: parent.show_frame(SimulateChromatogram))
        button2.config(highlightbackground=BKG)
        button2.pack(pady=2, padx=10)

        button3 = tk.Button(self, text="Find Tailing Limits",
                            command=lambda: parent.show_frame(FindLimits))
        button3.config(highlightbackground=BKG)
        button3.pack(pady=2, padx=10)
        self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)