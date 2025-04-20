import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import pygments
from pygments.lexers import get_lexer_by_name
import os


class CodeEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ProEdit")
        self.geometry("800x600")

        # Initialize notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}  # dictionary to store references for each tab

        # Set up menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Tab", command=self.new_tab)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_editor)

        self.edit_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Find", command=self.search_text)
        self.edit_menu.add_command(label="Replace", command=self.replace_text)

        self.language_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Language", menu=self.language_menu)
        self.language_menu.add_command(label="Python", command=lambda: self.change_language("python"))
        self.language_menu.add_command(label="JavaScript", command=lambda: self.change_language("javascript"))
        self.language_menu.add_command(label="C", command=lambda: self.change_language("c"))
        self.language_menu.add_command(label="HTML", command=lambda: self.change_language("html"))
        self.language_menu.add_command(label="CSS", command=lambda: self.change_language("css"))

        # Initialize first tab
        self.new_tab()
        
    def update_line_numbers(self, text_area, line_numbers):
        if text_area is None or line_numbers is None:
            return
        line_numbers.config(state='normal')
        line_numbers.delete(1.0, tk.END)
        line_count = text_area.index('end-1c').split('.')[0]
        lines = "\n".join(str(i) for i in range(1, int(line_count) + 1))
        line_numbers.insert(1.0, lines)
        line_numbers.config(state='disabled')


    def new_tab(self):
        tab_id = len(self.tabs) + 1
        tab_name = f"Untitled-{tab_id}"
        tab_frame = ttk.Frame(self.notebook)

        self.notebook.add(tab_frame, text=tab_name)
        self.notebook.select(tab_frame)

        container = tk.Frame(tab_frame)
        container.pack(fill=tk.BOTH, expand=True)

        shared_font = ("Consolas", 12)

        # Line numbers widget
        line_numbers = tk.Text(container, width=4, padx=4, takefocus=0, border=0,
                               background="#f0f0f0", state='disabled', wrap='none', font=shared_font)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text area
        text_area = tk.Text(container, wrap=tk.NONE, font=shared_font, undo=True)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vertical scrollbar
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Scroll sync
        text_area.config(yscrollcommand=lambda *args: self._on_textscroll(*args, widget=line_numbers))
        line_numbers.config(yscrollcommand=lambda *args: self._on_textscroll(*args, widget=text_area))
        scrollbar.config(command=lambda *args: self._on_scroll(*args, text_widget=text_area, line_widget=line_numbers))

        # Bindings
        text_area.bind("<KeyRelease>", lambda e: self.update_line_numbers(text_area, line_numbers))
        text_area.bind("<MouseWheel>", lambda e: self._on_mouse_wheel(e, text_area, line_numbers))
        line_numbers.bind("<MouseWheel>", lambda e: self._on_mouse_wheel(e, text_area, line_numbers))

        # Store tab data
        self.tabs[tab_name] = {
            "text_area": text_area,
            "line_numbers": line_numbers,
            "file_path": None
        }

        # Initial line numbers update
        self.update_line_numbers(text_area, line_numbers)

        
    def on_scroll(*args):
        text_area.yview(*args)
        line_numbers.yview(*args)

        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=on_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_area.config(yscrollcommand=scrollbar.set)
        line_numbers.config(yscrollcommand=scrollbar.set)
        
        text_area.bind("<MouseWheel>", lambda e: self._on_mouse_wheel(e, text_area, line_numbers))
        line_numbers.bind("<MouseWheel>", lambda e: self._on_mouse_wheel(e, text_area, line_numbers))



        # Bind events
        text_area.bind("<MouseWheel>", lambda e: self._on_mouse_wheel(e, text_area, line_numbers))
        line_numbers.bind("<MouseWheel>", lambda e: self._on_mouse_wheel(e, text_area, line_numbers))

        self.notebook.add(tab_frame, text=tab_name)
        self.tabs[tab_name] = {
            "text_area": text_area,
            "line_numbers": line_numbers,
            "file_path": None
        }
        self.notebook.select(tab_frame)

        # Initial line number update
        self.update_line_numbers(text_area, line_numbers)
        
    
    def _on_scroll(self, *args, text_widget=None, line_widget=None):
        if text_widget:
            text_widget.yview(*args)
        if line_widget:
            line_widget.yview(*args)

    def _on_textscroll(self, first, last, widget):
        widget.yview_moveto(first)

    def _on_mouse_wheel(self, event, text_widget, line_widget):
        delta = int(-1 * (event.delta / 120))
        text_widget.yview_scroll(delta, "units")
        line_widget.yview_scroll(delta, "units")
        return "break"
    
        
    def _on_mouse_wheel(self, event, text_area, line_numbers):
        text_area.yview_scroll(int(-1 * (event.delta / 120)), "units")
        line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"


    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt;*.py;*.html;*.css;*.js;*.c")])
        if file_path:
            with open(file_path, "r") as file:
                code = file.read()
            text_area = self.get_active_text_area()
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, code)
            self.tabs[self.get_active_tab()]["file_path"] = file_path

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt;*.py;*.html;*.css;*.js;*.c")])
        if file_path:
            text_area = self.get_active_text_area()
            code = text_area.get(1.0, tk.END)
            with open(file_path, "w") as file:
                file.write(code)
            self.tabs[self.get_active_tab()]["file_path"] = file_path

    def exit_editor(self):
        self.quit()

    def search_text(self):
        search_term = simpledialog.askstring("Search", "Enter search term:")
        if search_term:
            text_area = self.get_active_text_area()
            text_area.tag_remove("found", "1.0", tk.END)
            start = "1.0"
            while True:
                start = text_area.search(search_term, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(search_term)}c"
                text_area.tag_add("found", start, end)
                start = end
            text_area.tag_config("found", background="yellow", foreground="black")

    def replace_text(self):
        search_term = simpledialog.askstring("Find and Replace", "Enter search term:")
        if search_term:
            replace_term = simpledialog.askstring("Find and Replace", "Enter replacement term:")
            if replace_term:
                text_area = self.get_active_text_area()
                content = text_area.get(1.0, tk.END)
                new_content = content.replace(search_term, replace_term)
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, new_content)

    def get_active_text_area(self):
        tab_name = self.get_active_tab()
        return self.tabs[tab_name]["text_area"]

    def get_active_tab(self):
        return self.notebook.tab(self.notebook.select(), "text")

    def change_language(self, language):
        try:
            lexer = get_lexer_by_name(language)
            text_area = self.get_active_text_area()
            code = text_area.get(1.0, tk.END)
            highlighted_code = pygments.highlight(code, lexer, pygments.formatters.HtmlFormatter())
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, highlighted_code)
        except Exception as e:
            messagebox.showerror("Error", f"Unsupported language: {language} - {e}")

if __name__ == "__main__":
    app = CodeEditor()
    app.mainloop()
