import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from services.supabase_client import supabase  # Tu cliente configurado

def fetch_global_stats():
    # Consulta básica: todas las mediciones ordenadas por fecha
    response = supabase.table('medicion').select('fecha,temperatura,pulso,oxigenacion').order('fecha').execute()
    return response.data

def crear_graficos(datos):
    fechas = [d['fecha'][:10] for d in datos]  # Solo la fecha (YYYY-MM-DD)
    temperaturas = [d['temperatura'] for d in datos]
    oxigenaciones = [d['oxigenacion'] for d in datos]
    pulsos = [d['pulso'] for d in datos]

    fig, axs = plt.subplots(3, 1, figsize=(8, 7))
    axs[0].plot(fechas, temperaturas, marker='o', label="Temperatura")
    axs[0].set_title("Tendencia de Temperatura")
    axs[0].set_ylabel("°C")
    axs[1].plot(fechas, oxigenaciones, marker='o', label="Oxigenación", color='g')
    axs[1].set_title("Tendencia de Oxigenación")
    axs[1].set_ylabel("%")
    axs[2].plot(fechas, pulsos, marker='o', label="Pulso", color='r')
    axs[2].set_title("Tendencia de Pulso")
    axs[2].set_ylabel("bpm")
    for ax in axs:
        ax.set_xticks(fechas[::max(1, len(fechas)//7)])  # Espaciado de fechas
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    return fig

class EstadisticasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Estadísticas Globales Médicas")
        self.geometry("1000x800")
        self.canvas = None

        self.btn_recargar = ttk.Button(self, text="Recargar Datos", command=self.actualizar_vista)
        self.btn_recargar.pack(pady=10)
        self.actualizar_vista()

    def actualizar_vista(self):
        datos = fetch_global_stats()
        fig = crear_graficos(datos)
        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

if __name__ == "__main__":
    app = EstadisticasApp()
    app.mainloop()
