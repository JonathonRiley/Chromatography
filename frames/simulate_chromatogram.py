import tkinter as tk

from resources.settings import LARGE_FONT


class SimulateChromatogram(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Simulate Chromatogram", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        from frames.home_page import HomePage
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: parent.show_frame(HomePage))
        button1.pack()
