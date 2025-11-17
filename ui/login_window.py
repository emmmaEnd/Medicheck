import tkinter as tk
from tkinter import messagebox
from services.supabase_client import supabase_login

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Medichek")
        self.root.geometry("1280x720")
        self.root.configure(bg="#ecf0f3")
        self.root.resizable(False, False)

        # --- Tarjeta del login ---
        self.frame = tk.Frame(self.root, bg="white", bd=0, relief=tk.FLAT)
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=250)

        # Título
        self.title = tk.Label(
            self.frame, text="Iniciar Sesión",
            font=("Arial", 16, "bold"),
            bg="white", fg="#3a3b3c"
        )
        self.title.pack(pady=10)

        # Usuario
        tk.Label(self.frame, text="Usuario:", bg="white", fg="#555", font=("Arial", 12)).pack()
        self.user_entry = tk.Entry(self.frame, font=("Arial", 12), bg="#f1f3f6", bd=0)
        self.user_entry.pack(ipady=4, pady=5)

        # Contraseña
        tk.Label(self.frame, text="Contraseña:", bg="white", fg="#555", font=("Arial", 12)).pack()
        self.pass_entry = tk.Entry(self.frame, font=("Arial", 12), bg="#f1f3f6", bd=0, show="*")
        self.pass_entry.pack(ipady=4, pady=5)

        # Botón
        self.login_button = tk.Button(
            self.frame,
            text="Entrar",
            bg="#2F76FF",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            command=self.try_login
        )
        self.login_button.pack(pady=15)

    def try_login(self):
        usuario = self.user_entry.get()
        contrasena = self.pass_entry.get()

        if not usuario or not contrasena:
            messagebox.showwarning("Campos vacíos", "Ingresa usuario y contraseña.")
            return

        logged = supabase_login(usuario, contrasena)

        if logged:
            messagebox.showinfo("Éxito", "Inicio de sesión correcto.")
            # Aquí podrás abrir el panel médico
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")
