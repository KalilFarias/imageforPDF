"""
Gerador de PDF com Template
Copyright (c) 2026 Kalil Farias
Todos os direitos reservados.

Este software é protegido por direitos autorais.
É proibida a reprodução, modificação ou redistribuição
sem autorização do autor.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

from script import main as gerar_pdfs


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de PDF com Template")
        self.root.geometry("700x580")
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap("icone.ico")
        except:
            pass

        self.base_dirs = []
        self.template_path = ""

        self.build_ui()

    def build_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        tk.Label(
            content_frame,
            text="Pastas com fotos:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        frame = tk.Frame(content_frame)
        frame.pack(fill="both", expand=True, padx=10)

        self.listbox = tk.Listbox(frame, height=10)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        tk.Button(
            content_frame,
            text="➕ Adicionar Pasta",
            command=self.add_folders
        ).pack(pady=5)

        tk.Button(
            content_frame,
            text="🧹 Limpar Lista",
            command=self.clear_list
        ).pack(pady=3)

        tk.Label(
            content_frame,
            text="Template PDF:",
            font=("Arial", 12, "bold")
        ).pack(pady=8)

        self.template_label = tk.Label(
            content_frame,
            text="Nenhum template selecionado"
        )
        self.template_label.pack()

        tk.Button(
            content_frame,
            text="📄 Selecionar Template",
            command=self.select_template
        ).pack(pady=5)

        self.progress = ttk.Progressbar(
            content_frame,
            orient="horizontal",
            length=450,
            mode="determinate"
        )
        self.progress.pack(pady=15)

        self.btn_gerar = tk.Button(
            content_frame,
            text="🚀 Gerar PDFs",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.run_script
        )
        self.btn_gerar.pack(pady=10)

        footer = tk.Label(
            main_frame,
            text="© 2026 ASTETI (POLCAL) - Todos os direitos reservados",
            font=("Arial", 8),
            fg="#666666"
        )
        footer.pack(side="bottom", fill="x", pady=5)

    def add_folders(self):
        folder = filedialog.askdirectory(mustexist=True)
        if folder and folder not in self.base_dirs:
            self.base_dirs.append(folder)
            self.listbox.insert(tk.END, folder)

    def clear_list(self):
        self.base_dirs.clear()
        self.listbox.delete(0, tk.END)

    def select_template(self):
        path = filedialog.askopenfilename(
            title="Selecione o Template PDF",
            filetypes=[("PDF", "*.pdf")]
        )
        if path:
            self.template_path = path
            self.template_label.config(text=path)

    def run_script(self):
        if not self.base_dirs:
            messagebox.showerror("Erro", "Selecione pelo menos uma pasta.")
            return

        if not self.template_path:
            messagebox.showerror("Erro", "Selecione o template PDF.")
            return

        try:
            self.btn_gerar.config(state="disabled")
            self.progress["maximum"] = len(self.base_dirs)
            self.progress["value"] = 0

            for i, pasta in enumerate(self.base_dirs):
                gerar_pdfs(pasta, self.template_path)
                self.progress["value"] = i + 1
                self.root.update_idletasks()

            messagebox.showinfo("Sucesso", "PDFs gerados com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro:\n{e}")

        finally:
            self.btn_gerar.config(state="normal")
            self.progress["value"] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()