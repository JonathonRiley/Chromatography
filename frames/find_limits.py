import csv
import json
from math import inf
import numpy as np
import tkinter as tk
from tkinter import filedialog, StringVar, IntVar

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from resources.settings import BKG, LARGE_FONT, MEDIUM_FONT, SMALL_FONT
from resources.helper_functions import graph_zoom, expo_gauss_curve, multi_expo_gauss_curve, find_asym


class FindLimits(tk.Frame):
    def __init__(self, parent):
        self.peaks = []
        self.peak_frames = []
        self.buttons = []
        self.background = None
        self.data = [[x / 100, None] for x in range(60 * 100)]
        self.graph = None
        self.canvas = None
        self.xmin = 0
        self.xmax = 60
        self.ymax = 100
        self.ymin = -5
        self.tail = 1.01
        self.width = 0.01
        self.zoom = 0
        self.xlabels = ['Time (min)', "Tailing"]
        self.ylabels = ['Response', "Width"]
        self.f = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.f.add_subplot(111)
        self.ax2 = None
        self.ax.plot([], [])
        self.ax.set_xlim([self.xmin, self.xmax])
        self.ax.set_ylim([self.ymin, self.ymax])
        self.ax.set_xlabel(self.xlabels[0])
        self.ax.set_ylabel(self.ylabels[0])

        self.lamb_tail = self.load_lamb_tail()
        self.pv_widths = None
        self.pv_tails = None
        self.pv_fixed_width = None
        self.pv_fixed_tail = None

        self.res_widths = None
        self.res_tails = None
        self.res_fixed_width = None
        self.res_fixed_tail = None

        self.valleys = {float(width): {float(tail): None for tail in self.lamb_tail[width]} for width in self.lamb_tail}
        self.resolutions = {float(width): {float(tail): None for tail in self.lamb_tail[width]} for width in
                            self.lamb_tail}

        tk.Frame.__init__(self, parent)
        chart_frame = tk.Frame(self, width=900, height=600, relief=tk.SUNKEN, borderwidth=2)

        radio_btn_frame = tk.Frame(chart_frame)
        buttons = ['Chromatogram', 'Peak-Valley', 'Resolution']
        v = IntVar()
        for index in range(len(buttons)):
            radio_btn = tk.Radiobutton(master=radio_btn_frame, text=buttons[index], variable=v, value=index,
                                       command=lambda: self.update_graph())
            radio_btn.grid(row=0, column=index)
        self.buttons = v
        radio_btn_frame.pack(side=tk.TOP, pady=5)
        self.buttons.set(0)

        canvas_frame = tk.Frame(chart_frame)

        inner_canvas = tk.Frame(canvas_frame)
        canvas = FigureCanvasTkAgg(self.f, inner_canvas)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        chart_btn_frame = tk.Frame(inner_canvas, width=400)
        zoom_out_btn = tk.Button(chart_btn_frame, text="Zoom Out", command=lambda: graph_zoom(self, -1))
        zoom_out_btn.pack(side=tk.LEFT)
        zoom_in_btn = tk.Button(chart_btn_frame, text="Zoom In", command=lambda: graph_zoom(self, 1))
        zoom_in_btn.pack(side=tk.LEFT)
        chart_btn_frame.pack(side=tk.BOTTOM)
        inner_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scale_frame = tk.Frame(canvas_frame, height=600)
        refresh_btn = tk.Button(scale_frame, text="Refresh Graph", command=lambda: self.update_graph())
        refresh_btn.grid(row=0, column=0, columnspan=2)
        tk.Label(scale_frame, text="Width", font=SMALL_FONT).grid(row=1, column=0)
        tk.Label(scale_frame, text="Asym.", font=SMALL_FONT).grid(row=1, column=1)
        widths = sorted([float(x) for x in self.lamb_tail.keys()])
        width_step = abs(widths[0] - widths[1])
        tails = sorted([float(x) for x in self.lamb_tail[str(widths[0])].keys()])
        tail_step = abs(tails[0] - tails[1])
        width_scale = tk.Scale(scale_frame, from_=min(widths), to_=max(widths), resolution=width_step, length=320)
        width_scale.grid(row=2, column=0, padx=5)
        asym_scale = tk.Scale(scale_frame, from_=min(tails), to_=max(tails), resolution=tail_step, length=320)
        asym_scale.grid(row=2, column=1, padx=5)
        scale_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=20)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scales = [width_scale, asym_scale]
        self.canvas = canvas

        chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # add sidebar frame to contain peak parameters
        tools_frame = tk.Frame(self, width=450, bg=BKG)
        title = tk.Label(tools_frame, text="Find Limits", font=MEDIUM_FONT, bg=BKG)
        title.pack(pady=10, padx=10)

        top_btn_frame = tk.Frame(tools_frame, bg=BKG)
        load_params_btn = tk.Button(top_btn_frame, width=15, text="Load Parameters",
                                    command=lambda: self.load_params(tools_frame))
        load_params_btn.grid(row=0, column=0)
        load_params_btn.config(highlightbackground=BKG)
        save_curves_btn = tk.Button(top_btn_frame, width=15, text="Save Curves",
                                    command=lambda: self.save_curve_fit())
        save_curves_btn.config(highlightbackground=BKG)
        save_curves_btn.grid(row=0, column=1)

        add_btn = tk.Button(top_btn_frame, width=15, text="Add peak",
                            command=lambda: self.add_peak(tools_frame))
        add_btn.grid(row=1, column=0)
        add_btn.config(highlightbackground=BKG)

        remove_btn = tk.Button(top_btn_frame, width=15, text="Remove peak",
                               command=lambda: self.remove_peak())
        remove_btn.grid(row=1, column=1)
        remove_btn.config(highlightbackground=BKG)
        top_btn_frame.pack(side=tk.TOP)

        headers = ["Name", "Position", "Response"]

        headers_frame = tk.Frame(tools_frame, bg=BKG)
        bkg_label = tk.Label(headers_frame, text='Background', font=SMALL_FONT, bg=BKG, width=10)
        bkg_label.grid(row=0, column=1)
        sv = StringVar()
        sv.set(0)
        background = tk.Entry(headers_frame, textvariable=sv, width=5)
        self.background = background
        background.bind('<FocusOut>', (lambda _: self.update_graph()))
        background.config(highlightbackground=BKG)
        background.grid(row=0, column=2)
        for col in range(len(headers)):
            label = tk.Label(headers_frame, text=headers[col], font=SMALL_FONT, bg=BKG, width=8)
            label.grid(row=1, column=col)
        headers_frame.pack(side=tk.TOP, padx=5)

        # self.add_peak(tools_frame)

        from frames.home_page import HomePage
        home = tk.Button(tools_frame, text="Back to Home", command=lambda: parent.show_frame(HomePage))
        home.config(highlightbackground=BKG)
        home.pack(side=tk.BOTTOM)
        tools_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)

        self.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

    def load_lamb_tail(self):
        with open('resources/lambda_to_asym.json', 'r') as file:
            return json.load(file)

    def load_params(self, tools_frame):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file, delimiter=',')
            _ = next(csv_reader)
            params = [row for row in csv_reader]
        for name, position, response in params:
            self.add_peak(tools_frame, [name, position, response])

    def add_peak(self, frame, params=None):
        temp_frame = tk.Frame(frame, bg=BKG)
        mock_peaks = ['', 0, 0] if params is None else params
        entries = []
        for val in mock_peaks:
            sv = StringVar()
            sv.set(val)
            entry = tk.Entry(temp_frame, textvariable=sv, width=5)
            entry.bind('<FocusOut>', (lambda _: self.update_graph()))
            entry.config(highlightbackground=BKG)
            entries.append(entry)
            entry.pack(side=tk.LEFT, padx=11)
        self.peaks.append(entries)
        self.peak_frames.append(temp_frame)
        temp_frame.pack(side=tk.TOP, padx=5)

    def remove_peak(self):
        if len(self.peak_frames) > 1:
            self.peak_frames[-1].destroy()
            del self.peak_frames[-1]

    def parse_peak_params(self, peak):
        return float(peak[1].get()), float(peak[2].get())

    def find_HMFW(self, peak):
        peak_max = peak.index(max(peak))
        left = (np.abs(np.asarray(peak[:peak_max]) - 0.5 * peak[peak_max])).argmin()
        right = (np.abs(np.asarray(peak[peak_max:]) - 0.5 * peak[peak_max])).argmin()
        hmfw = np.abs(left - (peak_max+right))
        return peak_max, hmfw

    def build_curve(self, width, tailing, limit=None):
        if limit:
            xvals = [x for x, _ in self.data[::10]]
        else:
            xvals = [x for x, _ in self.data]
        fit_guess = [float(self.background.get()) for _ in xvals]
        peak_maxes = []
        peak_widths = []
        lamb = self.lamb_tail[str(width)][str(tailing)]['lambda']
        if lamb is not None:
            for peak in self.peaks:
                position, response = self.parse_peak_params(peak)
                if position != 0 and response != 0 and width != 0:
                    temp_peak = expo_gauss_curve(xvals, float(position), float(width), float(response), float(lamb))
                    peak_max, hmfw = self.find_HMFW(temp_peak)
                    peak_maxes.append(peak_max)
                    peak_widths.append(hmfw)
                    fit_guess = [sum(items) for items in zip(fit_guess, temp_peak)]
        else:
            fit_guess = [None for x, _ in self.data]
            peak_maxes = [None]
            peak_widths = [None]
        return fit_guess, peak_maxes, peak_widths

    def update_graph(self):
        try:
            self.ax.clear()
            self.ax2.clear()
            self.ax.set_xscale('linear')
        except:
            pass
        if self.buttons.get() == 0:
            xvals = [x for x, _ in self.data]
            width = self.scales[0].get()
            tail = self.scales[1].get()
            try:
                curve, peak_maxes, _ = self.build_curve(width, tail)
            except:
                curve = [None for _ in self.data]
                peak_maxes = [len(xvals) - 1]
            self.data = [[x, y] for x, y in zip(xvals, curve)]
            self.graph = [[x, y] for x, y in zip(xvals, curve)]
            self.ax.plot(xvals, curve)
            self.ax.set_xlim([0, max([xvals[index] for index in peak_maxes]) + 5])
            self.ax.set_ylim([self.ymin, self.ymax])
            self.ax.set_xlabel(self.xlabels[0])
            self.ax.set_ylabel(self.ylabels[0])
            self.canvas.draw()
            self.width = float(width)
            self.tail = float(tail)
        elif self.buttons.get() == 1:
            if self.pv_tails is not None and self.width == self.scales[0].get() and self.tail == self.scales[1].get():
                widths = self.pv_widths
                tails = self.pv_tails
                pv_ratios_fixed_tail = self.pv_fixed_tail
                pv_ratios_fixed_width = self.pv_fixed_width
            else:
                width = float(self.scales[0].get())
                tail = float(self.scales[1].get())
                self.tail = tail
                self.width = width
                pv_ratios_fixed_width = []
                pv_ratios_fixed_tail = []
                widths = []
                tails = []
                for temp_tail in self.lamb_tail[str(width)]:
                    try:
                        curve, peak_maxes, _ = self.build_curve(width, temp_tail, True)
                        min_valley_peak = inf
                        sorted_peaks = sorted(peak_maxes)
                        for index in range(len(sorted_peaks) - 2):
                            peak1 = curve[sorted_peaks[index]]
                            peak2 = curve[sorted_peaks[index + 1]]
                            valley = min(curve[sorted_peaks[index]:sorted_peaks[index + 1] + 1])
                            pv_ratio = min(peak1, peak2) / valley
                            if pv_ratio < min_valley_peak:
                                min_valley_peak = pv_ratio
                        pv_ratios_fixed_width.append(min_valley_peak)
                        tails.append(round(float(temp_tail),2))
                    except:
                        continue

                for temp_width in self.lamb_tail:
                    try:
                        curve, peak_maxes, _ = self.build_curve(float(temp_width), tail, True)
                        min_valley_peak = inf
                        sorted_peaks = sorted(peak_maxes)
                        for index in range(len(sorted_peaks) - 2):
                            peak1 = curve[sorted_peaks[index]]
                            peak2 = curve[sorted_peaks[index + 1]]
                            valley = min(curve[sorted_peaks[index]:sorted_peaks[index + 1] + 1])
                            pv_ratio = min(peak1, peak2) / valley
                            if pv_ratio < min_valley_peak:
                                min_valley_peak = pv_ratio
                        pv_ratios_fixed_tail.append(min_valley_peak)
                        widths.append(round(float(temp_width),2))
                    except:
                        continue
                self.pv_widths = widths
                self.pv_tails = tails
                self.pv_fixed_tail = pv_ratios_fixed_tail
                self.pv_fixed_width = pv_ratios_fixed_width
                self.graph = [[width, pv_fix_tail, tail, pv_fix_width]
                              for width, pv_fix_tail, tail, pv_fix_width
                              in zip(widths, pv_ratios_fixed_tail, tails, pv_ratios_fixed_width)]

            self.ax.set_xscale('linear')
            self.ax.clear()
            self.ax.plot(pv_ratios_fixed_width, tails, color='tab:green')
            self.ax.set_xlabel('Minimum Peak-to-Valley Ratio')
            self.ax.set_ylabel('Asym (5%)', color='tab:green')
            self.ax.set_xscale('log')
            if self.ax2 is None:
                self.ax2 = self.ax.twinx()
            self.ax2.plot(pv_ratios_fixed_tail, widths, color='tab:red')
            self.ax2.set_ylabel('Peak width (std. dev.)', color='tab:red')
            self.canvas.draw()

        elif self.buttons.get() == 2:
            if self.res_tails is not None and self.width == self.scales[0].get() and self.tail == self.scales[1].get():
                widths = self.res_widths
                tails = self.res_tails
                resolution_fixed_tail = self.res_fixed_tail
                resolution_fixed_width = self.res_fixed_width
            else:
                width = float(self.scales[0].get())
                tail = float(self.scales[1].get())
                self.tail = tail
                self.width = width
                resolution_fixed_width = []
                resolution_fixed_tail = []
                widths = []
                tails = []
                xvals = [x for x, _ in self.data]
                xstep = xvals[1]
                for temp_tail in self.lamb_tail[str(width)]:
                    try:
                        curve, peak_maxes, peak_widths = self.build_curve(width, temp_tail)
                        min_resolution = inf

                        sorted_peak_pos_widths = sorted([[xvals[pos], peak_width] for pos, peak_width in zip(peak_maxes, peak_widths)], key=lambda x: x[0])
                        for index in range(len(sorted_peak_pos_widths)-2):
                            peak1 = sorted_peak_pos_widths[index]
                            peak2 = sorted_peak_pos_widths[index+1]
                            resolution = abs(1.18 * (peak2[0] - peak1[0])/(peak2[1]*xstep+peak1[1]*xstep))
                            if resolution < min_resolution:
                                min_resolution = resolution
                        resolution_fixed_width.append(min_resolution)
                        tails.append(round(float(temp_tail),2))
                    except:
                        continue

                for temp_width in self.lamb_tail:
                    try:
                        _, peak_maxes, peak_widths = self.build_curve(temp_width, tail)
                        min_resolution = inf
                        sorted_peak_pos_widths = sorted([[xvals[pos], wid] for pos, wid in zip(peak_maxes, peak_widths)], key=lambda x: x[0])
                        for index in range(len(sorted_peak_pos_widths)-2):
                            peak1 = sorted_peak_pos_widths[index]
                            peak2 = sorted_peak_pos_widths[index+1]
                            resolution = abs(1.18 * (peak2[0] - peak1[0])/(peak2[1]*xstep+peak1[1]*xstep))
                            if resolution < min_resolution:
                                min_resolution = resolution
                        resolution_fixed_tail.append(min_resolution)
                        widths.append(round(float(temp_width), 2))
                    except:
                        continue
                self.res_widths = widths
                self.res_tails = tails
                self.res_fixed_tail = resolution_fixed_tail
                self.res_fixed_width = resolution_fixed_width
                self.graph = [[width, res_fix_tail, tail, res_fix_width]
                              for width, res_fix_tail, tail, res_fix_width
                              in zip(widths, resolution_fixed_tail, tails, resolution_fixed_width)]

            self.ax.set_xscale('linear')
            self.ax.clear()
            self.ax.plot(resolution_fixed_width, tails, color='tab:green')
            self.ax.set_xlabel('Minimum Resolution')
            self.ax.set_ylabel('Asym (5%)', color='tab:green')

            self.ax2.plot(resolution_fixed_tail, widths, color='tab:red')
            self.ax2.set_ylabel('Peak width (std. dev.)', color='tab:red')
            self.canvas.draw()

    def save_curve_fit(self):
        filename = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
        if filename is None:
            return
        if self.buttons.get() == 0:
            filename.write('time (min),response\n')
        elif self.buttons.get() == 1:
            filename.write('peak widths (min),peak valley ratio (fixed asym),peak asym,peak valley ratio (fixed width) \n')
        elif self.buttons.get() == 2:
            filename.write('peak widths (min),min. resolution (fixed asym),peak asym,min. resolution (fixed width) \n')
        for row in self.graph:
            filename.write(','.join([str(val) for val in row])+"\n")