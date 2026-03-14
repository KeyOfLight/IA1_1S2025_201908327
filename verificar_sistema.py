#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VERIFICACIÓN FINAL - Sistema MediLogic
Script para validar que todo está listo para la presentación
"""

import os
import sys
from pathlib import Path


def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE ARCHIVOS")
    print("="*70)
    
    archivos_requeridos = {
        "diagnostic_rules.pl": "Base de conocimiento Prolog",
        "prolog_engine.py": "Motor de conexión Prolog",
        "database.py": "Base de datos e integración",
        "patient_module.py": "Módulo de pacientes",
        "admin_module.py": "Módulo administrativo",
        "Main.py": "Pantalla principal",
        "demo_consultas_prolog.py": "Demostración de consultas"
    }
    
    archivos_validos = 0
    for archivo, descripcion in archivos_requeridos.items():
        existe = os.path.exists(archivo)
        estado = "✓" if existe else "✗"
        print(f"{estado} {archivo:<30} ({descripcion})")
        if existe:
            archivos_validos += 1
    
    print(f"\n→ Archivos: {archivos_validos}/{len(archivos_requeridos)}")
    return archivos_validos == len(archivos_requeridos)


def verificar_documentacion():
    """Verifica que toda la documentación esté presente"""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE DOCUMENTACIÓN")
    print("="*70)
    
    docs = {
        "INTEGRACION_PROLOG.md": "Documentación técnica",
        "PROLOG_SETUP.md": "Guía de instalación",
        "GUIA_PRESENTACION_PDF.md": "Guía para PDF",
        "RESUMEN_PROLOG.txt": "Resumen de integración",
        "CHECKLIST_PRESENTACION.txt": "Checklist final"
    }
    
    docs_validos = 0
    for archivo, descripcion in docs.items():
        existe = os.path.exists(archivo)
        estado = "✓" if existe else "✗"
        print(f"{estado} {archivo:<35} ({descripcion})")
        if existe:
            docs_validos += 1
    
    print(f"\n→ Documentación: {docs_validos}/{len(docs)}")
    return docs_validos == len(docs)


def verificar_prolog():
    """Verifica que Prolog esté instalado"""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE PROLOG")
    print("="*70)
    
    try:
        from pyswip import Prolog
        print("✓ pyswip instalado")
        
        try:
            prolog = Prolog()
            print("✓ Motor Prolog inicializado")
            return True
        except Exception as e:
            print(f"✗ Error al inicializar Prolog: {e}")
            print("  → Instala SWI-Prolog desde https://www.swi-prolog.org/")
            return False
            
    except ImportError:
        print("✗ pyswip no instalado")
        print("  → Ejecuta: pip install pyswip")
        return False


def verificar_reglas_prolog():
    """Verifica que las reglas Prolog sean válidas"""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE REGLAS PROLOG")
    print("="*70)
    
    try:
        from prolog_engine import get_prolog_engine
        
        print("Cargando motor Prolog...")
        engine = get_prolog_engine()
        print("✓ Motor Prolog cargado")
        
        # Prueba 1: Síntomas
        print("\nPrueba 1: Obtener síntomas...")
        sintomas = engine.obtener_sintomas()
        print(f"✓ Síntomas: {len(sintomas)} encontrados")
        
        # Prueba 2: Diagnóstico simple
        print("\nPrueba 2: Diagnóstico simple...")
        diags = engine.obtener_diagnosticos(["Fiebre"])
        print(f"✓ Diagnósticos: {len(diags)} encontrados para 'Fiebre'")
        
        # Prueba 3: Urgencia
        print("\nPrueba 3: Verificar urgencia...")
        urgente = engine.es_urgente("Apendicitis")
        print(f"✓ Apendicitis urgente: {urgente}")
        
        # Prueba 4: Recomendación
        print("\nPrueba 4: Obtener recomendación...")
        recom = engine.obtener_recomendacion("Gripe")
        print(f"✓ Recomendación obtenida: {recom[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def verificar_interfaz():
    """Verifica que la interfaz gráfica sea importable"""
    print("\n" + "="*70)
    print("VERIFICACIÓN DE INTERFAZ GRÁFICA")
    print("="*70)
    
    try:
        print("Importando módulo principal...")
        from Main import MainScreen
        print("✓ Main.py importable")
        
        print("Importando módulo de pacientes...")
        from patient_module import PatientDiagnosticModule
        print("✓ patient_module.py importable")
        
        print("Importando módulo administrativo...")
        from admin_module import AdminModule
        print("✓ admin_module.py importable")
        
        print("Importando base de datos...")
        from database import obtener_sintomas, obtener_diagnostico_prolog
        print("✓ database.py importable")
        
        return True
        
    except ImportError as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Ejecuta todas las verificaciones"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + " VERIFICACIÓN FINAL - SISTEMA MEDILOGIC ".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    resultados = {
        "Archivos": verificar_archivos(),
        "Documentación": verificar_documentacion(),
        "Prolog": verificar_prolog(),
        "Reglas Prolog": verificar_reglas_prolog(),
        "Interfaz": verificar_interfaz()
    }
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*70)
    
    print("\nResultados:")
    for component, valido in resultados.items():
        estado = "✓ LISTO" if valido else "✗ PROBLEMA"
        print(f"  {component:<20} {estado}")
    
    exitosos = sum(1 for v in resultados.values() if v)
    total = len(resultados)
    
    print(f"\n→ Estado general: {exitosos}/{total} componentes listos")
    
    if exitosos == total:
        print("\n" + "🎉 "*15)
        print("\n✓ ¡SISTEMA COMPLETAMENTE LISTO PARA PRESENTACIÓN!")
        print("\nPróximos pasos:")
        print("  1. Hacer commits en GitHub (5+)")
        print("  2. Capturar pantallas de ejecución")
        print("  3. Ejecutar: python demo_consultas_prolog.py")
        print("  4. Generar PDF con estructura en GUIA_PRESENTACION_PDF.md")
        print("\nTiempo estimado: 2-3 horas")
        print("\n" + "🎉 "*15)
        return 0
    else:
        print("\n⚠️  ATENCIÓN: Faltan componentes")
        print("\nComponentes con problemas:")
        for component, valido in resultados.items():
            if not valido:
                print(f"  - {component}")
        print("\nRevisa los pasos anteriores para solucionar.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
