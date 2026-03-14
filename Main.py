import tkinter as tk
from tkinter import font, messagebox
from patient_module import PatientDiagnosticModule
from admin_module import AdminModule


class MainScreen:
    """Pantalla principal del sistema de diagnóstico médico preliminar"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Diagnóstico Médico Preliminar")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.configure_styles()
        self.create_main_screen()
    
    def configure_styles(self):
        """Configura los estilos de fuentes y colores"""
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=14)
        self.description_font = font.Font(family="Helvetica", size=11)
        self.button_font = font.Font(family="Helvetica", size=12, weight="bold")
    
    def create_main_screen(self):
        """Crea la pantalla principal con descripción y opciones de acceso"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        header_frame = tk.Frame(main_frame, bg="#2c3e50", height=100)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="Sistema de Diagnóstico Médico Preliminar",
            font=self.title_font,
            fg="white",
            bg="#2c3e50",
            pady=20
        )
        title_label.pack()
        
        # Área de descripción
        description_frame = tk.Frame(main_frame, bg="#f0f0f0")
        description_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Título de descripción
        desc_title = tk.Label(
            description_frame,
            text="Bienvenido",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        desc_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Descripción del sistema
        description_text = """Este sistema proporciona una herramienta de apoyo para diagnóstico preliminar. 

IMPORTANTE: Esta aplicación NO sustituye la consulta médica profesional.

Funcionalidades:
• Módulo de Diagnóstico: Permite a los pacientes ingresar síntomas y obtener 
  una orientación preliminar sobre posibles condiciones de salud.

• Módulo Administrativo: Acceso restringido para personal médico autorizado 
  para revisar, analizar y gestionar registros de diagnósticos.

Por favor, consulte con un profesional médico calificado para cualquier 
diagnóstico definitivo y tratamiento médico."""
        
        description_label = tk.Label(
            description_frame,
            text=description_text,
            font=self.description_font,
            fg="#333333",
            bg="#f0f0f0",
            justify=tk.LEFT,
            wraplength=700
        )
        description_label.pack(anchor=tk.W, pady=15)
        
        # Frame de botones
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=40, pady=20)
        
        # Botón para módulo de diagnóstico
        btn_patient = tk.Button(
            button_frame,
            text="Módulo de Diagnóstico",
            font=self.button_font,
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=15,
            cursor="hand2",
            command=self.open_patient_module,
            relief=tk.RAISED,
            bd=2
        )
        btn_patient.pack(side=tk.LEFT, padx=10)
        
        # Botón para módulo administrativo
        btn_admin = tk.Button(
            button_frame,
            text="Módulo Administrativo",
            font=self.button_font,
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=15,
            cursor="hand2",
            command=self.open_admin_module,
            relief=tk.RAISED,
            bd=2
        )
        btn_admin.pack(side=tk.LEFT, padx=10)
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg="#34495e", height=50)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_label = tk.Label(
            footer_frame,
            text="© 2026 Sistema de Diagnóstico Médico | Uso exclusivamente académico y de soporte",
            font=font.Font(family="Helvetica", size=9),
            fg="#ecf0f1",
            bg="#34495e",
            pady=10
        )
        footer_label.pack()
    
    def open_patient_module(self):
        """Abre el módulo de diagnóstico para pacientes"""
        patient_window = tk.Toplevel(self.root)
        patient_window.transient(self.root)
        PatientDiagnosticModule(patient_window)
    
    def open_admin_module(self):
        """Abre el módulo administrativo con autenticación"""
        admin_window = tk.Toplevel(self.root)
        admin_window.transient(self.root)
        AdminModule(admin_window)


def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    app = MainScreen(root)
    root.mainloop()


if __name__ == "__main__":
    main()
