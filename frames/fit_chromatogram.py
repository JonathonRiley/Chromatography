import csv
import tkinter as tk
from tkinter import filedialog, StringVar

from scipy import optimize
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from resources.settings import BKG, LARGE_FONT, MEDIUM_FONT, SMALL_FONT
from resources.helper_functions import graph_zoom, expo_gauss_curve, multi_expo_gauss_curve, find_asym
from resources.fitter_helper_functions import process_guess_and_bounds, extract_background


class FitChromatogram(tk.Frame):

    def __init__(self, parent):
        self.peaks = []
        self.background = None
        self.data = [[x/100, None] for x in range(60*100)]
        self.canvas = None
        self.ymax=100
        self.ymin=-5
        self.peak_frames = []
        self.zoom = 0
        self.f = Figure(figsize=(6,4), dpi=100)
        self.ax = self.f.add_subplot(111)
        self.ax.plot([],[])
        self.ax.set_xlim([0,40])
        self.ax.set_ylim([0,100])
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Response")

        tk.Frame.__init__(self, parent)
        chart_frame = tk.Frame(self, width=900, height=600, relief=tk.SUNKEN, borderwidth=2)

        canvas = FigureCanvasTkAgg(self.f, chart_frame)
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas = canvas

        chart_btn_frame = tk.Frame(chart_frame, width=400)
        load_btn = tk.Button(chart_btn_frame, text="Load Data", command=lambda: self.load_data())
        load_btn.pack(side=tk.LEFT)
        zoom_out_btn = tk.Button(chart_btn_frame, text="Zoom Out", command=lambda: graph_zoom(self, -1))
        zoom_out_btn.pack(side=tk.LEFT)
        zoom_in_btn = tk.Button(chart_btn_frame, text="Zoom In", command=lambda: graph_zoom(self, 1))
        zoom_in_btn.pack(side=tk.LEFT)
        chart_btn_frame.pack(side=tk.TOP)
        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        #add sidebar frame to contain peak parameters
        tools_frame = tk.Frame(self, width=450, bg=BKG)
        title = tk.Label(tools_frame, text="Fit Chromatogram", font=MEDIUM_FONT, bg=BKG)
        title.pack(pady=10,padx=10)

        top_btn_frame = tk.Frame(tools_frame, bg=BKG)
        load_params_btn = tk.Button(top_btn_frame, width=15, text="Load Parameters",
                                    command=lambda: self.load_params(tools_frame))
        load_params_btn.grid(row=0, column=0)
        load_params_btn.config(highlightbackground=BKG)

        fit_btn = tk.Button(top_btn_frame, width=15, text="Run fit",
                            command=lambda: self.run_fit())
        fit_btn.grid(row=0, column=1)
        fit_btn.config(highlightbackground=BKG)

        add_btn = tk.Button(top_btn_frame, width=15, text="Add peak",
                            command=lambda: self.add_peak(tools_frame))
        add_btn.grid(row=1, column=0)
        add_btn.config(highlightbackground=BKG)

        remove_btn = tk.Button(top_btn_frame, width=15, text="Remove peak",
                               command=lambda: self.remove_peak())
        remove_btn.grid(row=1, column=1)
        remove_btn.config(highlightbackground=BKG)
        top_btn_frame.pack(side=tk.TOP)

        headers = ["Name","Position","Width","Response","Lambda", "Asym(5%)"]

        headers_frame = tk.Frame(tools_frame, bg=BKG)
        bkg_label = tk.Label(headers_frame, text='Background', font=SMALL_FONT, bg=BKG, width=10)
        bkg_label.grid(row=0,column=2)
        sv = StringVar()
        sv.set(0)
        background = tk.Entry(headers_frame, textvariable=sv, width=5)
        self.background = background
        background.bind('<FocusOut>', (lambda _: self.update_graph()))
        background.config(highlightbackground=BKG)
        background.grid(row=0,column=3)
        for col in range(len(headers)):
            label = tk.Label(headers_frame, text=headers[col], font=SMALL_FONT, bg=BKG, width=8)
            label.grid(row=1,column=col)
        headers_frame.pack(side=tk.TOP, padx=5)

        #self.add_peak(tools_frame)
        from frames.home_page import HomePage
        home = tk.Button(tools_frame, text="Back to Home", command=lambda: parent.show_frame(HomePage))
        home.config(highlightbackground=BKG)
        home.pack(side=tk.BOTTOM)
        tools_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)


        tools_btn_frame = tk.Frame(tools_frame)

        save_params_btn = tk.Button(tools_btn_frame, text="Save Parameters",
                                    command=lambda: self.save_params())
        save_params_btn.config(highlightbackground=BKG)
        save_params_btn.pack(side=tk.LEFT)


        save_curves_btn = tk.Button(tools_btn_frame, text="Save Fit Curves",
                                    command=lambda: self.save_curve_fit())
        save_curves_btn.config(highlightbackground=BKG)
        save_curves_btn.pack(side=tk.LEFT)
        tools_btn_frame.pack(side=tk.BOTTOM)

        self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    def load_data(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            _ = next(csv_reader)
            self.data = [[float(x), float(y)] for x, y in csv_reader]

        yvals = [y for _, y in self.data]
        ymin = min(yvals)
        ymax = max(yvals)
        self.ymin = ymin - 0.05*(ymax-ymin)
        self.ymax = ymax + 0.1*(ymax-ymin)
        self.update_graph()

    def load_params(self,tools_frame):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            _ = next(csv_reader)
            params = [row for row in csv_reader]
        for name, position, width, response, lamb in params:
            xvals = [x for x, _ in self.data]
            temp_peak = expo_gauss_curve(xvals, float(position), float(width), float(response), float(lamb))
            tailing = find_asym(xvals, temp_peak)
            self.add_peak(tools_frame, [name, position, width, response, lamb, tailing])
        self.update_tailings()
        self.update_graph()


    def add_peak(self, frame, params=None):
        temp_frame = tk.Frame(frame, bg=BKG)
        mock_peaks = ['',0,0,0,10,1] if params is None else params
        entries = []
        for val in mock_peaks[:-2]:
            sv = StringVar()
            sv.set(val)
            entry = tk.Entry(temp_frame, textvariable=sv, width=5)
            entry.bind('<FocusOut>', (lambda _: self.update_graph()))
            entry.config(highlightbackground=BKG)
            entries.append(entry)
            entry.pack(side=tk.LEFT, padx=11)

        sv = StringVar()
        sv.set(mock_peaks[-2])
        entry = tk.Entry(temp_frame, textvariable=sv, width=5)
        entry.bind('<FocusOut>', (lambda _: self.update_tailings()))
        entry.config(highlightbackground=BKG)
        entries.append(entry)
        entry.pack(side=tk.LEFT, padx=11)

        sv = StringVar()
        sv.set(mock_peaks[-1])
        label = tk.Label(temp_frame, textvariable=sv, width=5, height=1, bg='#c2f7ff',
                         borderwidth=2, relief='ridge')
        entries.append(sv)
        label.pack(side=tk.LEFT, padx=11)
        self.peaks.append(entries)
        self.peak_frames.append(temp_frame)
        temp_frame.pack(side=tk.TOP, padx=5)

    def remove_peak(self):
        if len(self.peak_frames) > 1:
            self.peak_frames[-1].destroy()
            del self.peak_frames[-1]

    def parse_peak_params(self, peak):
        return float(peak[1].get()), float(peak[2].get()), float(peak[3].get()), float(peak[4].get())

    def update_tailings(self):
        xvals = [x for x, _ in self.data]
        for peak in self.peaks:
            position, width, response, lamb = self.parse_peak_params(peak)
            if position!=0 and response !=0 and width!=0:
                temp_peak = expo_gauss_curve(xvals, position, width, response, lamb)
                peak[-1].set(round(find_asym(xvals, temp_peak),3))
        self.update_graph()

    def build_fit(self, xvals):
        fit_guess = [float(self.background.get()) for _ in self.data]
        for peak in self.peaks:
            position, width, response, lamb = self.parse_peak_params(peak)
            if position != 0 and response != 0 and width != 0:
                temp_peak = expo_gauss_curve(xvals, position, width, response, lamb)
                fit_guess = [sum(items) for items in zip(fit_guess, temp_peak)]
        return fit_guess

    def update_graph(self):
        self.ax.clear()
        xvals = [x for x, _ in self.data]
        yvals = [y for _, y in self.data]

        self.ax.plot(xvals,yvals)
        if len(self.peaks) > 0:
            fit_guess = self.build_fit(xvals)
            if sum(fit_guess) > 0:
                self.ax.plot(xvals, fit_guess)
        self.ax.set_ylim([self.ymin, self.ymax])
        self.canvas.draw()

    def run_fit(self):
        print("Begin curve fitting")
        user_guesses = [[float(ent.get()) for ent in peak[1:-1]] for peak in self.peaks]
        flat_guesses, bounds = process_guess_and_bounds(user_guesses)
        background = extract_background([val for index, val in enumerate(flat_guesses) if index%4==0], self.data)
        params, err = optimize.curve_fit(multi_expo_gauss_curve,
                                         [x for x, _ in self.data],
                                         [y-background for _, y in self.data],
                                         p0=flat_guesses,
                                         bounds=bounds)
        self.update_user_params(params)
        self.update_tailings()
        self.update_graph()
        print("Finished curve fitting")

    def update_user_params(self, params):
        for index in range(0, len(params), 4):
            self.peaks[index//4][1].delete(0, tk.END)
            self.peaks[index//4][2].delete(0, tk.END)
            self.peaks[index//4][3].delete(0, tk.END)
            self.peaks[index//4][4].delete(0, tk.END)
            self.peaks[index//4][1].insert(0, params[index])
            self.peaks[index//4][2].insert(0, params[index+1])
            self.peaks[index//4][3].insert(0, params[index+2])
            self.peaks[index//4][4].insert(0, params[index+3])

    def save_curve_fit(self):
        xvals = [x for x,_ in self.data]
        curve = self.build_fit(xvals)
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
        if filename is None:
            return
        for x, y in zip(xvals, curve):
            filename.write(f"{x},{y}\n")

        def save_params(self):
            filename = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
            if filename is None:
                return
            filename.write('name,position,width,response,lambda,asym\n')
            for peak in self.peaks:
                name = peak[0].get()
                position = peak[1].get()
                width = peak[2].get()
                response = peak[3].get()
                lamb = peak[4].get()
                asym = peak[5].get()
                filename.write(f"{name},{position},{width},{response},{lamb},{asym}\n")

