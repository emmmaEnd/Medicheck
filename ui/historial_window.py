import os
import math
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from services.supabase_client import supabase
from ui.estadisticas_window import EstadisticasApp


class HistorialWindow:
    def __init__(self, root, medico_nombre=""):
        self.root = root
        self.root.title("Medichek - Historial")
        self.root.geometry("1100x650")
        self.root.configure(bg="#ecf0f3")

        # Estado actual
        self.vista = "miniatura"            # "miniatura" o "lista"
        self.orden_asc = True               # sentido del orden
        self.campo_orden_mini = "id_control"
        self.campo_orden_lista = "fecha"

        # Paginado (4 x 8)
        self.page_size = 32
        self.current_page = 1
        self.total_pages = 1

        # Filtros
        self.filtro_texto = tk.StringVar()
        self.filtro_campo = tk.StringVar()

        # Datos
        self.mediciones = []        # todos los registros
        self.datos_filtrados = []   # resultado de buscar/ordenar

        # Imagen por defecto
        self.foto_default = self.cargar_imagen_perfil()

        # UI base
        self.crear_appbar(medico_nombre)
        self.crear_barra_lateral()
        self.crear_contenedor_principal()

        # Cargar datos y aplicar filtros por defecto
        self.cargar_datos()
        self.limpiar_filtros()

    # ==========================================================
    # CARGAR IMAGEN PERFIL
    # ==========================================================
    def cargar_imagen_perfil(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            ruta_img = os.path.join(base_dir, "assets", "perfil_default.png")
            if os.path.exists(ruta_img):
                return tk.PhotoImage(file=ruta_img)
        except Exception as e:
            print("Error cargando imagen de perfil:", e)
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

        def nav_btn(texto, selected=False, command=None):
            bg = "white" if selected else "#2F76FF"
            fg = "#2F76FF" if selected else "white"
            return tk.Button(
                nav,
                text=texto,
                bg=bg,
                fg=fg,
                font=("Arial", 11, "bold"),
                relief="solid",
                bd=1 if not selected else 0,
                padx=10,
                pady=3,
                command=command
            )


        nav_btn("Historial", True).grid(row=0, column=0, padx=5)
        nav_btn("Alertas").grid(row=0, column=1, padx=5)
        nav_btn("Estadísticas", command=self.abrir_estadisticas).grid(row=0, column=2, padx=5)

    # ==========================================================
    # BARRA LATERAL
    # ==========================================================
    def crear_barra_lateral(self):
        self.sidebar = tk.Frame(self.root, bg="white", width=180)
        self.sidebar.pack(fill="y", side="left")

        # BUSCAR
        tk.Label(
            self.sidebar,
            text="Buscar",
            bg="white",
            fg="#333",
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 0))

        self.entry_buscar = tk.Entry(
            self.sidebar,
            textvariable=self.filtro_texto,
            width=17,
            font=("Arial", 10)
        )
        self.entry_buscar.pack(pady=5)

        # VISTAS
        tk.Label(
            self.sidebar,
            text="Vistas",
            bg="white",
            fg="#333",
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 5))

        frame_vistas = tk.Frame(self.sidebar, bg="white")
        frame_vistas.pack()

        self.btn_vista_mini = tk.Button(
            frame_vistas,
            text="Miniatura",
            command=lambda: self.cambiar_vista("miniatura"),
            bg="#2F76FF",
            fg="white",
            width=8
        )
        self.btn_vista_mini.grid(row=0, column=0, padx=3)

        self.btn_vista_lista = tk.Button(
            frame_vistas,
            text="Lista",
            command=lambda: self.cambiar_vista("lista"),
            bg="#f1f3f6",
            fg="#333",
            width=8
        )
        self.btn_vista_lista.grid(row=0, column=1, padx=3)

        # ORDEN POR
        tk.Label(
            self.sidebar,
            text="Orden por:",
            bg="white",
            fg="#333",
            font=("Arial", 11, "bold")
        ).pack(pady=(15, 5))

        self.combo_orden = ttk.Combobox(
            self.sidebar,
            textvariable=self.filtro_campo,
            state="readonly",
            width=15
        )
        self.combo_orden.pack(pady=5)

        # Asc / Desc
        frame_ad = tk.Frame(self.sidebar, bg="white")
        frame_ad.pack()

        self.btn_asc = tk.Button(
            frame_ad,
            text="Asc",
            width=7,
            command=lambda: self.cambiar_orden(True),
            bg="#2F76FF",
            fg="white"
        )
        self.btn_asc.grid(row=0, column=0, padx=2)

        self.btn_desc = tk.Button(
            frame_ad,
            text="Desc",
            width=7,
            command=lambda: self.cambiar_orden(False),
            bg="#f1f3f6",
            fg="#333"
        )
        self.btn_desc.grid(row=0, column=1, padx=2)

        # BOTONES BUSCAR / LIMPIAR
        frame_buscar = tk.Frame(self.sidebar, bg="white")
        frame_buscar.pack(pady=15)

        self.btn_buscar = tk.Button(
            frame_buscar,
            text="BUSCAR",
            command=self.ejecutar_busqueda,
            bg="#2F76FF",
            fg="white",
            width=7
        )
        self.btn_buscar.grid(row=0, column=0, padx=3)

        self.btn_limpiar = tk.Button(
            frame_buscar,
            text="LIMPIAR",
            command=self.limpiar_filtros,
            bg="#f1f3f6",
            fg="#333",
            width=7
        )
        self.btn_limpiar.grid(row=0, column=1, padx=3)

        # PAGINADO
        tk.Label(
            self.sidebar,
            text="Paginado",
            bg="white",
            fg="#333",
            font=("Arial", 11, "bold")
        ).pack(pady=(10, 5))

        pag = tk.Frame(self.sidebar, bg="white")
        pag.pack()

        tk.Button(pag, text="◀", width=3,
                  command=self.pagina_anterior).grid(row=0, column=0, padx=2)
        self.lbl_pagina = tk.Label(pag, text="1 de 1", bg="white")
        self.lbl_pagina.grid(row=0, column=1, padx=2)
        tk.Button(pag, text="▶", width=3,
                  command=self.pagina_siguiente).grid(row=0, column=2, padx=2)

        # valores iniciales del combo
        self.actualizar_combo_orden()

    # ==========================================================
    # CONTENEDOR PRINCIPAL
    # ==========================================================
    def crear_contenedor_principal(self):
        self.body_container = tk.Frame(self.root, bg="#ecf0f3")
        self.body_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.body_container, bg="#ecf0f3", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.body_container, orient="vertical",
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.body = tk.Frame(self.canvas, bg="#ecf0f3")
        self.body_window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        self.body.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.body_window, width=e.width)
        )

    # ==========================================================
    # CARGAR DATOS SUPABASE
    # ==========================================================
    def cargar_datos(self):
        try:
            resp = supabase.table("medicion").select(
                "id_medicion, temperatura, pulso, oxigenacion, fecha,"
                "tarjeta_alumno(id_control, "
                "alumno(nombre, apellido_paterno, fecha_registro, foto_url))"
            ).execute()

            self.mediciones = []
            for row in resp.data:
                tarjeta = row.get("tarjeta_alumno") or {}
                alumno = tarjeta.get("alumno") or {}

                self.mediciones.append({
                    "id_medicion": row.get("id_medicion"),
                    "id_control": tarjeta.get("id_control"),
                    "nombre": alumno.get("nombre"),
                    "apellido_paterno": alumno.get("apellido_paterno"),
                    "temperatura": row.get("temperatura"),
                    "pulso": row.get("pulso"),
                    "oxigenacion": row.get("oxigenacion"),
                    "fecha": row.get("fecha"),
                    "fecha_registro": alumno.get("fecha_registro"),
                    "foto_url": alumno.get("foto_url"),
                })

        except Exception as e:
            print("Supabase error:", e)
            self.mediciones = []

    # ==========================================================
    # FILTROS / ORDEN
    # ==========================================================
    def limpiar_filtros(self):
        """Resetea texto, orden y vuelve a aplicar con los defaults de la vista."""
        self.filtro_texto.set("")

        if self.vista == "miniatura":
            self.campo_orden_mini = "id_control"
            self.orden_asc = True
        else:
            self.campo_orden_lista = "fecha"
            self.orden_asc = False

        # botones Asc / Desc
        if self.orden_asc:
            self.btn_asc.config(bg="#2F76FF", fg="white")
            self.btn_desc.config(bg="#f1f3f6", fg="#333")
        else:
            self.btn_desc.config(bg="#2F76FF", fg="white")
            self.btn_asc.config(bg="#f1f3f6", fg="#333")

        self.actualizar_combo_orden()
        self.ejecutar_busqueda()

    def ejecutar_busqueda(self):
        """
        Aplica filtro de texto + orden según la vista.
        Solo se llama con los botones BUSCAR o LIMPIAR.
        """
        texto = self.filtro_texto.get().strip().lower()
        combo_value = self.filtro_campo.get().strip()

        if self.vista == "miniatura":
            if not combo_value:
                combo_value = "id_control"
            self.campo_orden_mini = combo_value

            # Agrupar por alumno (1 card por id_control)
            alumnos = {}
            for m in self.mediciones:
                idc = m.get("id_control")
                if idc is None:
                    continue

                idc_str = str(idc).lower()
                nom = (m.get("nombre") or "").lower()
                ape = (m.get("apellido_paterno") or "").lower()

                if texto in idc_str or texto in nom or texto in ape:
                    if idc not in alumnos:
                        alumnos[idc] = {
                            "id_control": idc,
                            "nombre": m.get("nombre"),
                            "apellido_paterno": m.get("apellido_paterno"),
                            "id_medicion": m.get("id_medicion"),
                            "temperatura": m.get("temperatura"),
                            "pulso": m.get("pulso"),
                            "oxigenacion": m.get("oxigenacion"),
                            "fecha": m.get("fecha"),
                            "fecha_registro": m.get("fecha_registro"),
                            "foto_url": m.get("foto_url"),
                        }

            datos = list(alumnos.values())
            campo = self.campo_orden_mini

        else:  # vista lista → 1 a 1 registro
            if not combo_value:
                combo_value = "fecha"
            self.campo_orden_lista = combo_value

            datos = []
            for m in self.mediciones:
                idc_str = str(m.get("id_control") or "").lower()
                nom = (m.get("nombre") or "").lower()
                ape = (m.get("apellido_paterno") or "").lower()

                if texto in idc_str or texto in nom or texto in ape:
                    datos.append(m)

            campo = self.campo_orden_lista

        # Ordenar
        def key_fn(x):
            val = x.get(campo)
            return (val is None, val)

        datos = sorted(
            datos,
            key=key_fn,
            reverse=not self.orden_asc
        )

        self.datos_filtrados = datos
        self.current_page = 1
        self.total_pages = max(1, math.ceil(len(datos) / self.page_size))
        self.actualizar_label_pagina()
        self.mostrar_vista()

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

    # ==========================================================
    # CAMBIOS DE ESTADO (VISTA / ORDEN / PÁGINA)
    # ==========================================================
    def cambiar_vista(self, vista):
        if self.vista == vista:
            return

        self.vista = vista

        if vista == "miniatura":
            self.btn_vista_mini.config(bg="#2F76FF", fg="white")
            self.btn_vista_lista.config(bg="#f1f3f6", fg="#333")
        else:
            self.btn_vista_lista.config(bg="#2F76FF", fg="white")
            self.btn_vista_mini.config(bg="#f1f3f6", fg="#333")

        # Al cambiar de vista, resetear filtros a sus defaults
        self.limpiar_filtros()

    def cambiar_orden(self, asc):
        # Solo cambia la bandera; se aplicará cuando se pulse BUSCAR o LIMPIAR
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

    # ==========================================================
    # PINTAR VISTAS
    # ==========================================================
    def limpiar_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def mostrar_vista(self):
        self.limpiar_body()

        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        datos_pagina = self.datos_filtrados[start:end]

        if self.vista == "miniatura":
            self.mostrar_miniatura(datos_pagina)
        else:
            self.mostrar_lista(datos_pagina)

    # ------------------ MINIATURA ------------------ #
    def mostrar_miniatura(self, datos):
        grid = tk.Frame(self.body, bg="#ecf0f3")
        grid.pack(fill="x", expand=True, padx=20, pady=20)

        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform="col")

        total_slots = self.page_size  # 32
        for idx in range(total_slots):
            r = idx // 4
            c = idx % 4

            card = tk.Frame(
                grid,
                bg="white",
                highlightbackground="#dcdcdc",
                highlightthickness=1,
                cursor="hand2"
            )
            card.grid(row=r, column=c, padx=10, pady=10, sticky="we")
            card.grid_propagate(False)
            card.bind("<Configure>", lambda e, f=card: self.redimensionar_card(f))

            if idx < len(datos):
                info = datos[idx]
                idc = info.get("id_control")

                img_slot = tk.Label(card, bg="white")
                img_slot.pack(fill="x")
                img_slot.pack_propagate(False)
                img_slot.bind(
                    "<Configure>",
                    lambda e, lab=img_slot: self.redimensionar_imagen(lab)
                )

                lbl_id = tk.Label(
                    card,
                    text=idc,
                    bg="white",
                    fg="#2F76FF",
                    font=("Arial", 12, "bold")
                )
                lbl_id.pack()

                lbl_nom = tk.Label(
                    card,
                    text=f"{info.get('nombre') or ''} {info.get('apellido_paterno') or ''}",
                    bg="white",
                    fg="#555",
                    font=("Arial", 11)
                )
                lbl_nom.pack(pady=(2, 6))

                # hacer clickable la card y sus hijos
                def bind_detalle(widget, ic=idc):
                    widget.bind(
                        "<Button-1>",
                        lambda e, i=ic: self.abrir_detalle_alumno(i)
                    )

                for w in (card, img_slot, lbl_id, lbl_nom):
                    bind_detalle(w)
            else:
                tk.Label(card, bg="white").pack(fill="both", expand=True)

    # ------------------ LISTA ------------------ #
    def mostrar_lista(self, datos):
        columns = (
            "id_medicion", "id_control", "nombre", "apellido_paterno",
            "temperatura", "pulso", "oxigenacion", "fecha"
        )

        table = ttk.Treeview(self.body, columns=columns, show="headings")

        for col in columns:
            table.heading(col, text=col.replace("_", " ").title())
            table.column(col, width=120, anchor="center")

        for m in datos:
            fecha_texto = ""
            if m.get("fecha"):
                try:
                    fecha_dt = datetime.fromisoformat(m["fecha"].replace("Z", ""))
                    fecha_texto = fecha_dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    fecha_texto = m["fecha"]

            table.insert(
                "",
                "end",
                values=(
                    m.get("id_medicion"),
                    m.get("id_control"),
                    m.get("nombre"),
                    m.get("apellido_paterno"),
                    m.get("temperatura"),
                    m.get("pulso"),
                    m.get("oxigenacion"),
                    fecha_texto
                )
            )

        table.pack(fill="both", expand=True, pady=10)

        # doble clic abre detalle de registro
        table.bind("<Double-1>", lambda e, t=table: self.on_table_doble_click(t))

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

    # ==========================================================
    # DETALLES (ALUMNO / REGISTRO)
    # ==========================================================
    def centrar_ventana(self, win, ancho, alto):
        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw // 2) - (ancho // 2)
        y = (sh // 2) - (alto // 2)
        win.geometry(f"{ancho}x{alto}+{x}+{y}")

    def on_table_doble_click(self, tree):
        item_id = tree.focus()
        if not item_id:
            return
        values = tree.item(item_id, "values")
        if not values:
            return
        id_medicion = values[0]
        reg = next(
            (m for m in self.mediciones
             if str(m.get("id_medicion")) == str(id_medicion)),
            None
        )
        if reg:
            self.abrir_detalle_registro(reg)

    # ---------- Detalle Alumno (desde miniaturas) ----------
    def abrir_detalle_alumno(self, id_control):
        registros = [
            m for m in self.mediciones
            if m.get("id_control") == id_control
        ]
        if not registros:
            return

        # ordenar registros por fecha desc para mostrar arriba los recientes
        registros = sorted(
            registros,
            key=lambda m: (m.get("fecha") is None, m.get("fecha")),
            reverse=True
        )

        ref = registros[0]
        nombre = (ref.get("nombre") or "")
        ape = (ref.get("apellido_paterno") or "")
        nombre_completo = (nombre + " " + ape).strip()

        fecha_registro = ref.get("fecha_registro")
        fecha_reg_texto = ""
        if fecha_registro:
            try:
                fr = datetime.fromisoformat(fecha_registro.replace("Z", ""))
                fecha_reg_texto = fr.strftime("%Y-%m-%d %H:%M")
            except Exception:
                fecha_reg_texto = str(fecha_registro)

        win = tk.Toplevel(self.root)
        win.title(f"Alumno {id_control}")
        self.centrar_ventana(win, 700, 500)
        win.configure(bg="#ecf0f3")

        cont = tk.Frame(win, bg="#ecf0f3")
        cont.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            cont,
            text=f"Alumno: {id_control}",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # Parte superior: foto + datos
        top = tk.Frame(cont, bg="#ecf0f3")
        top.pack(fill="x", pady=5)

        # Foto
        frame_foto = tk.Frame(top, bg="white", width=140, height=140,
                              highlightbackground="#dcdcdc", highlightthickness=1)
        frame_foto.pack(side="left", padx=20)
        frame_foto.pack_propagate(False)

        lbl_foto = tk.Label(frame_foto, bg="white")
        lbl_foto.pack(fill="both", expand=True)
        lbl_foto.bind("<Configure>", lambda e, lab=lbl_foto: self.redimensionar_imagen(lab))

        # Datos alumno
        datos_alumno = tk.Frame(top, bg="#ecf0f3")
        datos_alumno.pack(side="left", padx=10, pady=10, anchor="nw")

        tk.Label(
            datos_alumno,
            text=f"Nombre completo: {nombre_completo}",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 11)
        ).pack(anchor="w")

        tk.Label(
            datos_alumno,
            text=f"Fecha registro: {fecha_reg_texto or '—'}",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(3, 0))

        # Filtros para minilista
        frame_filtros = tk.Frame(cont, bg="#ecf0f3")
        frame_filtros.pack(fill="x", pady=(10, 2))

        tk.Label(
            frame_filtros,
            text="Orden por:",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(5, 3))

        var_campo = tk.StringVar(value="fecha")
        combo_campo = ttk.Combobox(
            frame_filtros,
            textvariable=var_campo,
            state="readonly",
            width=12,
            values=["fecha", "id_medicion", "temperatura", "pulso", "oxigenacion"]
        )
        combo_campo.pack(side="left")

        tk.Label(
            frame_filtros,
            text="  Orden:",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(10, 3))

        var_sentido = tk.StringVar(value="DESC")
        combo_sent = ttk.Combobox(
            frame_filtros,
            textvariable=var_sentido,
            state="readonly",
            width=6,
            values=["ASC", "DESC"]
        )
        combo_sent.pack(side="left")

        btn_aplicar = tk.Button(
            frame_filtros,
            text="Aplicar",
            bg="#2F76FF",
            fg="white",
            width=8
        )
        btn_aplicar.pack(side="left", padx=10)

        # Minilista de registros del alumno
        frame_lista = tk.Frame(cont, bg="#ecf0f3")
        frame_lista.pack(fill="both", expand=True, pady=(5, 0))

        cols = ("id_medicion", "fecha", "temperatura", "pulso", "oxigenacion")
        tabla = ttk.Treeview(frame_lista, columns=cols, show="headings", height=8)

        for col in cols:
            tabla.heading(col, text=col.replace("_", " ").title())
            tabla.column(col, anchor="center", width=110)

        tabla.pack(fill="both", expand=True)

        # Doble clic en minilista → detalle registro
        tabla.bind("<Double-1>", lambda e, t=tabla: self.on_table_doble_click(t))

        def refrescar_minilista():
            campo = var_campo.get()
            asc = (var_sentido.get() == "ASC")

            def key_min(r):
                v = r.get(campo)
                return (v is None, v)

            ordenados = sorted(
                registros,
                key=key_min,
                reverse=not asc
            )

            for item in tabla.get_children():
                tabla.delete(item)

            for m in ordenados:
                fecha_texto = ""
                if m.get("fecha"):
                    try:
                        fd = datetime.fromisoformat(m["fecha"].replace("Z", ""))
                        fecha_texto = fd.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        fecha_texto = m["fecha"]

                tabla.insert(
                    "",
                    "end",
                    values=(
                        m.get("id_medicion"),
                        fecha_texto,
                        m.get("temperatura"),
                        m.get("pulso"),
                        m.get("oxigenacion")
                    )
                )

        btn_aplicar.config(command=refrescar_minilista)
        refrescar_minilista()

    # ---------- Detalle Registro (desde lista y minilista) ----------
    def abrir_detalle_registro(self, reg):
        if not reg:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Registro {reg.get('id_medicion')}")
        self.centrar_ventana(win, 550, 430)
        win.configure(bg="#ecf0f3")

        cont = tk.Frame(win, bg="#ecf0f3")
        cont.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            cont,
            text=f"Registro {reg.get('id_medicion')}",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        fecha_texto = ""
        if reg.get("fecha"):
            try:
                fd = datetime.fromisoformat(reg["fecha"].replace("Z", ""))
                fecha_texto = fd.strftime("%Y-%m-%d %H:%M")
            except Exception:
                fecha_texto = reg["fecha"]

        tk.Label(
            cont,
            text=f"Fecha de medida: {fecha_texto or '—'}",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 11)
        ).pack(pady=(0, 10))

        # Panel con temperatura / pulso / oxigenación
        panel = tk.Frame(cont, bg="#ecf0f3")
        panel.pack(pady=5)

        def caja_indicador(parent, titulo, valor):
            frame = tk.Frame(parent, bg="white",
                             highlightbackground="#dcdcdc", highlightthickness=1)
            frame.pack(side="left", padx=5)
            tk.Label(
                frame,
                text=titulo,
                bg="white",
                fg="#333",
                font=("Arial", 10, "bold")
            ).pack(padx=10, pady=(5, 0))
            tk.Label(
                frame,
                text=valor,
                bg="white",
                fg="#333",
                font=("Arial", 11)
            ).pack(padx=10, pady=(0, 5))

        temp_val = f"{reg.get('temperatura') or '—'} °C"
        pulso_val = f"{reg.get('pulso') or '—'} bpm"
        oxi_val = f"{reg.get('oxigenacion') or '—'} %"

        caja_indicador(panel, "Temperatura", temp_val)
        caja_indicador(panel, "Ritmo", pulso_val)
        caja_indicador(panel, "Oxigenación", oxi_val)

        # Parte inferior: datos alumno + foto
        bottom = tk.Frame(cont, bg="#ecf0f3")
        bottom.pack(fill="x", expand=True, pady=(20, 0))

        info_alumno = tk.Frame(bottom, bg="#ecf0f3")
        info_alumno.pack(side="left", padx=20, anchor="nw")

        nombre = (reg.get("nombre") or "")
        ape = (reg.get("apellido_paterno") or "")
        nombre_completo = (nombre + " " + ape).strip()

        tk.Label(
            info_alumno,
            text="Alumno:",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        tk.Label(
            info_alumno,
            text=f"{reg.get('id_control') or ''}",
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 11)
        ).pack(anchor="w")

        tk.Label(
            info_alumno,
            text=nombre_completo,
            bg="#ecf0f3",
            fg="#333",
            font=("Arial", 11)
        ).pack(anchor="w", pady=(0, 5))

        frame_foto = tk.Frame(bottom, bg="white", width=120, height=120,
                              highlightbackground="#dcdcdc", highlightthickness=1)
        frame_foto.pack(side="right", padx=20)
        frame_foto.pack_propagate(False)

        lbl_foto = tk.Label(frame_foto, bg="white")
        lbl_foto.pack(fill="both", expand=True)
        lbl_foto.bind("<Configure>", lambda e, lab=lbl_foto: self.redimensionar_imagen(lab))

    def abrir_estadisticas(self):
        self.root.destroy()
        EstadisticasApp().mainloop()
