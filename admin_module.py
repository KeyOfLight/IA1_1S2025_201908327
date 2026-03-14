import tkinter as tk
from tkinter import font, messagebox, ttk
from database import validate_credentials, get_diagnoses, delete_diagnosis


class AdminModule:
    """Módulo administrativo para personal médico con autenticación"""
    
    def __init__(self, window):
        self.window = window
        self.window.title("Módulo Administrativo")
        self.window.geometry("1200x650")
        self.window.resizable(False, False)
        self.authenticated = False
        self.user_level = None
        self.current_username = None
        
        self.configure_styles()
        self.show_login()
    
    def configure_styles(self):
        """Configura los estilos de fuentes"""
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.text_font = font.Font(family="Helvetica", size=10)
        self.label_font = font.Font(family="Helvetica", size=11)
    
    def show_login(self):
        """Muestra la pantalla de autenticación"""
        # Limpiar ventana
        for widget in self.window.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        header = tk.Frame(main_frame, bg="#e74c3c")
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="Acceso Administrativo",
            font=self.title_font,
            fg="white",
            bg="#e74c3c",
            pady=20
        )
        title.pack()
        
        # Frame de login
        login_frame = tk.Frame(main_frame, bg="#f0f0f0")
        login_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        description = tk.Label(
            login_frame,
            text="Este módulo es exclusivo para personal médico autorizado.\nIngrese sus credenciales para acceder.",
            font=self.text_font,
            fg="#333",
            bg="#f0f0f0",
            justify=tk.CENTER
        )
        description.pack(pady=(0, 30))
        
        # Usuario
        user_label = tk.Label(
            login_frame,
            text="Usuario:",
            font=self.label_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        user_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.user_entry = tk.Entry(
            login_frame,
            font=self.text_font,
            width=30,
            bd=2,
            relief=tk.SOLID
        )
        self.user_entry.pack(fill=tk.X, pady=(5, 20))
        self.user_entry.focus()
        
        # Contraseña
        pass_label = tk.Label(
            login_frame,
            text="Contraseña:",
            font=self.label_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        pass_label.pack(anchor=tk.W, pady=(10, 0))
        
        self.pass_entry = tk.Entry(
            login_frame,
            font=self.text_font,
            width=30,
            show="•",
            bd=2,
            relief=tk.SOLID
        )
        self.pass_entry.pack(fill=tk.X, pady=(5, 30))
        self.pass_entry.bind("<Return>", lambda e: self.verify_credentials())
        
        # Información de credenciales de prueba
        info_frame = tk.Frame(login_frame, bg="#e8f4f8", relief=tk.SUNKEN, bd=1)
        info_frame.pack(fill=tk.X, pady=20)
        
        info_text = """Credenciales de Prueba:
Médico: usuario: medico | contraseña: medico123
Administrador: usuario: admin | contraseña: admin123"""
        
        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=font.Font(family="Helvetica", size=8),
            fg="#01579b",
            bg="#e8f4f8",
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        info_label.pack(anchor=tk.W)
        
        # Botones
        button_frame = tk.Frame(login_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)
        
        btn_login = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            font=self.subtitle_font,
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.verify_credentials
        )
        btn_login.pack(side=tk.LEFT, padx=10)
        
        btn_cancel = tk.Button(
            button_frame,
            text="Cancelar",
            font=self.subtitle_font,
            bg="#e74c3c",
            fg="white",
            padx=30,
            pady=10,
            cursor="hand2",
            command=self.window.destroy
        )
        btn_cancel.pack(side=tk.LEFT, padx=10)
    
    def verify_credentials(self):
        """Verifica las credenciales ingresadas"""
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Aviso", "Por favor ingrese usuario y contraseña")
            return
        
        result = validate_credentials(username, password)
        
        if result["authenticated"]:
            self.authenticated = True
            self.user_level = result["level"]
            self.current_username = username
            self.show_admin_panel()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
            self.pass_entry.delete(0, tk.END)
            self.pass_entry.focus()
    
    def show_admin_panel(self):
        """Muestra el panel administrativo después de la autenticación"""
        # Limpiar ventana
        for widget in self.window.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        header = tk.Frame(main_frame, bg="#2c3e50")
        header.pack(fill=tk.X)
        
        header_content = tk.Frame(header, bg="#2c3e50")
        header_content.pack(fill=tk.X, padx=15, pady=10)
        
        title = tk.Label(
            header_content,
            text=f"Panel Administrativo - Bienvenido {self.current_username or ''}",
            font=self.title_font,
            fg="white",
            bg="#2c3e50"
        )
        title.pack(anchor=tk.W)
        
        user_level_text = f"Nivel de acceso: {self.user_level.upper()}"
        level_label = tk.Label(
            header_content,
            text=user_level_text,
            font=self.text_font,
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        level_label.pack(anchor=tk.W)
        
        # Contenido
        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título de sección
        section_title = tk.Label(
            content_frame,
            text="Registros de Diagnósticos",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        section_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Tabla de diagnósticos
        table_frame = tk.Frame(content_frame, bg="white", relief=tk.SUNKEN, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear Treeview
        columns = ("ID", "Síntomas", "Crónicas", "Alergias", "Diagnósticos", "Fecha")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            height=12,
            show="headings"
        )
        
        # Definir encabezados
        self.tree.heading("ID", text="ID")
        self.tree.heading("Síntomas", text="Síntomas Reportados")
        self.tree.heading("Crónicas", text="Enfermedades Crónicas")
        self.tree.heading("Alergias", text="Alergias")
        self.tree.heading("Diagnósticos", text="Diagnósticos Preliminares")
        self.tree.heading("Fecha", text="Fecha")
        
        self.tree.column("ID", width=40)
        self.tree.column("Síntomas", width=190)
        self.tree.column("Crónicas", width=180)
        self.tree.column("Alergias", width=180)
        self.tree.column("Diagnósticos", width=280)
        self.tree.column("Fecha", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Cargar diagnósticos
        self.load_diagnoses()
        
        # Botones de acción
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=15)
        
        btn_refresh = tk.Button(
            button_frame,
            text="Actualizar",
            font=self.text_font,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.load_diagnoses
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        if self.user_level == "admin":
            btn_delete = tk.Button(
                button_frame,
                text="Eliminar Seleccionado",
                font=self.text_font,
                bg="#e74c3c",
                fg="white",
                padx=15,
                pady=8,
                cursor="hand2",
                command=self.delete_selected
            )
            btn_delete.pack(side=tk.LEFT, padx=5)
        
        btn_logout = tk.Button(
            button_frame,
            text="Cerrar Sesión",
            font=self.text_font,
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.logout
        )
        btn_logout.pack(side=tk.RIGHT, padx=5)
    
    def load_diagnoses(self):
        """Carga los diagnósticos en la tabla"""
        # Limpiar tabla existente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener diagnósticos
        diagnoses = get_diagnoses()
        
        # Insertar diagnósticos en la tabla
        for diagnosis in diagnoses:
            self.tree.insert(
                "",
                tk.END,
                values=diagnosis
            )
        
        if not diagnoses:
            self.tree.insert("", tk.END, values=("", "No hay registros", "", "", "", ""))
    
    def delete_selected(self):
        """Elimina el diagnóstico seleccionado (solo para admin)"""
        selection = self.tree.selection()
        
        if not selection:
            messagebox.showwarning("Aviso", "Por favor seleccione un registro")
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar el registro seleccionado?"):
            item = selection[0]
            values = self.tree.item(item)["values"]
            diagnosis_id = values[0]
            
            delete_diagnosis(diagnosis_id)
            self.load_diagnoses()
            messagebox.showinfo("Éxito", "Registro eliminado exitosamente")
    
    def logout(self):
        """Cierra sesión y regresa al login"""
        if messagebox.askyesno("Confirmar", "¿Desea cerrar sesión?"):
            self.authenticated = False
            self.user_level = None
            self.current_username = None
            self.show_login()
