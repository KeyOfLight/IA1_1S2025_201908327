import tkinter as tk
from datetime import datetime
from tkinter import filedialog, font, messagebox, scrolledtext
from database import (
    save_diagnosis,
    construir_reporte_diagnostico,
    generar_informe_pdf,
    obtener_sintomas,
    obtener_diagnostico_prolog,
    obtener_clasificacion_diagnosticos,
    obtener_recomendacion_prolog,
    es_condicion_urgente,
    obtener_perfil_urgencia,
    get_rpa_status,
)


class PatientDiagnosticModule:
    """Módulo de diagnóstico preliminar para pacientes (basado en Prolog)"""
    
    def __init__(self, window):
        self.window = window
        self.window.title("Módulo de Diagnóstico - Pacientes")
        self.window.geometry("900x700")
        self.window.resizable(False, False)
        
        # Obtener síntomas del motor de Prolog
        self.sintomas_disponibles = obtener_sintomas()
        
        # Si Prolog no está disponible, usar fallback
        if not self.sintomas_disponibles:
            print("Prolog no disponible, usando síntomas de fallback")
            self.sintomas_disponibles = [
                "Fiebre", "Tos", "Dolor de cabeza", "Dolor de garganta",
                "Congestión nasal", "Diarrea", "Náuseas", "Fatiga",
                "Dolor abdominal", "Mareos"
            ]

        self.rpa_status = get_rpa_status()
        
        self.configure_styles()
        self.create_interface()
    
    def configure_styles(self):
        """Configura los estilos de fuentes"""
        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.subtitle_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.text_font = font.Font(family="Helvetica", size=10)
    
    def create_interface(self):
        """Crea la interfaz de diagnóstico"""
        main_frame = tk.Frame(self.window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        header = tk.Frame(main_frame, bg="#27ae60")
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="Diagnóstico Preliminar",
            font=self.title_font,
            fg="white",
            bg="#27ae60",
            pady=15
        )
        title.pack()
        
        # Contenido principal
        content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Instrucciones
        instruction_label = tk.Label(
            content_frame,
            text="Seleccione sus síntomas del listado. Puede seleccionar múltiples síntomas:",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para síntomas con scrollbar
        symptoms_frame = tk.Frame(content_frame, bg="white", relief=tk.SUNKEN, bd=1)
        symptoms_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(symptoms_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(
            symptoms_frame,
            bg="white",
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Frame interior para los checkbuttons
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        self.symptom_vars = {}
        self.severity_vars = {}  # Para almacenar severidad de síntomas
        
        # Usar síntomas del motor Prolog
        for symptom in sorted(self.sintomas_disponibles):
            var = tk.BooleanVar()
            self.symptom_vars[symptom] = var
            severity_var = tk.StringVar(value="Moderado")
            self.severity_vars[symptom] = severity_var
            
            # Frame para síntoma + severidad
            symptom_row = tk.Frame(inner_frame, bg="white")
            symptom_row.pack(anchor=tk.W, fill=tk.X, padx=10, pady=3)
            
            # Checkbox del síntoma
            check = tk.Checkbutton(
                symptom_row,
                text=symptom,
                variable=var,
                font=self.text_font,
                bg="white",
                activebackground="#ecf0f1",
                command=lambda s=symptom: self._update_severity_state(s)
            )
            check.pack(side=tk.LEFT, anchor=tk.W)
            
            # Selector de severidad
            severity_frame = tk.Frame(symptom_row, bg="white")
            severity_frame.pack(side=tk.LEFT, padx=(20, 0))
            
            severity_label = tk.Label(
                severity_frame,
                text="Severidad:",
                font=font.Font(family="Helvetica", size=8),
                bg="white",
                fg="#666666"
            )
            severity_label.pack(side=tk.LEFT, padx=(0, 5))
            
            severity_menu = tk.OptionMenu(
                severity_frame,
                severity_var,
                "Leve", "Moderado", "Severo"
            )
            severity_menu.config(
                font=font.Font(family="Helvetica", size=8),
                bg="#ecf0f1",
                activebackground="#d5dbdb"
            )
            severity_menu.pack(side=tk.LEFT)
            
            # Estado inicial: deshabilitado
            self._update_severity_state(symptom)
        
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Campos adicionales del formulario clínico
        extra_info_title = tk.Label(
            content_frame,
            text="Antecedentes del paciente (opcional):",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        extra_info_title.pack(anchor=tk.W, pady=(5, 5))

        extra_info_frame = tk.Frame(content_frame, bg="#f0f0f0")
        extra_info_frame.pack(fill=tk.X, pady=(0, 10))

        chronic_frame = tk.Frame(extra_info_frame, bg="#f0f0f0")
        chronic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        chronic_label = tk.Label(
            chronic_frame,
            text="Enfermedades crónicas (separadas por coma):",
            font=self.text_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        chronic_label.pack(anchor=tk.W)

        self.chronic_diseases_input = scrolledtext.ScrolledText(
            chronic_frame,
            height=3,
            font=self.text_font,
            wrap=tk.WORD
        )
        self.chronic_diseases_input.pack(fill=tk.X, pady=(4, 0))

        allergies_frame = tk.Frame(extra_info_frame, bg="#f0f0f0")
        allergies_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        allergies_label = tk.Label(
            allergies_frame,
            text="Alergias (separadas por coma):",
            font=self.text_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        allergies_label.pack(anchor=tk.W)

        self.allergies_input = scrolledtext.ScrolledText(
            allergies_frame,
            height=3,
            font=self.text_font,
            wrap=tk.WORD
        )
        self.allergies_input.pack(fill=tk.X, pady=(4, 0))
        
        # Botones de acción
        button_frame = tk.Frame(content_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=15)
        
        btn_diagnose = tk.Button(
            button_frame,
            text="Obtener Diagnóstico Preliminar",
            font=self.text_font,
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=10,
            cursor="hand2",
            command=self.generate_diagnosis
        )
        btn_diagnose.pack(side=tk.LEFT, padx=5)
        
        btn_clear = tk.Button(
            button_frame,
            text="Limpiar",
            font=self.text_font,
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=10,
            cursor="hand2",
            command=self.clear_selection
        )
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        btn_close = tk.Button(
            button_frame,
            text="Cerrar",
            font=self.text_font,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=10,
            cursor="hand2",
            command=self.window.destroy
        )
        btn_close.pack(side=tk.RIGHT, padx=5)

        # Estado de RPA/PyAutoGUI
        rpa_fg = "#1e8449" if self.rpa_status.get("available") else "#b9770e"
        rpa_status_label = tk.Label(
            content_frame,
            text=f"RPA PyAutoGUI: {self.rpa_status.get('message', 'Estado no disponible')}",
            font=font.Font(family="Helvetica", size=9),
            fg=rpa_fg,
            bg="#f0f0f0",
            wraplength=820,
            justify=tk.LEFT,
        )
        rpa_status_label.pack(anchor=tk.W, pady=(5, 10))
        
        # Aviso importante
        warning_label = tk.Label(
            content_frame,
            text="⚠ AVISO: Este diagnóstico es preliminar y educativo. No reemplaza la consulta médica profesional.",
            font=font.Font(family="Helvetica", size=9, weight="bold"),
            fg="white",
            bg="#e74c3c",
            wraplength=800,
            padx=10,
            pady=8
        )
        warning_label.pack(fill=tk.X)
    
    def generate_diagnosis(self):
        """Genera el diagnóstico preliminar usando el motor Prolog"""
        # Capturar síntomas con severidad
        symptoms_with_severity = []
        for sym, var in self.symptom_vars.items():
            if var.get():
                severity = self.severity_vars[sym].get()
                symptoms_with_severity.append({
                    "name": sym,
                    "severity": severity
                })
        
        chronic_diseases = self._parse_list_input(self.chronic_diseases_input.get("1.0", tk.END))
        allergies = self._parse_list_input(self.allergies_input.get("1.0", tk.END))
        
        if not symptoms_with_severity:
            messagebox.showwarning("Aviso", "Por favor seleccione al menos un síntoma")
            return
        
        # Extraer solo nombres de síntomas para Prolog
        selected_symptoms = [s["name"] for s in symptoms_with_severity]
        
        # Obtener diagnósticos del motor Prolog
        try:
            diagnosticos_prolog = obtener_diagnostico_prolog(selected_symptoms, symptoms_with_severity)
            if not diagnosticos_prolog:
                messagebox.showwarning("Aviso", "No se encontraron diagnósticos para los síntomas seleccionados")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar Prolog: {str(e)}\n\nAsegúrese de tener SWI-Prolog instalado y pyswip configurado.")
            return
        
        # Generar perfil clinico de urgencia (leve/moderado/severo)
        urgency_profile = obtener_perfil_urgencia(
            symptoms_with_severity,
            conditions=diagnosticos_prolog,
            chronic_diseases=chronic_diseases,
            allergies=allergies,
        )
        clasificacion_diagnosticos = obtener_clasificacion_diagnosticos(diagnosticos_prolog)

        # Crear ventana de resultados
        result_window = tk.Toplevel(self.window)
        result_window.title("Resultados del Diagnóstico Preliminar")
        result_window.geometry("1000x900")
        result_window.resizable(False, False)
        
        # Encabezado
        header = tk.Frame(result_window, bg="#3498db")
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="Resultados del Diagnóstico (Motor Prolog)",
            font=self.title_font,
            fg="white",
            bg="#3498db",
            pady=15
        )
        title.pack()
        
        # Área de contenido (expandible)
        content = tk.Frame(result_window, bg="#f0f0f0")
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=(15, 8))

        # Barra de acciones fija en la parte inferior para que siempre sea visible
        button_frame = tk.Frame(result_window, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=(0, 12))
        
        # Síntomas seleccionados
        symptom_title = tk.Label(
            content,
            text="Síntomas Reportados:",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        symptom_title.pack(anchor=tk.W)
        
        # Mostrar síntomas con severidad
        symptom_text = ", ".join([f"{s['name']} ({s['severity']})" for s in symptoms_with_severity])
        symptom_label = tk.Label(
            content,
            text=symptom_text,
            font=self.text_font,
            fg="#34495e",
            bg="#ecf0f1",
            wraplength=650,
            justify=tk.LEFT,
            padx=10,
            pady=8
        )
        symptom_label.pack(anchor=tk.W, fill=tk.X, pady=(5, 15))

        # Antecedentes reportados
        chronic_title = tk.Label(
            content,
            text="Enfermedades crónicas reportadas:",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        chronic_title.pack(anchor=tk.W)

        chronic_text = ", ".join(chronic_diseases) if chronic_diseases else "No reportadas"
        chronic_label = tk.Label(
            content,
            text=chronic_text,
            font=self.text_font,
            fg="#34495e",
            bg="#ecf0f1",
            wraplength=650,
            justify=tk.LEFT,
            padx=10,
            pady=6
        )
        chronic_label.pack(anchor=tk.W, fill=tk.X, pady=(5, 10))

        allergies_title = tk.Label(
            content,
            text="Alergias reportadas:",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        allergies_title.pack(anchor=tk.W)

        allergies_text = ", ".join(allergies) if allergies else "No reportadas"
        allergies_label = tk.Label(
            content,
            text=allergies_text,
            font=self.text_font,
            fg="#34495e",
            bg="#ecf0f1",
            wraplength=650,
            justify=tk.LEFT,
            padx=10,
            pady=6
        )
        allergies_label.pack(anchor=tk.W, fill=tk.X, pady=(5, 15))

        # Nivel de urgencia segun perfil clinico
        urgency_level = urgency_profile.get("nivel_urgencia", "leve")
        urgency_score = urgency_profile.get("score", 0)
        urgency_action = urgency_profile.get("accion_recomendada", "Consulte a un medico.")
        urgency_colors = {
            "leve": ("#e8f8f5", "#117864"),
            "moderado": ("#fef9e7", "#b9770e"),
            "severo": ("#fdedec", "#922b21"),
        }
        urg_bg, urg_fg = urgency_colors.get(urgency_level, ("#e8f8f5", "#117864"))

        urgency_title = tk.Label(
            content,
            text="Nivel de urgencia segun perfil clinico:",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0",
        )
        urgency_title.pack(anchor=tk.W)

        urgency_label = tk.Label(
            content,
            text=f"{urgency_level.upper()} (Puntaje: {urgency_score})\nAccion recomendada: {urgency_action}",
            font=self.text_font,
            fg=urg_fg,
            bg=urg_bg,
            justify=tk.LEFT,
            wraplength=760,
            padx=10,
            pady=8,
        )
        urgency_label.pack(anchor=tk.W, fill=tk.X, pady=(5, 15))

        # Resumen de clasificacion por sistema/tipo
        classification_title = tk.Label(
            content,
            text="Clasificacion de condiciones (sistema/tipo):",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0",
        )
        classification_title.pack(anchor=tk.W)

        classification_text = tk.Text(content, height=6, width=80, font=self.text_font)
        classification_text.pack(fill=tk.X, pady=(5, 12))

        systems_map = {}
        types_map = {}
        for diagnostico in diagnosticos_prolog:
            condicion_nombre = diagnostico[0] if isinstance(diagnostico, tuple) else str(diagnostico)
            clasificacion = clasificacion_diagnosticos.get(condicion_nombre, {})

            sistema = clasificacion.get("sistema", "No definido")
            tipo = clasificacion.get("tipo", "No definido")

            systems_map.setdefault(sistema, []).append(condicion_nombre)
            types_map.setdefault(tipo, []).append(condicion_nombre)

        classification_text.insert(tk.END, "Por sistema:\n")
        for sistema in sorted(systems_map.keys()):
            condiciones = ", ".join(sorted(set(systems_map[sistema])))
            classification_text.insert(tk.END, f"- {sistema}: {condiciones}\n")

        classification_text.insert(tk.END, "\nPor tipo:\n")
        for tipo in sorted(types_map.keys()):
            condiciones = ", ".join(sorted(set(types_map[tipo])))
            classification_text.insert(tk.END, f"- {tipo}: {condiciones}\n")

        classification_text.config(state=tk.DISABLED)
        
        # Posibles condiciones (desde Prolog)
        condition_title = tk.Label(
            content,
            text="Posibles Condiciones de Salud (Motor Prolog - por relevancia):",
            font=self.subtitle_font,
            fg="#2c3e50",
            bg="#f0f0f0"
        )
        condition_title.pack(anchor=tk.W)
        
        condition_text = tk.Text(content, height=8, width=80, font=self.text_font)
        condition_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Mostrar diagnósticos de Prolog con relevancia
        for i, (condition, score) in enumerate(diagnosticos_prolog, 1):
            clasificacion = clasificacion_diagnosticos.get(condition, {})
            sistema = clasificacion.get("sistema", "No definido")
            tipo = clasificacion.get("tipo", "No definido")

            relevance = "Alta" if score >= 2 else "Media"
            urgencia = " ⚠️ URGENTE" if es_condicion_urgente(condition) else ""
            recomendacion = obtener_recomendacion_prolog(condition)
            if es_condicion_urgente(condition):
                action = "Acuda a emergencias hoy mismo."
            elif urgency_level == "severo":
                action = "Busque atencion medica el mismo dia."
            elif urgency_level == "moderado":
                action = "Programe consulta medica en menos de 24 horas."
            else:
                action = "Cuidados en casa y vigilancia de evolucion."

            condition_text.insert(
                tk.END,
                f"{i}. {condition} (Relevancia: {relevance}){urgencia}\n"
                f"   Sistema: {sistema} | Tipo: {tipo}\n"
                f"   Recomendacion: {recomendacion}\n"
                f"   Accion: {action}\n\n",
            )
        
        condition_text.config(state=tk.DISABLED)
        
        # Recomendación final
        recommendation_frame = tk.Frame(content, bg="#fff3cd", relief=tk.SUNKEN, bd=1)
        recommendation_frame.pack(fill=tk.X, pady=15)
        
        recommendation_text = """IMPORTANTE - RECOMENDACIÓN:

Este diagnóstico es PRELIMINAR y EDUCATIVO solamente. 
No debe ser utilizado como sustituto de la consulta médica profesional.

Por favor, diríjase a un médico calificado para:
• Confirmación del diagnóstico
• Evaluación clínica completa  
• Tratamiento médico apropiado
• Cualquier inquietud sobre su salud"""
        
        recommendation_label = tk.Label(
            recommendation_frame,
            text=recommendation_text,
            font=font.Font(family="Helvetica", size=9),
            fg="#856404",
            bg="#fff3cd",
            justify=tk.LEFT,
            padx=10,
            pady=10
        )
        recommendation_label.pack(anchor=tk.W)
        
        # Botones (anclados en barra inferior)
        
        btn_save = tk.Button(
            button_frame,
            text="Guardar Registro",
            font=self.text_font,
            bg="#27ae60",
            fg="white",
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.save_diagnosis_record(
                symptoms_with_severity,
                diagnosticos_prolog,
                chronic_diseases=chronic_diseases,
                allergies=allergies,
                urgency_profile=urgency_profile,
            )
        )
        btn_save.pack(side=tk.LEFT, padx=5)

        btn_save_rpa = tk.Button(
            button_frame,
            text="Guardar + RPA (PyAutoGUI)",
            font=self.text_font,
            bg="#2e86c1",
            fg="white",
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.save_diagnosis_record(
                symptoms_with_severity,
                diagnosticos_prolog,
                run_rpa=True,
                chronic_diseases=chronic_diseases,
                allergies=allergies,
                urgency_profile=urgency_profile,
            )
        )
        btn_save_rpa.pack(side=tk.LEFT, padx=5)

        btn_pdf = tk.Button(
            button_frame,
            text="Descargar Informe PDF",
            font=self.text_font,
            bg="#1f618d",
            fg="white",
            padx=10,
            pady=8,
            cursor="hand2",
            command=lambda: self.download_pdf_report(
                symptoms=symptoms_with_severity,
                conditions=diagnosticos_prolog,
                chronic_diseases=chronic_diseases,
                allergies=allergies,
                urgency_profile=urgency_profile,
            )
        )
        btn_pdf.pack(side=tk.LEFT, padx=5)
        
        btn_close = tk.Button(
            button_frame,
            text="Cerrar",
            font=self.text_font,
            bg="#e74c3c",
            fg="white",
            padx=10,
            pady=8,
            cursor="hand2",
            command=result_window.destroy
        )
        btn_close.pack(side=tk.RIGHT, padx=5)
    
    def save_diagnosis_record(self, symptoms, conditions, run_rpa=False, chronic_diseases=None, allergies=None, urgency_profile=None):
        """Guarda el registro del diagnóstico (datos de Prolog)"""
        result = save_diagnosis(
            symptoms,
            conditions,
            run_rpa=run_rpa,
            return_details=True,
            chronic_diseases=chronic_diseases,
            allergies=allergies,
            urgency_profile=urgency_profile,
        )

        if not result.get("success"):
            messagebox.showerror(
                "Error",
                f"No se pudo guardar el registro: {result.get('error', 'Error desconocido')}"
            )
            return

        if not run_rpa:
            messagebox.showinfo(
                "Éxito",
                "El registro ha sido guardado exitosamente\n(Procesado por motor Prolog)"
            )
            return

        rpa_result = result.get("rpa") or {}
        if rpa_result.get("executed"):
            messagebox.showinfo(
                "Éxito - RPA Ejecutado",
                "Registro guardado y flujo RPA completado con PyAutoGUI.\n\n"
                f"Reporte: {rpa_result.get('report_path')}\n"
                f"Captura: {rpa_result.get('screenshot_path')}\n"
                f"PDF: {rpa_result.get('pdf_report_path', 'No generado')}"
            )
            return

        pdf_message = (
            f"PDF generado: {rpa_result.get('pdf_report_path')}"
            if rpa_result.get("pdf_generated")
            else "PDF no generado"
        )
        messagebox.showwarning(
            "Registro guardado - RPA parcial",
            "El diagnóstico fue guardado, pero el flujo RPA no se completó totalmente.\n\n"
            f"Detalle: {rpa_result.get('message', 'Sin detalle')}\n"
            f"Reporte generado: {rpa_result.get('report_path', 'No disponible')}\n"
            f"{pdf_message}"
        )

    def download_pdf_report(self, symptoms, conditions, chronic_diseases=None, allergies=None, urgency_profile=None):
        """Permite descargar informe PDF completo del analisis actual."""
        try:
            report_payload = construir_reporte_diagnostico(
                symptoms=symptoms,
                conditions=conditions,
                chronic_diseases=chronic_diseases,
                allergies=allergies,
                urgency_profile=urgency_profile,
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo preparar el informe: {e}")
            return

        default_name = f"informe_diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        selected_path = filedialog.asksaveasfilename(
            title="Guardar informe PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=default_name,
        )

        if not selected_path:
            return

        try:
            pdf_path = generar_informe_pdf(report_payload, output_path=selected_path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")
            return

        messagebox.showinfo(
            "Informe PDF generado",
            "Se generó correctamente el informe con diagnosticos, afinidad, reglas activadas y tratamiento seguro.\n\n"
            f"Ruta: {pdf_path}"
        )
    
    def clear_selection(self):
        """Limpia la selección de síntomas"""
        for var in self.symptom_vars.values():
            var.set(False)
        self.chronic_diseases_input.delete("1.0", tk.END)
        self.allergies_input.delete("1.0", tk.END)

    def _update_severity_state(self, symptom):
        """Habilita/deshabilita el selector de severidad según si el síntoma está seleccionado"""
        # Este método se llama cuando el checkbox cambia
        # La severidad se maneja dinámicamente en generate_diagnosis
        pass

    def _parse_list_input(self, raw_text):
        """Convierte texto libre (comas o saltos de línea) en lista sin duplicados."""
        normalized = raw_text.replace("\n", ",")
        values = [value.strip() for value in normalized.split(",") if value.strip()]

        clean_values = []
        seen = set()
        for value in values:
            key = value.lower()
            if key in seen:
                continue
            seen.add(key)
            clean_values.append(value)

        return clean_values
