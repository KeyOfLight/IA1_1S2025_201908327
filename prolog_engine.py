
import os
import re
import unicodedata
from pathlib import Path

try:
    from pyswip import Prolog
except ImportError:
    print("ERROR: pyswip no está instalado.")
    print("Instálalo con: pip install pyswip")
    raise


class PrologDiagnosticEngine:
    """Motor de diagnóstico basado en Prolog"""
    
    def __init__(self):
        """Inicializa el motor de Prolog"""
        self.prolog = Prolog()
         
        rules_file = os.path.join(os.path.dirname(__file__), "diagnostic_rules.pl")
        
        if not os.path.exists(rules_file):
            raise FileNotFoundError(f"Archivo de reglas no encontrado: {rules_file}")
         
        try:
            self.prolog.consult(rules_file)
            print(f" Reglas de Prolog cargadas desde: {rules_file}")
        except Exception as e:
            raise Exception(f"Error al cargar reglas Prolog: {e}")

        # Secuencias comunes de texto mal decodificado (UTF-8 interpretado como Latin-1)
        self._mojibake_map = {
            "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú", "Ã±": "ñ", "Ã¼": "ü",
            "Ã": "Á", "Ã‰": "É", "Ã": "Í", "Ã“": "Ó", "Ãš": "Ú", "Ã‘": "Ñ", "Ãœ": "Ü",
            "ã¡": "á", "ã©": "é", "ã­": "í", "ã³": "ó", "ãº": "ú", "ã±": "ñ", "ã¼": "ü",
            "â": "'", "â": '"', "â": '"', "â": "-", "â": "-", "Â": "",
        }
        self._display_name_overrides = {
            "migrana": "Migraña",
        }
    
    def obtener_sintomas(self):
        """Obtiene la lista de síntomas disponibles"""
        try:
            sintomas = []
            for result in self.prolog.query("todos_sintomas(S)"):
                sintomas_temp = result["S"]
                
                sintomas = self._prolog_list_to_python(sintomas_temp)
                break
            
            
            sintomas_formateados = [self._format_prolog_value(s) for s in sintomas]
            return sorted(sintomas_formateados)
        except Exception as e:
            print(f"Error obteniendo síntomas: {e}")
            return []
    
    def obtener_diagnosticos(self, sintomas_seleccionados, symptoms_with_severity=None):
        """
        Obtiene diagnósticos basados en síntomas seleccionados
        
        Args:
            sintomas_seleccionados: Lista de síntomas (strings con espacios)
            symptoms_with_severity: Lista de diccionarios con síntoma y severidad (opcional)
        
        Returns:
            Lista de tuplas (condición, relevancia)
        """
        try:
            # Convertir síntomas a formato Prolog
            sintomas_prolog = [self._to_prolog_identifier(s) for s in sintomas_seleccionados]
            
            # Si tenemos información de severidad, aplicar ponderación
            if symptoms_with_severity:
                # Crear mapa de severidad para acceso rápido
                severity_map = {}
                for symptom_dict in symptoms_with_severity:
                    symptom_name = self._to_prolog_identifier(symptom_dict.get("name", ""))
                    severity = symptom_dict.get("severity", "moderado").lower()
                    severity_map[symptom_name] = severity
                
                # Aplicar ponderación: síntomas severos contribuyen más a la relevancia
                diagnosticos_ponderados = {}
                for sintoma in sintomas_prolog:
                    severity = severity_map.get(sintoma, "moderado")
                    weight = self._get_severity_weight(severity)
                    
                    # Obtener todas las condiciones relacionadas con este síntoma
                    sintoma_atom = self._to_prolog_atom(sintoma)
                    query_cond = f"relacion({sintoma_atom}, C)"
                    for result in self.prolog.query(query_cond):
                        condition = result["C"]
                        if condition not in diagnosticos_ponderados:
                            diagnosticos_ponderados[condition] = 0
                        diagnosticos_ponderados[condition] += weight
                
                # Ordenar por peso y convertir a formato esperado
                diagnosticos = sorted(
                    [(cond, weight) for cond, weight in diagnosticos_ponderados.items()],
                    key=lambda x: x[1],
                    reverse=True
                )
                return [(self._format_prolog_value(cond), weight) for cond, weight in diagnosticos]
            
            # Método original sin severidad para compatibilidad hacia atrás
            sintomas_formato_prolog = self._python_list_to_prolog(sintomas_prolog)
            
            diagnosticos = []
            query = f"diagnosticos_ordenados({sintomas_formato_prolog}, D)"
            
            for result in self.prolog.query(query):
                diagnosticos_lista = result["D"]

                diagnosticos_con_relevancia = []


                if isinstance(diagnosticos_lista, str):
                    diagnosticos_con_relevancia = self._parse_diagnosticos_list_string(diagnosticos_lista)


                elif hasattr(diagnosticos_lista, '__iter__'):
                    for item in diagnosticos_lista:
                        diagnostico = self._parse_diagnostico_item(item)
                        if diagnostico:
                            diagnosticos_con_relevancia.append(diagnostico)


                    if not diagnosticos_con_relevancia:
                        diagnosticos_con_relevancia = self._parse_diagnosticos_list_string(str(diagnosticos_lista))


                else:
                    diagnostico = self._parse_diagnostico_item(diagnosticos_lista)
                    if diagnostico:
                        diagnosticos_con_relevancia.append(diagnostico)

                diagnosticos = diagnosticos_con_relevancia
                break
            
            return diagnosticos
        except Exception as e:
            print(f"Error obteniendo diagnósticos: {e}")
            return []
    
    def obtener_recomendacion(self, condicion):
        """
        Obtiene la recomendación médica para una condición
        
        Args:
            condicion: Nombre de la condición (string con espacios)
        
        Returns:
            String con la recomendación
        """
        try:
            condicion_prolog = self._to_prolog_atom(condicion)
            
            for result in self.prolog.query(f"obtener_recomendacion({condicion_prolog}, R)"):
                recomendacion = self._normalize_text(result["R"])
                if recomendacion:
                    return recomendacion
            
            return "Consulte con un profesional médico para más información."
        except Exception as e:
            print(f"Error obteniendo recomendación: {e}")
            return "Consulte con un profesional médico para más información."

    def obtener_clasificacion_condicion(self, condicion):
        """
        Obtiene la clasificación de una condición por sistema y tipo

        Args:
            condicion: Nombre de la condición (string con espacios)

        Returns:
            Diccionario con condicion, sistema y tipo
        """
        try:
            condicion_atom = self._to_prolog_atom(condicion)
            for result in self.prolog.query(f"obtener_clasificacion_condicion({condicion_atom}, S, T)"):
                return {
                    "condicion": str(condicion),
                    "sistema": self._format_prolog_value(result.get("S")),
                    "tipo": self._format_prolog_value(result.get("T")),
                }

            return {
                "condicion": str(condicion),
                "sistema": "No definido",
                "tipo": "No definido",
            }
        except Exception as e:
            print(f"Error obteniendo clasificación de condición: {e}")
            return {
                "condicion": str(condicion),
                "sistema": "No definido",
                "tipo": "No definido",
            }

    def obtener_condiciones_por_sistema(self, sistema):
        """
        Obtiene condiciones clasificadas dentro de un sistema

        Args:
            sistema: Nombre del sistema (ej. respiratorio)

        Returns:
            Lista de condiciones formateadas
        """
        try:
            sistema_atom = self._to_prolog_atom(sistema)
            for result in self.prolog.query(f"condiciones_por_sistema({sistema_atom}, C)"):
                condiciones = self._prolog_list_to_python(result.get("C", []))
                return sorted([self._format_prolog_value(c) for c in condiciones])
            return []
        except Exception as e:
            print(f"Error obteniendo condiciones por sistema: {e}")
            return []

    def obtener_condiciones_por_tipo(self, tipo):
        """
        Obtiene condiciones clasificadas por tipo clínico

        Args:
            tipo: Nombre del tipo (ej. infecciosa_viral)

        Returns:
            Lista de condiciones formateadas
        """
        try:
            tipo_atom = self._to_prolog_atom(tipo)
            for result in self.prolog.query(f"condiciones_por_tipo({tipo_atom}, C)"):
                condiciones = self._prolog_list_to_python(result.get("C", []))
                return sorted([self._format_prolog_value(c) for c in condiciones])
            return []
        except Exception as e:
            print(f"Error obteniendo condiciones por tipo: {e}")
            return []

    def obtener_sistemas_clasificacion(self):
        """Obtiene todos los sistemas disponibles para clasificar condiciones."""
        try:
            for result in self.prolog.query("sistemas_disponibles(S)"):
                sistemas = self._prolog_list_to_python(result.get("S", []))
                return sorted([self._format_prolog_value(s) for s in sistemas])
            return []
        except Exception as e:
            print(f"Error obteniendo sistemas de clasificación: {e}")
            return []

    def obtener_tipos_clasificacion(self):
        """Obtiene todos los tipos disponibles para clasificar condiciones."""
        try:
            for result in self.prolog.query("tipos_condicion_disponibles(T)"):
                tipos = self._prolog_list_to_python(result.get("T", []))
                return sorted([self._format_prolog_value(t) for t in tipos])
            return []
        except Exception as e:
            print(f"Error obteniendo tipos de clasificación: {e}")
            return []
    
    def es_urgente(self, condicion):
        """
        Verifica si una condición requiere atención inmediata
        
        Args:
            condicion: Nombre de la condición (string con espacios)
        
        Returns:
            Boolean
        """
        try:
            condicion_prolog = self._to_prolog_atom(condicion)
            
            for _ in self.prolog.query(f"es_urgente({condicion_prolog})"):
                return True
            
            return False
        except Exception as e:
            print(f"Error verificando urgencia: {e}")
            return False
    
    def obtener_descripcion_sintoma(self, sintoma):
        """
        Obtiene la descripción de un síntoma
        
        Args:
            sintoma: Nombre del síntoma (string con espacios)
        
        Returns:
            String con la descripción
        """
        try:
            sintoma_prolog = self._to_prolog_atom(sintoma)
            
            for result in self.prolog.query(f"descripcion_sintoma({sintoma_prolog}, D)"):
                descripcion = self._normalize_text(result["D"])
                if descripcion:
                    return descripcion
            
            return "Sin descripción disponible."
        except Exception as e:
            print(f"Error obteniendo descripción: {e}")
            return "Sin descripción disponible."
    
    def obtener_severidad_sintoma(self, sintoma):
        """
        Obtiene el nivel de severidad de un síntoma
        
        Args:
            sintoma: Nombre del síntoma (string con espacios)
        
        Returns:
            String: 'alta', 'media' o 'baja'
        """
        try:
            sintoma_prolog = self._to_prolog_atom(sintoma)
            
            for result in self.prolog.query(f"severidad({sintoma_prolog}, S)"):
                severidad = self._normalize_text(result["S"])
                if severidad:
                    return severidad
            
            return "media"
        except Exception as e:
            print(f"Error obteniendo severidad: {e}")
            return "media"
    
    # ==================== MÉTODOS AUXILIARES ====================
    
    def _get_severity_weight(self, severity):
        """
        Obtiene el peso (ponderación) basado en la severidad del síntoma
        
        Args:
            severity: String con la severidad ('leve', 'moderado', 'severo')
        
        Returns:
            Número entero que representa el peso
        """
        severity_lower = severity.lower()
        severity_weights = {
            'severo': 3,
            'moderado': 2,
            'leve': 1,
            'alto': 3,
            'medio': 2,
            'bajo': 1
        }
        return severity_weights.get(severity_lower, 2)  # Defecto a moderado (2)

    def _to_prolog_atom(self, value):
        """Normaliza un string de Python a átomo Prolog seguro."""
        atom = self._to_prolog_identifier(value)
        atom = atom.replace("'", "''")
        return f"'{atom}'"

    def _to_prolog_identifier(self, value):
        """Convierte texto de UI a identificador ASCII seguro para Prolog."""
        text = self._normalize_text(value).lower().replace(' ', '_')
        normalized = unicodedata.normalize("NFKD", text)
        return ''.join(char for char in normalized if not unicodedata.combining(char))

    def _normalize_text(self, value):
        """Corrige texto mal codificado y limpia comillas externas."""
        if isinstance(value, bytes):
            try:
                text = value.decode("utf-8").strip()
            except UnicodeDecodeError:
                text = value.decode("latin-1", errors="replace").strip()
        else:
            text = str(value).strip()

        if not text:
            return text

        # Evita dobles comillas cuando ya viene como átomo/string serializado.
        if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
            text = text[1:-1]

        for bad, good in self._mojibake_map.items():
            if bad in text:
                text = text.replace(bad, good)

        return text

    def _format_prolog_value(self, value):
        """Convierte un átomo Prolog a texto amigable para UI."""
        if value is None:
            return "No definido"

        text = self._normalize_text(value)
        if not text or text.lower() in {"none", "no_definido"}:
            return "No definido"

        text_lower = text.lower()
        if text_lower in self._display_name_overrides:
            return self._display_name_overrides[text_lower]

        return text.replace('_', ' ').title()
    
    def _python_list_to_prolog(self, py_list):
        """Convierte una lista de Python a formato de lista Prolog"""
        if not py_list:
            return "[]"
        
        items = ", ".join([self._to_prolog_atom(item) for item in py_list])
        return f"[{items}]"

    def _parse_diagnostico_item(self, item):
        """Convierte un resultado de Prolog en tupla (condición, relevancia)."""
        try:
            # Caso directo: (condicion, relevancia)
            if isinstance(item, (tuple, list)) and len(item) == 2:
                condicion, relevancia = item
                condicion_limpia = self._normalize_text(condicion)
                return (self._format_prolog_value(condicion_limpia), int(relevancia))

            # Fallback robusto para representaciones en string:
            # - "gripe-1"
            # - "(gripe, 1)"
            item_str = str(item).strip()

            # Formato: (condicion, numero)
            match_par = re.match(r"^\(\s*([^,]+)\s*,\s*(-?\d+)\s*\)$", item_str)
            if match_par:
                condicion = self._normalize_text(match_par.group(1))
                relevancia = int(match_par.group(2))
                return (self._format_prolog_value(condicion), relevancia)

            # Formato: condicion-numero
            match_guion = re.match(r"^(.+)-(-?\d+)$", item_str)
            if match_guion:
                condicion = self._normalize_text(match_guion.group(1))
                relevancia = int(match_guion.group(2))
                return (self._format_prolog_value(condicion), relevancia)

            return None
        except (TypeError, ValueError):
            return None

    def _parse_diagnosticos_list_string(self, lista_str):
        """Parsea una lista de diagnósticos serializada en string.

        Soporta formatos como:
        - "[gripe-3,resfriado-1]"
        - "[(gripe, 3), (resfriado, 1)]"
        """
        diagnosticos = []

        if not lista_str:
            return diagnosticos

        texto = str(lista_str).strip()

        # Formato: (condicion, numero)
        for condicion, relevancia in re.findall(r"\(\s*([^,\)]+)\s*,\s*(-?\d+)\s*\)", texto):
            condicion_limpia = self._normalize_text(condicion)
            diagnosticos.append((self._format_prolog_value(condicion_limpia), int(relevancia)))

        if diagnosticos:
            return diagnosticos

        # Formato: condicion-numero
        for condicion, relevancia in re.findall(r"([^,\]\s\)]+)\s*-\s*(-?\d+)", texto):
            condicion_limpia = self._normalize_text(condicion)
            diagnosticos.append((self._format_prolog_value(condicion_limpia), int(relevancia)))

        return diagnosticos
    
    def _prolog_list_to_python(self, prolog_list):
        """Convierte una lista de Prolog a lista de Python"""
        result = []
        
        if isinstance(prolog_list, str):
            # Si es un string, parsearlo
            return [prolog_list]
        
        # Iterar a través de la lista de Prolog
        try:
            if hasattr(prolog_list, '__iter__'):
                for item in prolog_list:
                    result.append(self._normalize_text(item))
        except:
            result.append(self._normalize_text(prolog_list))
        
        return result
    
    # ==================== MEDICAMENTOS ====================
    
    def obtener_medicamentos_para(self, condicion):
        """
        Obtiene medicamentos para una condición médica
        
        Args:
            condicion: Nombre de la condición (string con espacios o con guiones bajos)
        
        Returns:
            Lista de nombres de medicamentos
        """
        try:
            # Normalizar nombre de condición para Prolog
            condicion_prolog = self._to_prolog_atom(condicion)
            
            medicamentos = []
            for result in self.prolog.query(f"medicamentos_para({condicion_prolog}, M)"):
                meds = result["M"]
                if hasattr(meds, '__iter__') and not isinstance(meds, str):
                    medicamentos = [self._normalize_text(m).strip("'") for m in meds]
                elif isinstance(meds, str):
                    # Procesar string en formato Prolog
                    meds_clean = self._normalize_text(meds).replace('[', '').replace(']', '').replace("'", '')
                    medicamentos = [m.strip() for m in meds_clean.split(',') if m.strip()]
                break
            
            return medicamentos
        except Exception as e:
            print(f"Error obteniendo medicamentos para {condicion}: {e}")
            return []
    
    def obtener_tipo_medicamento(self, medicamento):
        """
        Obtiene el tipo/categoría de un medicamento
        
        Args:
            medicamento: Nombre del medicamento
        
        Returns:
            String con la categoría
        """
        try:
            med_prolog = self._to_prolog_atom(medicamento)
            
            for result in self.prolog.query(f"tipo_medicamento({med_prolog}, T)"):
                tipo = self._normalize_text(result["T"])
                if tipo:
                    return tipo
            
            return "Tipo no disponible"
        except Exception as e:
            print(f"Error obteniendo tipo de medicamento: {e}")
            return "Tipo no disponible"
    
    def obtener_dosis_medicamento(self, medicamento):
        """
        Obtiene la dosis recomendada de un medicamento
        
        Args:
            medicamento: Nombre del medicamento
        
        Returns:
            String con dosis recomendada
        """
        try:
            med_prolog = self._to_prolog_atom(medicamento)
            
            for result in self.prolog.query(f"dosis_recomendada({med_prolog}, D)"):
                dosis = self._normalize_text(result["D"])
                if dosis:
                    return dosis
            
            return "Dosis no disponible"
        except Exception as e:
            print(f"Error obteniendo dosis: {e}")
            return "Dosis no disponible"
    
    def obtener_efectos_secundarios(self, medicamento):
        """
        Obtiene efectos secundarios de un medicamento
        
        Args:
            medicamento: Nombre del medicamento
        
        Returns:
            String con descripción de efectos
        """
        try:
            med_prolog = self._to_prolog_atom(medicamento)
            
            for result in self.prolog.query(f"efecto_secundario({med_prolog}, E)"):
                efectos = self._normalize_text(result["E"])
                if efectos:
                    return efectos
            
            return "Sin efectos secundarios conocidos o no disponible"
        except Exception as e:
            print(f"Error obteniendo efectos secundarios: {e}")
            return "Sin efectos secundarios conocidos o no disponible"
    
    def obtener_contraindicaciones(self, medicamento):
        """
        Obtiene contraindicaciones de un medicamento
        
        Args:
            medicamento: Nombre del medicamento
        
        Returns:
            Lista de condiciones contraindicadas
        """
        try:
            med_prolog = self._to_prolog_atom(medicamento)
            
            contraindicaciones = []
            for result in self.prolog.query(f"contraindicacion({med_prolog}, C)"):
                contraind = self._normalize_text(result["C"])
                if contraind:
                    contraindicaciones.append(self._format_prolog_value(contraind))
            
            return contraindicaciones
        except Exception as e:
            print(f"Error obteniendo contraindicaciones: {e}")
            return []
    
    def obtener_todos_medicamentos(self):
        """
        Obtiene lista de todos los medicamentos disponibles
        
        Returns:
            Lista de nombres de medicamentos
        """
        try:
            medicamentos = []
            for result in self.prolog.query("todos_medicamentos(M)"):
                meds = result["M"]
                if hasattr(meds, '__iter__') and not isinstance(meds, str):
                    medicamentos = [self._normalize_text(m).strip("'") for m in meds]
                break
            
            return medicamentos
        except Exception as e:
            print(f"Error obteniendo medicamentos: {e}")
            return []

    def obtener_medicamentos_seguros(self, diagnostico, alergias=None, enfermedades_cronicas=None):
        """
        Obtiene medicamentos seguros para un diagnóstico, evitando conflictos con
        alergias y enfermedades crónicas del paciente
        
        Args:
            diagnostico: Nombre de la condición/enfermedad (string con espacios o guiones bajos)
            alergias: Lista de alergias del paciente (ej. ['Penicilina', 'Aspirina'])
            enfermedades_cronicas: Lista de enfermedades crónicas (ej. ['Asma', 'Hipertensión'])
        
        Returns:
            Lista de medicamentos seguros (nombres)
        """
        try:
            diagnostico_prolog = self._to_prolog_atom(diagnostico)
            alergias = alergias or []
            enfermedades_cronicas = enfermedades_cronicas or []
            
            # Convertir listas a formato Prolog
            alergias_prolog = [self._to_prolog_atom(a) for a in alergias]
            enfermedades_prolog = [self._to_prolog_atom(e) for e in enfermedades_cronicas]
            
            query = f"medicamentos_seguros_para_paciente({diagnostico_prolog}, [{', '.join(alergias_prolog)}], [{', '.join(enfermedades_prolog)}], M)"
            
            medicamentos_seguros = []
            for result in self.prolog.query(query):
                meds = result.get("M", [])
                if hasattr(meds, '__iter__') and not isinstance(meds, str):
                    medicamentos_seguros = [self._normalize_text(m).strip("'") for m in meds]
                elif isinstance(meds, str):
                    meds_clean = self._normalize_text(meds).replace('[', '').replace(']', '').replace("'", '')
                    medicamentos_seguros = [m.strip() for m in meds_clean.split(',') if m.strip()]
                break
            
            return medicamentos_seguros
        except Exception as e:
            print(f"Error obteniendo medicamentos seguros para {diagnostico}: {e}")
            return []

    def obtener_medicamentos_bloqueados(self, diagnostico, alergias=None, enfermedades_cronicas=None):
        """
        Obtiene medicamentos bloqueados para un diagnóstico, indicando el motivo
        
        Args:
            diagnostico: Nombre de la condición/enfermedad (string con espacios o guiones bajos)
            alergias: Lista de alergias del paciente
            enfermedades_cronicas: Lista de enfermedades crónicas
        
        Returns:
            Lista de dicts con estructura:
            [
                {
                    "medicamento": "amoxicilina",
                    "motivo": "alergia",
                    "razon": "Penicilina"
                },
                ...
            ]
        """
        try:
            diagnostico_prolog = self._to_prolog_atom(diagnostico)
            alergias = alergias or []
            enfermedades_cronicas = enfermedades_cronicas or []
            
            # Convertir listas a formato Prolog
            alergias_prolog = [self._to_prolog_atom(a) for a in alergias]
            enfermedades_prolog = [self._to_prolog_atom(e) for e in enfermedades_cronicas]
            
            query = f"medicamentos_bloqueados_para_paciente({diagnostico_prolog}, [{', '.join(alergias_prolog)}], [{', '.join(enfermedades_prolog)}], M)"
            
            medicamentos_bloqueados = []
            for result in self.prolog.query(query):
                meds = result.get("M", [])
                if hasattr(meds, '__iter__') and not isinstance(meds, str):
                    for med_item in meds:
                        med_str = self._normalize_text(med_item).strip("'")
                        medicamentos_bloqueados.append(med_str)
                elif isinstance(meds, str):
                    meds_clean = self._normalize_text(meds).replace('[', '').replace(']', '').replace("'", '')
                    for med_item in meds_clean.split(','):
                        med_str = med_item.strip()
                        if med_str:
                            medicamentos_bloqueados.append(med_str)
                break
            
            return medicamentos_bloqueados
        except Exception as e:
            print(f"Error obteniendo medicamentos bloqueados para {diagnostico}: {e}")
            return []

    def sugerir_tratamiento_seguro(self, diagnostico, alergias=None, enfermedades_cronicas=None):
        """
        Sugiere medicamentos de forma segura para un diagnóstico, considerando
        el perfil clínico del paciente (alergias y enfermedades crónicas)
        
        Args:
            diagnostico: Nombre de la enfermedad/condición
            alergias: Lista de alergias del paciente
            enfermedades_cronicas: Lista de enfermedades crónicas
        
        Returns:
            Diccionario con medicamentos seguros y bloqueados
        """
        alergias = alergias or []
        enfermedades_cronicas = enfermedades_cronicas or []
        
        medicamentos_seguros = self.obtener_medicamentos_seguros(diagnostico, alergias, enfermedades_cronicas)
        medicamentos_bloqueados = self.obtener_medicamentos_bloqueados(diagnostico, alergias, enfermedades_cronicas)
        
        resultado = {
            "diagnostico": diagnostico,
            "perfil_paciente": {
                "alergias": alergias,
                "enfermedades_cronicas": enfermedades_cronicas
            },
            "medicamentos_seguros": medicamentos_seguros,
            "medicamentos_bloqueados": medicamentos_bloqueados,
            "resumen": {
                "total_opciones": len(medicamentos_seguros) + len(medicamentos_bloqueados),
                "medicamentos_disponibles": len(medicamentos_seguros),
                "medicamentos_contraindicados": len(medicamentos_bloqueados)
            }
        }
        
        return resultado


    # ==================== PERFIL CLINICO Y URGENCIA ====================

    def evaluar_perfil_urgencia(self, symptoms_with_severity, condiciones=None, chronic_diseases=None, allergies=None):
        """Genera nivel de urgencia clinica segun perfil del paciente.

        Returns:
            dict con score, nivel_urgencia (leve/moderado/severo) y accion_recomendada.
        """
        severity_weights = {"leve": 1, "moderado": 2, "severo": 3}
        score = 0

        for item in symptoms_with_severity or []:
            sev = str(item.get("severity", "moderado")).strip().lower()
            score += severity_weights.get(sev, 2)

        # Si hay condicion urgente detectada en diagnostico, eleva significativamente el riesgo.
        for condicion in condiciones or []:
            nombre = condicion[0] if isinstance(condicion, tuple) else str(condicion)
            if self.es_urgente(nombre):
                score += 5
                break

        score += min(len(chronic_diseases or []), 2)
        score += min(len(allergies or []), 1)

        if score >= 11:
            nivel = "severo"
        elif score >= 6:
            nivel = "moderado"
        else:
            nivel = "leve"

        action_by_level = {
            "severo": "Acuda a emergencias de inmediato y evite automedicarse.",
            "moderado": "Solicite consulta medica en menos de 24 horas y vigile signos de alarma.",
            "leve": "Manejo en casa con observacion; consulte si empeora o persiste."
        }

        return {
            "score": score,
            "nivel_urgencia": nivel,
            "accion_recomendada": action_by_level[nivel],
        }


# Instancia global del motor
_engine = None


def get_prolog_engine():
    """Obtiene instancia global del motor de Prolog"""
    global _engine
    if _engine is None:
        _engine = PrologDiagnosticEngine()
    return _engine
