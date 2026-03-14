"""
Utilidades RPA usando PyAutoGUI para el flujo de diagnostico.
Genera evidencia automatica (reporte de texto + captura de pantalla).
"""

import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RPA_OUTPUT_DIR = os.path.join(BASE_DIR, "rpa_output")

PYAUTOGUI_AVAILABLE = False
PYAUTOGUI_IMPORT_ERROR = ""

try:
    import pyautogui  # type: ignore

    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except Exception as exc:  # pragma: no cover - depende del entorno
    PYAUTOGUI_IMPORT_ERROR = str(exc)


def _ensure_output_dir():
    """Crea el directorio de salida de RPA si no existe."""
    os.makedirs(RPA_OUTPUT_DIR, exist_ok=True)


def get_rpa_status():
    """Retorna el estado de disponibilidad de PyAutoGUI."""
    if PYAUTOGUI_AVAILABLE:
        return {
            "available": True,
            "message": "PyAutoGUI disponible para automatizacion RPA."
        }

    error_detail = PYAUTOGUI_IMPORT_ERROR or "No se pudo importar pyautogui."
    return {
        "available": False,
        "message": f"PyAutoGUI no disponible: {error_detail}"
    }


def _build_report_text(diagnosis_record):
    """Construye el texto del reporte de evidencia RPA."""
    lines = [
        "REPORTE AUTOMATIZADO - RPA PYAUTOGUI",
        "=" * 46,
        f"ID Diagnostico: {diagnosis_record.get('id', 'N/A')}",
        f"Fecha: {diagnosis_record.get('date', 'N/A')}",
        "",
        "Sintomas:",
    ]

    for symptom in diagnosis_record.get("symptoms", []):
        lines.append(f"- {symptom}")

    lines.append("")
    lines.append("Condiciones sugeridas:")

    for condition in diagnosis_record.get("conditions", []):
        name = condition.get("name", "N/A")
        relevance = condition.get("relevance", "N/A")
        lines.append(f"- {name} (relevancia: {relevance})")

    lines.append("")
    lines.append("Generado automaticamente por flujo RPA en backend Python.")
    return "\n".join(lines)


def execute_diagnosis_rpa_flow(diagnosis_record):
    """
    Ejecuta el flujo RPA para un diagnostico.

    El flujo incluye:
    1) Generar reporte de texto automatizado.
    2) Capturar evidencia de pantalla con PyAutoGUI.
    """
    _ensure_output_dir()

    diagnosis_id = diagnosis_record.get("id", "sin_id")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_path = os.path.join(
        RPA_OUTPUT_DIR, f"reporte_diagnostico_{diagnosis_id}_{timestamp}.txt"
    )

    result = {
        "executed": False,
        "available": PYAUTOGUI_AVAILABLE,
        "report_path": report_path,
        "screenshot_path": None,
        "message": "",
    }

    # Paso 1: crear reporte de texto (siempre posible)
    try:
        report_text = _build_report_text(diagnosis_record)
        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(report_text)
    except Exception as exc:
        result["message"] = f"No se pudo generar el reporte RPA: {exc}"
        return result

    # Paso 2: evidencia visual con PyAutoGUI
    if not PYAUTOGUI_AVAILABLE:
        result["message"] = (
            "Reporte generado, pero PyAutoGUI no esta disponible para captura: "
            f"{PYAUTOGUI_IMPORT_ERROR or 'error de importacion.'}"
        )
        return result

    try:
        screenshot_path = os.path.join(
            RPA_OUTPUT_DIR, f"evidencia_diagnostico_{diagnosis_id}_{timestamp}.png"
        )
        screenshot = pyautogui.screenshot()  # type: ignore[name-defined]
        screenshot.save(screenshot_path)

        mouse_pos = pyautogui.position()  # type: ignore[name-defined]

        result.update(
            {
                "executed": True,
                "screenshot_path": screenshot_path,
                "message": (
                    "Flujo RPA completado: reporte y evidencia visual generados. "
                    f"Posicion mouse capturada: ({mouse_pos.x}, {mouse_pos.y})."
                ),
            }
        )
        return result
    except Exception as exc:
        result["message"] = (
            "Reporte generado, pero fallo la captura de pantalla con PyAutoGUI: "
            f"{exc}"
        )
        return result
