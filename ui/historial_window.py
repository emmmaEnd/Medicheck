import os
import math
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from services.supabase_client import supabase


class HistorialWindow:
    def __init__(self, root, medico_nombre=""):
        self.root = root
        self.root.title("Medichek - Historial")
        self.root.geometry("1100x650")
        self.root.configure(bg="#ecf0f3")

        # Estado actual
        self.vista = "miniatura"                   # vista actual
        self.orden_asc = True                      # modo orden
        self.campo_orden = "id_control"            # campo por default miniatura
        self.campo_orden_lista = "fecha"           # default en lista
        self.campo_orden_mini = "id_control"       # default miniatura

        # Paginado (4 x 8)
        self.page_size = 32
        self.current_page = 1
        self.total_pages = 1

        # Filtros
        self.filtro_texto = tk.StringVar()
        self.filtro_campo = tk.StringVar()         # combo Orden por

        # Datos cargados
        self.mediciones = []

        # Imagen por defecto
        self.foto_default = self.cargar_imagen_perfil()

        # UI base
        self.crear_appbar(medico_nombre)
        self.crear_barra_lateral()
        self.crear_contenedor_principal()

        # Cargar datos y mostrar
        self.cargar_datos()
        self.mostrar_vista()

    # ==========================================================
    # CARGAR IMAGEN PERFIL
    # ==========================================================
    def cargar_imagen_perfil(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            ruta_img = os.path.join(base_dir, "assets", "perfil_default.png")
            if os.path.exists(ruta_img):
                return tk.PhotoImage(file=ruta_img)
        except:
            pass
        return None

    # ==========================================================
    # APPBAR
    # ==========================================================
    def crear_appbar(self, medico_nombre):
        self.appbar = tk.Frame(self.root, bg="#2F76FF", height=80)
        self.appbar.pack(fill="x", side="top")

        tk.Label(
            self.appbar,
            text="Historial de Mediciones",
            bg="#2F76FF",
            fg="white",
            font=("Arial", 16, "bold")
        ).place(x=20, y=8)

        tk.Label(
            self.appbar,
            text=f"Médico: {medico_nombre}",
            bg="#2F76FF",
            fg="white",
            font=("Arial", 11)
        ).place(x=20, y=40)

        nav = tk.Frame(self.appbar, bg="#2F76FF")
        nav.place(x=300, y=22)

        def nav_btn(texto, selected=False):
            bg = "white" if selected else "#2F76FF"
            fg = "#2F76FF" if selected else "white"
            return tk.Button(
                nav, text=texto, bg=bg, fg=fg,
                font=("Arial", 11, "bold"),
                relief="solid", bd=1 if not selected else 0,
                padx=10, pady=3
            )

        nav_btn("Historial", True).grid(row=0, column=0, padx=5)
        nav_btn("Alertas").grid(row=0, column=1, padx=5)
        nav_btn("Estadísticas").grid(row=0, column=2, padx=5)

    # ==========================================================
    # BARRA LATERAL (FILTROS + NAVEGACIÓN)
    # ==========================================================
    def crear_barra_lateral(self):
        self.sidebar = tk.Frame(self.root, bg="white", width=180)
        self.sidebar.pack(fill="y", side="left")

        # ======================= BUSCAR =======================
        tk.Label(self.sidebar, text="Buscar", bg="white", fg="#333",
                 font=("Arial", 11, "bold")).pack(pady=(15, 0))

        self.entry_buscar = tk.Entry(self.sidebar, textvariable=self.filtro_texto,
                                     width=17, font=("Arial", 10))
        self.entry_buscar.pack(pady=5)

        # ======================= VISTAS =======================
        tk.Label(self.sidebar, text="Vistas", bg="white", fg="#333",
                 font=("Arial", 11, "bold")).pack(pady=(15, 5))

        frame_vistas = tk.Frame(self.sidebar, bg="white")
        frame_vistas.pack()

        self.btn_vista_mini = tk.Button(
            frame_vistas, text="Miniatura",
            command=lambda: self.cambiar_vista("miniatura"),
            bg="#2F76FF", fg="white", width=8
        )
        self.btn_vista_mini.grid(row=0, column=0, padx=3)

        self.btn_vista_lista = tk.Button(
            frame_vistas, text="Lista",
            command=lambda: self.cambiar_vista("lista"),
            bg="#f1f3f6", fg="#333", width=8
        )
        self.btn_vista_lista.grid(row=0, column=1, padx=3)

        # ======================= ORDEN POR =======================
        tk.Label(self.sidebar, text="Orden por:", bg="white", fg="#333",
                 font=("Arial", 11, "bold")).pack(pady=(15, 5))

        self.combo_orden = ttk.Combobox(
            self.sidebar, textvariable=self.filtro_campo,
            state="readonly", width=15
        )
        self.combo_orden.pack(pady=5)

        # Modo ASC/DESC
        frame_ad = tk.Frame(self.sidebar, bg="white")
        frame_ad.pack()

        self.btn_asc = tk.Button(
            frame_ad, text="Asc", width=7,
            command=lambda: self.cambiar_orden(True),
            bg="#2F76FF", fg="white"
        )
        self.btn_asc.grid(row=0, column=0, padx=2)

        self.btn_desc = tk.Button(
            frame_ad, text="Desc", width=7,
            command=lambda: self.cambiar_orden(False),
            bg="#f1f3f6", fg="#333"
        )
        self.btn_desc.grid(row=0, column=1, padx=2)

        # ======================= BOTÓN BUSCAR =======================
        self.btn_buscar = tk.Button(
            self.sidebar, text="BUSCAR",
            command=self.ejecutar_busqueda,
            bg="#2F76FF", fg="white", width=15
        )
        self.btn_buscar.pack(pady=15)

        # ======================= PAGINADO =======================
        tk.Label(self.sidebar, text="Paginado", bg="white", fg="#333",
                 font=("Arial", 11, "bold")).pack(pady=(10, 5))

        pag = tk.Frame(self.sidebar, bg="white")
        pag.pack()

        tk.Button(pag, text="◀", width=3, command=self.pagina_anterior).grid(row=0, column=0, padx=2)
        self.lbl_pagina = tk.Label(pag, text="1 de 1", bg="white")
        self.lbl_pagina.grid(row=0, column=1, padx=2)
        tk.Button(pag, text="▶", width=3, command=self.pagina_siguiente).grid(row=0, column=2, padx=2)

        self.actualizar_combo_orden()

    # ==========================================================
    # CONTENEDOR PRINCIPAL (CANVAS + BODY)
    # ==========================================================
    def crear_contenedor_principal(self):
        self.body_container = tk.Frame(self.root, bg="#ecf0f3")
        self.body_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.body_container, bg="#ecf0f3", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.body_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg="#ecf0f3")
        self.body_window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        self.body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.body_window, width=e.width))

    # ==========================================================
    # CARGAR DATOS SUPABASE
    # ==========================================================
    def cargar_datos(self):
        try:
            resp = supabase.table("medicion").select(
                "id_medicion, temperatura, pulso, oxigenacion, fecha,"
                "tarjeta_alumno(id_control, alumno(nombre, apellido_paterno))"
            ).execute()

            self.mediciones = []
            for row in resp.data:
                alumno = row["tarjeta_alumno"]["alumno"] if row.get("tarjeta_alumno") else {}

                self.mediciones.append({
                    "id_medicion": row["id_medicion"],
                    "id_control": row["tarjeta_alumno"]["id_control"] if row.get("tarjeta_alumno") else None,
                    "nombre": alumno.get("nombre"),
                    "apellido_paterno": alumno.get("apellido_paterno"),
                    "temperatura": row.get("temperatura"),
                    "pulso": row.get("pulso"),
                    "oxigenacion": row.get("oxigenacion"),
                    "fecha": row.get("fecha")
                })

        except Exception as e:
            print("Supabase error:", e)
            self.mediciones = []

        self.ejecutar_busqueda()

    # ==========================================================
    # FILTRADO Y ORDENADO
    # ==========================================================
    def ejecutar_busqueda(self):
        texto = self.filtro_texto.get().strip().lower()

        datos = []
        for m in self.mediciones:
            if (texto in str(m["id_control"]).lower()
                or texto in (m["nombre"] or "").lower()
                or texto in (m["apellido_paterno"] or "").lower()):
                datos.append(m)

        # ordenar
        campo = self.campo_orden_mini if self.vista == "miniatura" else self.campo_orden_lista

        datos = sorted(
            datos,
            key=lambda x: (x[campo] is None, x[campo]),
            reverse=not self.orden_asc
        )

        self.datos_filtrados = datos
        self.current_page = 1
        self.total_pages = max(1, math.ceil(len(datos) / self.page_size))
        self.actualizar_label_pagina()
        self.mostrar_vista()

    # ==========================================================
    # UTILIDADES
    # ==========================================================
    def actualizar_combo_orden(self):
        if self.vista == "miniatura":
            self.combo_orden["values"] = ["id_control", "nombre"]
            self.combo_orden.set(self.campo_orden_mini)
        else:
            self.combo_orden["values"] = [
                "fecha", "id_medicion", "id_control", "nombre",
                "apellido_paterno", "temperatura", "pulso", "oxigenacion"
            ]
            self.combo_orden.set(self.campo_orden_lista)

    def cambiar_vista(self, vista):
        self.vista = vista

        if vista == "miniatura":
            self.btn_vista_mini.config(bg="#2F76FF", fg="white")
            self.btn_vista_lista.config(bg="#f1f3f6", fg="#333")
        else:
            self.btn_vista_lista.config(bg="#2F76FF", fg="white")
            self.btn_vista_mini.config(bg="#f1f3f6", fg="#333")

        self.actualizar_combo_orden()
        self.ejecutar_busqueda()

    def cambiar_orden(self, asc):
        self.orden_asc = asc
        if asc:
            self.btn_asc.config(bg="#2F76FF", fg="white")
            self.btn_desc.config(bg="#f1f3f6", fg="#333")
        else:
            self.btn_desc.config(bg="#2F76FF", fg="white")
            self.btn_asc.config(bg="#f1f3f6", fg="#333")

    def pagina_anterior(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.actualizar_label_pagina()
            self.mostrar_vista()

    def pagina_siguiente(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.actualizar_label_pagina()
            self.mostrar_vista()

    def actualizar_label_pagina(self):
        self.lbl_pagina.config(text=f"{self.current_page} de {self.total_pages}")

    def limpiar_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    # ==========================================================
    # MOSTRAR VISTA
    # ==========================================================
    def mostrar_vista(self):
        self.limpiar_body()

        # segmentación por página
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        datos_pagina = self.datos_filtrados[start:end]

        if self.vista == "miniatura":
            self.mostrar_miniatura(datos_pagina)
        else:
            self.mostrar_lista(datos_pagina)

    # ==========================================================
    # MINIATURA
    # ==========================================================
    def mostrar_miniatura(self, datos):
        grid = tk.Frame(self.body, bg="#ecf0f3")
        grid.pack(fill="x", expand=True, padx=20, pady=20)

        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform="col")

        filas = 8
        idx = 0

        for r in range(filas):
            for c in range(4):
                card = tk.Frame(
                    grid, bg="white",
                    highlightbackground="#dcdcdc", highlightthickness=1
                )
                card.grid(row=r, column=c, padx=10, pady=10, sticky="we")
                card.grid_propagate(False)
                card.bind("<Configure>", lambda e, f=card: self.redimensionar_card(f))

                if idx < len(datos):
                    info = datos[idx]

                    img_slot = tk.Label(card, bg="white")
                    img_slot.pack(fill="x")
                    img_slot.pack_propagate(False)
                    img_slot.bind("<Configure>", lambda e, lab=img_slot: self.redimensionar_imagen(lab))

                    tk.Label(card, text=info["id_control"], bg="white",
                             fg="#2F76FF", font=("Arial", 12, "bold")).pack()

                    tk.Label(card, text=f"{info['nombre']} {info['apellido_paterno']}",
                             bg="white", fg="#555", font=("Arial", 11)).pack()

                idx += 1

    # ==========================================================
    # LISTA (CON FECHA)
    # ==========================================================
    def mostrar_lista(self, datos):
        columns = ("id_medicion", "id_control", "nombre", "apellido_paterno",
                   "temperatura", "pulso", "oxigenacion", "fecha")

        table = ttk.Treeview(self.body, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col.replace("_", " ").title())
            table.column(col, width=120, anchor="center")

        for m in datos:
            fecha_texto = ""
            if m["fecha"]:
                try:
                    fecha_dt = datetime.fromisoformat(m["fecha"].replace("Z", ""))
                    fecha_texto = fecha_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    fecha_texto = m["fecha"]

            table.insert("", "end", values=(
                m["id_medicion"],
                m["id_control"],
                m["nombre"],
                m["apellido_paterno"],
                m["temperatura"],
                m["pulso"],
                m["oxigenacion"],
                fecha_texto
            ))

        table.pack(fill="both", expand=True, pady=10)

    # ==========================================================
    # REDIMENSIONAMIENTO
    # ==========================================================
    def redimensionar_card(self, frame):
        w = frame.winfo_width()
        if w > 0:
            h = int(w * 1.2)
            frame.config(height=h)

    def redimensionar_imagen(self, label):
        if self.foto_default is None:
            return

        w = label.winfo_width()
        h = label.winfo_height()
        if w < 10 or h < 10:
            return

        fx = max(self.foto_default.width() // w, 1)
        fy = max(self.foto_default.height() // h, 1)
        f = max(fx, fy)

        img = self.foto_default.subsample(f, f)
        label.config(image=img)
        label.image = img
