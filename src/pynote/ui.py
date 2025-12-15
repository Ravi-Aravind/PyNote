# src/pynote/ui.py
"""
UI components (menus, dialogs) for PyNote.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog


class AboutDialog:
    """About dialog for PyNote."""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('About PyNote')
        self.dialog.geometry('300x200')
        self.dialog.resizable(False, False)
        self._create_widgets()
    
    def _create_widgets(self):
        tk.Label(
            self.dialog,
            text='PyNote',
            font=('Arial', 16, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            self.dialog,
            text='A Beginner-Friendly Desktop Text Editor',
            font=('Arial', 10)
        ).pack(pady=5)
        
        tk.Label(
            self.dialog,
            text='Version 0.1.0',
            font=('Arial', 9)
        ).pack(pady=5)
        
        tk.Label(
            self.dialog,
            text='Built with Python + Tkinter',
            font=('Arial', 8)
        ).pack(pady=5)
        
        tk.Button(
            self.dialog,
            text='OK',
            command=self.dialog.destroy,
            width=10
        ).pack(pady=20)


class GoToLineDialog:
    """Go to line number dialog."""
    
    def __init__(self, parent, max_lines):
        self.parent = parent
        self.max_lines = max_lines
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('Go to Line')
        self.dialog.geometry('250x100')
        self.dialog.resizable(False, False)
        self._create_widgets()
    
    def _create_widgets(self):
        tk.Label(
            self.dialog,
            text=f'Enter line number (1-{self.max_lines}):'
        ).pack(pady=10)
        
        self.entry = tk.Entry(self.dialog, width=20)
        self.entry.pack(pady=5)
        self.entry.focus()
        self.entry.bind('<Return>', lambda e: self._ok())
        
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text='OK',
            command=self._ok,
            width=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text='Cancel',
            command=self.dialog.destroy,
            width=8
        ).pack(side='left', padx=5)
    
    def _ok(self):
        try:
            line_num = int(self.entry.get())
            if 1 <= line_num <= self.max_lines:
                self.result = line_num
                self.dialog.destroy()
            else:
                messagebox.showerror(
                    'Error',
                    f'Line number must be between 1 and {self.max_lines}'
                )
        except ValueError:
            messagebox.showerror('Error', 'Please enter a valid number')


def show_about(parent):
    """Show about dialog."""
    AboutDialog(parent)


class ShortcutsDialog:
    """Keyboard shortcuts dialog."""

    def __init__(self, parent, is_mac=False):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title('Keyboard Shortcuts')
        self.dialog.geometry('380x320')
        self.dialog.resizable(False, False)
        self._create_widgets(is_mac)

    def _create_widgets(self, is_mac):
        tk.Label(
            self.dialog,
            text='Keyboard Shortcuts',
            font=('Arial', 14, 'bold')
        ).pack(pady=8)

        shortcuts = [
            ('File', [
                ('New', 'Cmd+N' if is_mac else 'Ctrl+N'),
                ('Open', 'Cmd+O' if is_mac else 'Ctrl+O'),
                ('Save', 'Cmd+S' if is_mac else 'Ctrl+S'),
                ('Save As', 'Cmd+Shift+S' if is_mac else 'Ctrl+Shift+S'),
            ]),
            ('Edit', [
                ('Undo', 'Cmd+Z' if is_mac else 'Ctrl+Z'),
                ('Redo', 'Cmd+Shift+Z' if is_mac else 'Ctrl+Y'),
            ]),
            ('View', [
                ('Toggle Status Bar', 'Cmd+B' if is_mac else 'Ctrl+B'),
            ]),
        ]

        for category, items in shortcuts:
            frame = tk.Frame(self.dialog)
            frame.pack(fill='x', padx=12, pady=4)
            tk.Label(frame, text=category, font=('Arial', 11, 'bold')).pack(anchor='w')
            for name, key in items:
                row = tk.Frame(frame)
                row.pack(fill='x', pady=1)
                tk.Label(row, text=name, width=18, anchor='w').pack(side='left')
                tk.Label(row, text=key, anchor='w', font=('Arial', 9)).pack(side='left')

        tk.Button(
            self.dialog,
            text='OK',
            command=self.dialog.destroy,
            width=10
        ).pack(pady=12)


def show_shortcuts(parent, is_mac=False):
    """Show keyboard shortcuts dialog."""
    dlg = ShortcutsDialog(parent, is_mac=is_mac)
    parent.wait_window(dlg.dialog)

