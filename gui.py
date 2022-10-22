import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import os

from settings import Settings
import utils


class App:
    FONT = ('Helvetica', '16')

    def __init__(self):
        self.settings = Settings()
        self.window = tk.Tk()
        self.frame = ttk.Frame(self.window, padding='5')

        self.config_window()
        self.config_window_frame()
        self.input_directory_selection = DirectorySelection(self, 'Select Source:')
        self.output_directory_selection = DirectorySelection(self, 'Select Destination:', padding='0 2 0 0')
        self.options_menu = OptionsMenu(self, padding='0 2 0 0')
        self.patterns = Patterns(self, padding='0 2 0 0')
        self.actions = Actions(self, padding='0 2 0 0')
        self.configure_rows()
        self.options_menu.set_mode()

    def run(self):
        self.window.mainloop()

    def config_window(self):
        self.window.title('Regex File Utilities')
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.geometry('800x600')
        s = ttk.Style()
        s.configure('.', font=App.FONT)  # change root style, which configures all widgets

    def config_window_frame(self):
        self.frame.grid(column=0, row=0, sticky='NESW')
        self.frame.rowconfigure(0, weight=0)
        self.frame.columnconfigure(0, weight=1)

    def configure_rows(self):
        self.input_directory_selection.grid(row=0, column=0, sticky='NEW')
        self.output_directory_selection.grid(row=1, column=0, sticky='NEW')
        self.options_menu.grid(row=2, column=0, sticky='NEW')
        self.patterns.grid(row=3, column=0, sticky='NEW')
        self.actions.grid(row=4, column=0, sticky='NEW')


class DirectorySelection(ttk.Frame):
    def __init__(self, parent, button_text, *args, **kwargs):
        super().__init__(parent.frame, *args, **kwargs)
        self.directory = tk.StringVar()
        self.button = ttk.Button(self, text=button_text, command=self.set_dir)
        self.entry = ttk.Entry(self, textvariable=self.directory, font=parent.FONT)

        self.button.grid(row=0, column=0, sticky='NESW')
        self.entry.grid(row=0, column=1, sticky='NESW')
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

    def set_dir(self):
        self.directory.set(tk.filedialog.askdirectory(mustexist=True))


class OptionsMenu(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent.frame, *args, **kwargs)
        self.parent = parent
        self.mode = tk.StringVar()
        self.recursive = tk.BooleanVar()
        self.skip_errors = tk.BooleanVar()
        self.file_and_folder = tk.StringVar()

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.setup_mode()
        self.setup_checkbuttons()
        self.setup_radios()

    def setup_mode(self):
        self.mode.set(self.parent.settings.mode)

        mode_label = ttk.Label(self, text='Mode:')
        mode_label.grid(row=0, column=0)

        set_mode_combo = ttk.Combobox(self, textvariable=self.mode, font=self.parent.FONT, width=10)
        set_mode_combo['values'] = self.parent.settings.modes
        set_mode_combo.state(['readonly'])
        set_mode_combo.bind('<<ComboboxSelected>>', self.set_mode)
        set_mode_combo.grid(row=0, column=1)

    def setup_checkbuttons(self):
        checkbutton_frame = ttk.Frame(self)
        for row in range(0, 3):
            checkbutton_frame.rowconfigure(row, weight=1)
        checkbutton_frame.grid(row=0, column=2)

        recursive_checkbutton = ttk.Checkbutton(checkbutton_frame, text='Recursive (enter sub-folders)',
                                                onvalue=True, offvalue=False, variable=self.recursive,
                                                command=self.set_recursive)
        recursive_checkbutton.grid(row=0, sticky='W')

        skip_errors_checkbutton = ttk.Checkbutton(checkbutton_frame, text='Continue on error',
                                                  onvalue=True, offvalue=False, variable=self.skip_errors,
                                                  command=self.set_skip_errors)
        skip_errors_checkbutton.grid(row=1, sticky='W')

    def setup_radios(self):
        radio_frame = ttk.Frame(self)
        for row in range(0, 3):
            radio_frame.rowconfigure(row, weight=1)
        radio_frame.grid(row=0, column=3)

        self.file_and_folder.set(self.parent.settings.file_mode)
        radio_file = ttk.Radiobutton(radio_frame, text='Files only', variable=self.file_and_folder,
                                     value='files', command=self.set_file_folder)
        radio_folder = ttk.Radiobutton(radio_frame, text='Folders only', variable=self.file_and_folder,
                                       value='folders', command=self.set_file_folder)
        radio_both = ttk.Radiobutton(radio_frame, text='Both', variable=self.file_and_folder,
                                     value='both', command=self.set_file_folder)
        radio_file.grid(row=0, sticky='W')
        radio_folder.grid(row=1, sticky='W')
        radio_both.grid(row=2, sticky='W')

    def set_mode(self, *_):
        self.parent.settings.mode = self.mode.get()
        output_pattern_status = 'enabled' if self.parent.settings.mode == 'rename' else 'disabled'
        self.parent.patterns.output_entry.config(state=output_pattern_status)
        output_dir_status = 'disabled' if self.parent.settings.mode in ['rename', 'delete'] else 'enabled'
        self.parent.output_directory_selection.entry.config(state=output_dir_status)
        self.parent.output_directory_selection.button.config(state=output_dir_status)

    def set_recursive(self):
        self.parent.settings.recursive = self.recursive.get()

    def set_skip_errors(self):
        self.parent.settings.skip_errors = self.skip_errors.get()

    def set_file_folder(self):
        self.parent.settings.file_mode = self.file_and_folder.get()


class Patterns(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent.frame, *args, **kwargs)
        self.input = tk.StringVar()
        self.output = tk.StringVar()
        self.output_entry = ttk.Entry(self, textvariable=self.output, font=parent.FONT)
        input_entry = ttk.Entry(self, textvariable=self.input, font=parent.FONT)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text='Input pattern:').grid(row=0, column=0)
        ttk.Label(self, text='Output pattern:').grid(row=0, column=1)
        input_entry.grid(row=1, column=0, sticky='NESW', padx=2)
        self.output_entry.grid(row=1, column=1, sticky='NESW', padx=2)


class Actions(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent.frame, *args, **kwargs)
        self.parent = parent
        self.run_button = ttk.Button(self, text='Run', command=self.run)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.run_button.grid(row=0, column=0, sticky='W')

    # TODO: thread this: disable the run button, run the threaded task, re-enable the run button upon completion
    def run(self):
        in_dir = self.parent.input_directory_selection.directory.get()
        in_pattern = self.parent.patterns.input.get()
        if not os.path.exists(in_dir) or not os.path.isdir(in_dir):
            utils.set_last_err(NotADirectoryError('Input directory does not exist'))
            return
        if not in_pattern:
            utils.set_last_err(Exception('Input pattern is required'))
            return

        mode = self.parent.settings.mode
        out_dir = ''
        if mode in ['move', 'copy']:
            out_dir = self.parent.output_directory_selection.directory.get()
            if not os.path.exists(out_dir) or not os.path.isdir(out_dir):
                utils.set_last_err(NotADirectoryError('Output directory does not exist'))
                return

        settings = self.parent.settings
        if mode == 'rename':
            out_pattern = self.parent.patterns.output.get()
            utils.run_rename(in_dir, in_pattern, out_pattern, settings)
        elif mode == 'delete':
            utils.run_delete(in_dir, in_pattern, settings)
        elif mode == 'move':
            utils.run_copy_or_move(in_dir, in_pattern, out_dir, settings, copy=False)
        elif mode == 'copy':
            utils.run_copy_or_move(in_dir, in_pattern, out_dir, settings, copy=True)
