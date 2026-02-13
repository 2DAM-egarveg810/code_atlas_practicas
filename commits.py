#!/usr/bin/env python3
import os
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class GitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Commit & Push")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Directorio actual (repositorio Git)
        self.repo_path = os.getcwd()
        
        self.create_widgets()
        self.validate_git_repo()
    
    def validate_git_repo(self):
        """Verifica que el directorio actual sea un repositorio Git válido"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_path,
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            messagebox.showerror(
                "Error",
                f"No es un repositorio Git válido.\n\nDirectorio actual:\n{self.repo_path}"
            )
            self.disable_controls()
    
    def disable_controls(self):
        """Deshabilita controles si no es repositorio válido"""
        for widget in [self.commit_btn, self.push_btn, self.status_btn]:
            widget.config(state="disabled")
    
    def create_widgets(self):
        # Frame superior: información del repositorio
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text="Repositorio:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(top_frame, text=self.repo_path, wraplength=550).pack(anchor="w")

        ttk.Label(top_frame, text="Tipos:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(top_frame, text="fix: corrección de bug\nui: cambios visuales\nmap: mapaLeaflet\nauth: autenticación\nrefactor: mejorar código\ndocs: documentación\nconfig: configuración\nchore: mantenimiento", wraplength=550).pack(anchor="w")

        # Frame para mensaje de commit
        msg_frame = ttk.LabelFrame(self.root, text=" Mensaje de Commit ", padding=10)
        msg_frame.pack(fill="x", padx=10, pady=5)
        
        # Título (línea 1)
        ttk.Label(msg_frame, text="Título (máx 50-75 caracteres):").pack(anchor="w")
        self.title_entry = ttk.Entry(msg_frame, width=70)
        self.title_entry.pack(fill="x", pady=(0, 5))
        self.title_entry.bind("<KeyRelease>", self.update_preview)
        
        # Cuerpo (líneas adicionales)
        ttk.Label(msg_frame, text="Descripción (opcional):").pack(anchor="w", pady=(5, 0))
        self.body_text = scrolledtext.ScrolledText(msg_frame, height=6, width=70, wrap="word")
        self.body_text.pack(fill="both", expand=True, pady=(0, 5))
        self.body_text.bind("<KeyRelease>", self.update_preview)
        
        # Vista previa del mensaje
        ttk.Label(msg_frame, text="Vista previa:", font=("Arial", 9, "italic")).pack(anchor="w")
        self.preview_text = scrolledtext.ScrolledText(msg_frame, height=4, width=70, wrap="word", bg="#f0f0f0")
        self.preview_text.pack(fill="x")
        self.preview_text.config(state="disabled")
        
        # Frame de botones
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_btn = ttk.Button(btn_frame, text="Ver Estado", command=self.git_status)
        self.status_btn.pack(side="left", padx=5)
        
        self.commit_btn = ttk.Button(btn_frame, text="Commit", command=self.git_commit)
        self.commit_btn.pack(side="left", padx=5)
        
        self.push_btn = ttk.Button(btn_frame, text="Push", command=self.git_push)
        self.push_btn.pack(side="left", padx=5)
        
        # Área de resultados/salida
        result_frame = ttk.LabelFrame(self.root, text=" Resultados ", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=8, width=70, wrap="word")
        self.result_text.pack(fill="both", expand=True)
        self.result_text.config(state="disabled")
    
    def update_preview(self, event=None):
        """Actualiza la vista previa del mensaje de commit"""
        title = self.title_entry.get().strip()
        body = self.body_text.get("1.0", "end-1c").strip()
        
        preview = title
        if body:
            preview += "\n\n" + body
        
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", preview)
        self.preview_text.config(state="disabled")
    
    def append_result(self, text, clear=False):
        """Añade texto al área de resultados"""
        self.result_text.config(state="normal")
        if clear:
            self.result_text.delete("1.0", "end")
        self.result_text.insert("end", text + "\n")
        self.result_text.see("end")
        self.result_text.config(state="disabled")
        self.root.update()
    
    def run_git_command(self, command):
        """Ejecuta un comando git y retorna (success, output)"""
        try:
            self.append_result(f"$ {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                if result.stdout.strip():
                    self.append_result(result.stdout)
                return True, result.stdout
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                self.append_result(f"Error:\n{error_msg}")
                return False, error_msg
        except subprocess.TimeoutExpired:
            self.append_result("Error: Comando timeout")
            return False, "Timeout"
        except Exception as e:
            self.append_result(f"Excepción: {str(e)}")
            return False, str(e)
    
    def git_status(self):
        """Muestra el estado actual del repositorio"""
        self.append_result("=== git status ===", clear=True)
        self.run_git_command(["git", "status"])
    
    def git_commit(self):
        """Realiza un commit con el mensaje proporcionado"""
        title = self.title_entry.get().strip()
        body = self.body_text.get("1.0", "end-1c").strip()
        
        if not title:
            messagebox.showwarning("Advertencia", "El título del commit es obligatorio")
            return
        
        # Construir mensaje completo (formato convencional Git)
        message = title
        if body:
            message += "\n\n" + body
        
        self.append_result("=== git commit ===", clear=True)
        success, _ = self.run_git_command(["git", "commit", "-m", message])
        
        if success:
            messagebox.showinfo("Éxito", "Commit realizado correctamente")
            self.title_entry.delete(0, "end")
            self.body_text.delete("1.0", "end")
            self.update_preview()
    
    def git_push(self):
        """Realiza un push al repositorio remoto"""
        self.append_result("=== git push ===", clear=True)
        success, _ = self.run_git_command(["git", "push"])
        
        if success:
            messagebox.showinfo("Éxito", "Push completado correctamente")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitGUI(root)
    root.mainloop() 
