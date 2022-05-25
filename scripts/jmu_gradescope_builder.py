#!/usr/bin/env python
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path
import subprocess
import platform
import os
import jmu_gradescope_utils.build_utils as build_utils


def open_file(file_path):
    if platform.system() == 'Windows':
        os.startfile(file_path)
    elif platform.system() == 'Darwin':
        subprocess.run(['open', str(file_path)])
    else:  # Linux
        subprocess.run(['xdg-open', str(file_path)])


class LoggingHandlerFrame(ttk.Frame):
    # https://stackoverflow.com/a/37188648

    class WidgetLogger(logging.Handler):
        def __init__(self, widget):
            logging.Handler.__init__(self)
            self.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            self.setFormatter(formatter)
            self.widget = widget
            self.widget.config(state='disabled')
            self.widget.tag_config("INFO", foreground="black")
            self.widget.tag_config("DEBUG", foreground="grey")
            self.widget.tag_config("WARNING", foreground="orange")
            self.widget.tag_config("ERROR", foreground="red")
            self.widget.tag_config("CRITICAL", foreground="red", underline=1)
            self.red = self.widget.tag_configure("red", foreground="red")

        def emit(self, record):
            self.widget.config(state='normal')
            # Append message (record) to the widget
            self.widget.insert(tk.END, self.format(record) + '\n',
                               record.levelname)
            self.widget.see(tk.END)  # Scroll to the bottom
            self.widget.config(state='disabled')
            self.widget.update()  # Refresh the widget

    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.scrollbar_y = tk.Scrollbar(self)
        self.scrollbar_x = tk.Scrollbar(self, orient='horizontal')
        self.scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E))
        self.scrollbar_x.grid(row=1, column=0, sticky=(tk.S, tk.E, tk.W))

        self.text = tk.Text(self, xscrollcommand=self.scrollbar_x.set,
                            yscrollcommand=self.scrollbar_y.set, wrap="none")
        self.text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        self.scrollbar_y.config(command=self.text.yview)
        self.scrollbar_x.config(command=self.text.xview)

        self.logging_handler = LoggingHandlerFrame.WidgetLogger(self.text)


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Python Gradescope Submission Builder')
        self.geometry('640x480')
        self.resizable(True, True)

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Select Autograder Folder...",
                             command=self.select_autograder)
        filemenu.add_command(label="Select Sample Submission...",
                             command=self.select_sample_submission)
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

        path_frame = ttk.Frame(self)
        path_frame.columnconfigure(0, weight=0)
        path_frame.columnconfigure(1, weight=1)
        label = ttk.Label(path_frame, text='Autograder:')
        label.grid(row=0, column=0, padx=4, pady=10, sticky="w")
        self.grader_path_text = tk.Text(path_frame, height=1,
                                        bg="gray95")

        self.grader_path_text.grid(row=0, column=1, padx=4, pady=10)

        label = ttk.Label(path_frame, text='Sample Submission:')
        label.grid(row=1, column=0, padx=4, pady=10, sticky="w")
        self.sample_path_text = tk.Text(path_frame, height=1,
                                        bg="gray95")
        self.sample_path_text.grid(row=1, column=1, padx=4, pady=10,
                                   sticky="w")

        path_frame.pack(side=tk.TOP)

        button_frame = ttk.Frame(self)
        self.test_button = ttk.Button(button_frame, text='Test Autograder',
                                      command=self.test)
        self.test_button.pack(side=tk.LEFT, padx=4, pady=10)
        self.test_button["state"] = "disabled"

        self.build_button = ttk.Button(button_frame, text='Build Autograder',
                                       command=self.build)
        self.build_button["state"] = "disabled"
        self.build_button.pack(side=tk.LEFT, padx=4, pady=10)

        button_frame.pack(side=tk.TOP)

        log_frame = tk.LabelFrame(self, text="Log Data")

        logwidget = LoggingHandlerFrame(log_frame, width=80, height=24)
        logger = logging.getLogger()
        logging.basicConfig(level=logging.INFO)
        logger.addHandler(logwidget.logging_handler)
        logwidget.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        log_frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH,
                       padx=4, pady=10)

    def test(self):
        autograder_folder = self.grader_path_text.get("1.0", 'end-1c')
        sample_folder = self.sample_path_text.get("1.0", 'end-1c')
        result_json_loc = build_utils.test_autograder(autograder_folder,
                                                      sample_folder)
        open_file(result_json_loc)

    def build(self):

        autograder_folder = self.grader_path_text.get("1.0", 'end-1c')
        autograder_path = Path(autograder_folder)
        name = 'autograder_' + str(autograder_path.name) + ".zip"
        default = autograder_path / name
        zipfile = fd.asksaveasfilename(filetypes=[("Zip file", ".zip")],
                                       initialdir=autograder_folder,
                                       initialfile=default)
        if len(zipfile) > 0:
            build_utils.build_zip(autograder_folder, zipfile)

    def select_autograder(self):
        folder = fd.askdirectory(title='Select Autograder Folder')
        if len(folder) > 0:
            self.build_button["state"] = "enable"

            self.grader_path_text.config(state=tk.NORMAL)
            self.grader_path_text.delete(1.0, "end")
            self.grader_path_text.insert(1.0, folder)
            self.grader_path_text.config(state=tk.DISABLED)

            cur_sample = self.sample_path_text.get("1.0", 'end-1c')
            if len(cur_sample) == 0:
                p = Path(folder)
                possible_sample = p / 'sample'
                if possible_sample.exists() and possible_sample.is_dir():
                    self.test_button["state"] = "enable"
                    self.sample_path_text.config(state=tk.NORMAL)
                    self.sample_path_text.delete(1.0, "end")
                    self.sample_path_text.insert(1.0, str(possible_sample))
                    self.sample_path_text.config(state=tk.DISABLED)

    def select_sample_submission(self):
        folder = fd.askdirectory(title='Select Sample Submission')

        if len(folder) > 0:
            self.test_button["state"] = "enable"
            self.sample_path_text.config(state=tk.NORMAL)
            self.sample_path_text.delete(1.0, "end")
            self.sample_path_text.insert(1.0, folder)
            self.sample_path_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = App()
    app.mainloop()
