# src/pynote/main.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
try:
    from . import utils
    from . import themes
except Exception:
    # Fallback for running as a script directly
    import os, sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pynote import utils, themes

APP_TITLE = "PyNote"


class PyNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry('800x600')
        self._filepath = None
        # Settings and theme
        self.settings = utils.load_settings()
        self.current_theme_name = self.settings.get('theme', 'light')
        self.dark_mode = tk.BooleanVar(value=(self.current_theme_name.lower() == 'dark'))
        self.style = ttk.Style(self)
        # Using emoji icons for consistency across platforms
        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()
        self._apply_theme()

    def _create_widgets(self):
        # Toolbar with small icon buttons
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(side='top', fill='x')

        # Emoji-based small buttons (📄 New, 📂 Open, 💾 Save)
        btn_new = ttk.Button(self.toolbar, text='📄', width=3, command=self.new_file)
        btn_open = ttk.Button(self.toolbar, text='📂', width=3, command=self.open_file)
        btn_save = ttk.Button(self.toolbar, text='💾', width=3, command=self.save_file)

        for b in (btn_new, btn_open, btn_save):
            b.pack(side='left', padx=4, pady=4)

        # Text widget with scrollbar
        self.text = tk.Text(self, wrap='word', undo=True)
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='left', fill='both', expand=True)

        # status bar
        self.status = tk.StringVar()
        self.status.set('Ln 1, Col 0 | Words: 0 | Chars: 0')
        self.status_bar = ttk.Label(self, textvariable=self.status, anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

        # update cursor position
        self.text.bind('<KeyRelease>', self._update_status)
        self.text.bind('<ButtonRelease>', self._update_status)

    def _create_menu(self):
        menu = tk.Menu(self)
        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label='New', command=self.new_file)
        filemenu.add_command(label='Open', command=self.open_file)
        filemenu.add_command(label='Save', command=self.save_file)
        filemenu.add_command(label='Save As', command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self.quit)
        menu.add_cascade(label='File', menu=filemenu)

        viewmenu = tk.Menu(menu, tearoff=0)
        viewmenu.add_checkbutton(label='Dark Mode', variable=self.dark_mode, command=self._toggle_dark_mode)
        menu.add_cascade(label='View', menu=viewmenu)
        self.config(menu=menu)

    def _bind_shortcuts(self):
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-n>', lambda e: self.new_file())
        # macOS Command key support
        self.bind('<Command-n>', lambda e: self.new_file())
        self.bind('<Control-z>', lambda e: self.text.event_generate('<<Undo>>'))
        self.bind('<Control-y>', lambda e: self.text.event_generate('<<Redo>>'))

    def _load_icons(self):
        # Deprecated: image-based icons removed to avoid TclError on some platforms
        # Kept for compatibility; no-op.
        pass

    def _apply_theme(self):
        name = 'dark' if self.dark_mode.get() else 'light'
        theme = themes.get_theme(name)
        # Apply to text widget
        themes.apply_theme(self.text, theme)
        # Apply to root window background
        self.configure(bg=theme['bg'])
        # Apply to toolbar and status bar via ttk styles
        # Use a custom style to avoid clobbering global styles
        self.style.theme_use(self.style.theme_use())
        self.style.configure('PyNote.TFrame', background=theme['status_bg'])
        self.style.configure('PyNote.TLabel', background=theme['status_bg'], foreground=theme['status_fg'])
        self.toolbar.configure(style='PyNote.TFrame')
        self.status_bar.configure(style='PyNote.TLabel')
        # Scrollbar colors (best-effort; may vary by platform/theme)
        try:
            self.style.configure('Vertical.TScrollbar', background=theme['gutter_bg'], troughcolor=theme['gutter_bg'])
        except Exception:
            pass

    def _toggle_dark_mode(self):
        self.current_theme_name = 'dark' if self.dark_mode.get() else 'light'
        # Save preference
        self.settings['theme'] = self.current_theme_name
        utils.save_settings(self.settings)
        # Apply
        self._apply_theme()

    def new_file(self):
        if self._confirm_discard():
            self.text.delete('1.0', tk.END)
            self._filepath = None
            self.title(APP_TITLE)
            self._update_status()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.text.delete('1.0', tk.END)
                self.text.insert('1.0', data)
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
                self._update_status()
            except Exception as e:
                messagebox.showerror('Error', f'Failed to open file: {str(e)}')

    def save_file(self):
        if self._filepath:
            try:
                with open(self._filepath, 'w', encoding='utf-8') as f:
                    f.write(self.text.get('1.0', tk.END))
                self.text.edit_modified(False)
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')
        else:
            self.save_as()

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Text Files', '*.txt;*.md;*.py'), ('All Files', '*.*')]
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text.get('1.0', tk.END))
                self._filepath = path
                self.title(f"{APP_TITLE} - {path}")
                self.text.edit_modified(False)
                messagebox.showinfo('Saved', 'File saved successfully')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {str(e)}')

    def _update_status(self, event=None):
        idx = self.text.index(tk.INSERT).split('.')
        line = idx[0]
        col = idx[1]
        content = self.text.get('1.0', 'end-1c')
        try:
            words = utils.count_words(content)
            chars = utils.count_chars(content)
        except Exception:
            # Fallback in unlikely event utils isn't available
            words = len(content.split())
            chars = len(content)
        self.status.set(f'Ln {line}, Col {col} | Words: {words} | Chars: {chars}')

    def _confirm_discard(self):
        if self.text.edit_modified():
            resp = messagebox.askyesnocancel(
                'Unsaved changes',
                'You have unsaved changes. Save before continuing?'
            )
            if resp is None:
                return False
            if resp:
                self.save_file()
        return True


if __name__ == '__main__':
    app = PyNoteApp()
    app.mainloop()

