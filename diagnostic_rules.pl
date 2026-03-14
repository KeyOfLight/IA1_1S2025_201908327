:- encoding(utf8).

% ============================================
% SISTEMA DE DIAGNÓSTICO MÉDICO EN PROLOG
% Reglas y hechos para diagnóstico preliminar
% ============================================

% ==================== SÍNTOMAS ====================
% Definición de síntomas existentes

sintoma(fiebre).
sintoma(tos).
sintoma(dolor_cabeza).
sintoma(dolor_garganta).
sintoma(congestion_nasal).
sintoma(diarrea).
sintoma(nauseas).
sintoma(fatiga).
sintoma(dolor_abdominal).
sintoma(mareos).

% ==================== CONDICIONES ====================
% Definición de condiciones médicas

condicion(gripe).
condicion(resfriado).
condicion(migrana).
condicion(faringitis).
condicion(laringitis).
condicion(amigdalitis).
condicion(gastroenteritis).
condicion(intoxicacion_alimentaria).
condicion(infeccion_parasitaria).
condicion(anemia).
condicion(depresion).
condicion(enfermedad_tiroidea).
condicion(falta_sueno).
condicion(gastritis).
condicion(apendicitis).
condicion(colicos).
condicion(ulcera).
condicion(hipertension).
condicion(hipotension).
condicion(vertigo).
condicion(covid_19).
condicion(neumonia).
condicion(bronquitis).
condicion(asma).
condicion(tension).
condicion(deshidratacion).
condicion(alergia).
condicion(sinusitis).
condicion(intoxicacion).

% ==================== CLASIFICACION DE CONDICIONES ====================
% clasificacion_condicion(Condicion, Sistema, Tipo)

clasificacion_condicion(gripe, respiratorio, infecciosa_viral).
clasificacion_condicion(resfriado, respiratorio, infecciosa_viral).
clasificacion_condicion(migrana, neurologico, neurologica).
clasificacion_condicion(faringitis, respiratorio, infecciosa_bacteriana).
clasificacion_condicion(laringitis, respiratorio, inflamatoria).
clasificacion_condicion(amigdalitis, respiratorio, infecciosa_bacteriana).
clasificacion_condicion(gastroenteritis, digestivo, infecciosa).
clasificacion_condicion(intoxicacion_alimentaria, digestivo, toxica).
clasificacion_condicion(infeccion_parasitaria, digestivo, parasitaria).
clasificacion_condicion(anemia, hematologico, cronica).
clasificacion_condicion(depresion, salud_mental, psicologica).
clasificacion_condicion(enfermedad_tiroidea, endocrino, hormonal).
clasificacion_condicion(falta_sueno, neurologico, funcional).
clasificacion_condicion(gastritis, digestivo, inflamatoria).
clasificacion_condicion(apendicitis, digestivo, quirurgica_urgente).
clasificacion_condicion(colicos, digestivo, funcional).
clasificacion_condicion(ulcera, digestivo, inflamatoria).
clasificacion_condicion(hipertension, cardiovascular, cronica).
clasificacion_condicion(hipotension, cardiovascular, hemodinamica).
clasificacion_condicion(vertigo, neurologico, vestibular).
clasificacion_condicion(covid_19, respiratorio, infecciosa_viral).
clasificacion_condicion(neumonia, respiratorio, infecciosa).
clasificacion_condicion(bronquitis, respiratorio, inflamatoria_infecciosa).
clasificacion_condicion(asma, respiratorio, cronica).
clasificacion_condicion(tension, neurologico, funcional).
clasificacion_condicion(deshidratacion, metabolico, desequilibrio_hidrico).
clasificacion_condicion(alergia, inmunologico, alergica).
clasificacion_condicion(sinusitis, respiratorio, inflamatoria_infecciosa).
clasificacion_condicion(intoxicacion, digestivo, toxica).

% Condicion inferida desde relaciones sintoma-condicion.
clasificacion_condicion(infeccion_viral, general, infecciosa_viral).

% ==================== RELACIONES SÍNTOMA-CONDICIÓN ====================
% Reglas que relacionan síntomas con condiciones

relacion(fiebre, gripe).
relacion(fiebre, infeccion_viral).
relacion(fiebre, covid_19).
relacion(fiebre, neumonia).

relacion(tos, gripe).
relacion(tos, resfriado).
relacion(tos, bronquitis).
relacion(tos, asma).

relacion(dolor_cabeza, migrana).
relacion(dolor_cabeza, tension).
relacion(dolor_cabeza, gripe).
relacion(dolor_cabeza, deshidratacion).

relacion(dolor_garganta, faringitis).
relacion(dolor_garganta, laringitis).
relacion(dolor_garganta, amigdalitis).

relacion(congestion_nasal, resfriado).
relacion(congestion_nasal, alergia).
relacion(congestion_nasal, sinusitis).

relacion(diarrea, gastroenteritis).
relacion(diarrea, intoxicacion_alimentaria).
relacion(diarrea, infeccion_parasitaria).

relacion(nauseas, gastroenteritis).
relacion(nauseas, migrana).
relacion(nauseas, intoxicacion).

relacion(fatiga, anemia).
relacion(fatiga, depresion).
relacion(fatiga, enfermedad_tiroidea).
relacion(fatiga, falta_sueno).

relacion(dolor_abdominal, gastritis).
relacion(dolor_abdominal, apendicitis).
relacion(dolor_abdominal, colicos).
relacion(dolor_abdominal, ulcera).

relacion(mareos, hipertension).
relacion(mareos, hipotension).
relacion(mareos, vertigo).
relacion(mareos, anemia).

% ==================== REGLAS DE DIAGNÓSTICO ====================

% Obtener todas las condiciones posibles para un síntoma
condiciones_por_sintoma(Sintoma, Condicion) :-
    relacion(Sintoma, Condicion).

% Diagnosticar basado en múltiples síntomas
diagnosticar(Sintomas, Diagnostico) :-
    member(S, Sintomas),
    relacion(S, Diagnostico).

% Calcular coincidencias (relevancia)
contar_coincidencias([], _, 0).
contar_coincidencias([H|T], Condicion, Count) :-
    relacion(H, Condicion),
    !,
    contar_coincidencias(T, Condicion, Count1),
    Count is Count1 + 1.
contar_coincidencias([_|T], Condicion, Count) :-
    contar_coincidencias(T, Condicion, Count).

% Encontrar diagnósticos ordenados por relevancia
diagnosticos_ordenados(Sintomas, ListaDiagnosticos) :-
    findall(Cond-Count, 
            (condicion(Cond), 
             contar_coincidencias(Sintomas, Cond, Count), 
             Count > 0),
            DiagnosticosConPuntos),
    sort(2, @>=, DiagnosticosConPuntos, ListaDiagnosticos).

% Obtener diagnósticos sin puntuación
obtener_diagnosticos(Sintomas, Diagnosticos) :-
    findall(Cond, 
            diagnosticar(Sintomas, Cond),
            Diagnosticos_temp),
    list_to_set(Diagnosticos_temp, Diagnosticos).

% ==================== INFORMACIÓN MÉDICA ====================

% Descripción de síntomas
descripcion_sintoma(fiebre, "Aumento anormal de la temperatura corporal").
descripcion_sintoma(tos, "Expulsión repentina y audible de aire por las vías respiratorias").
descripcion_sintoma(dolor_cabeza, "Sensación dolorosa en la cabeza o cuero cabelludo").
descripcion_sintoma(dolor_garganta, "Dolor, irritación o raspado en la garganta").
descripcion_sintoma(congestion_nasal, "Bloqueo de las fosas nasales, dificultad para respirar").
descripcion_sintoma(diarrea, "Evacuaciones intestinales frecuentes y sueltas").
descripcion_sintoma(nauseas, "Sensación de malestar con ganas de vomitar").
descripcion_sintoma(fatiga, "Cansancio extremo y falta de energía").
descripcion_sintoma(dolor_abdominal, "Dolor o molestia en la región abdominal").
descripcion_sintoma(mareos, "Sensación de vértigo o inestabilidad").

% Severidad de síntomas
severidad(fiebre, alta).          % Síntoma grave
severidad(tos, media).
severidad(dolor_cabeza, baja).
severidad(dolor_garganta, media).
severidad(congestion_nasal, baja).
severidad(diarrea, media).
severidad(nauseas, media).
severidad(fatiga, baja).
severidad(dolor_abdominal, alta).  % Síntoma crítico
severidad(mareos, media).

% Requiere atención inmediata
urgente(apendicitis).
urgente(intoxicacion).
urgente(covid_19).
urgente(neumonia).

% Recomendaciones médicas
recomendacion(gripe, "Descanse y manténgase hidratado. Consulte a un médico si los síntomas persisten.").
recomendacion(resfriado, "Use medicamentos de venta libre y descanse. Mejorará en 7-10 días.").
recomendacion(migrana, "Descansa en ambiente oscuro y tranquilo. Consulte a un médico para medicación.").
recomendacion(gastroenteritis, "Rehidratación es primordial. Evite alimentos sólidos inicialmente.").
recomendacion(apendicitis, "BUSQUE ATENCIÓN MÉDICA INMEDIATA - Esta condición requiere evaluación urgente.").

% ==================== CONSULTAS ÚTILES ====================

% Listar todos los síntomas disponibles
todos_sintomas(Sintomas) :-
    findall(S, sintoma(S), Sintomas).

% Listar todas las condiciones disponibles
todas_condiciones(Condiciones) :-
    findall(C, condicion(C), Condiciones).

% Obtener clasificacion por sistema/tipo para una condicion
obtener_clasificacion_condicion(Condicion, Sistema, Tipo) :-
    clasificacion_condicion(Condicion, Sistema, Tipo),
    !.
obtener_clasificacion_condicion(_, no_definido, no_definido).

% Listar condiciones por sistema
condiciones_por_sistema(Sistema, Condiciones) :-
    findall(C, clasificacion_condicion(C, Sistema, _), Lista),
    sort(Lista, Condiciones).

% Listar condiciones por tipo
condiciones_por_tipo(Tipo, Condiciones) :-
    findall(C, clasificacion_condicion(C, _, Tipo), Lista),
    sort(Lista, Condiciones).

% Listar sistemas disponibles para clasificacion
sistemas_disponibles(Sistemas) :-
    findall(S, clasificacion_condicion(_, S, _), Lista),
    sort(Lista, Sistemas).

% Listar tipos de condicion disponibles para clasificacion
tipos_condicion_disponibles(Tipos) :-
    findall(T, clasificacion_condicion(_, _, T), Lista),
    sort(Lista, Tipos).

% Verificar si una condición es urgente
es_urgente(Condicion) :-
    urgente(Condicion).

% Obtener recomendación para una condición
obtener_recomendacion(Condicion, Recomendacion) :-
    recomendacion(Condicion, Recomendacion),
    !.
obtener_recomendacion(_, "Consulte con un profesional médico para mayor información.").

% ==================== VALIDACIÓN ====================

% Validar que un síntoma existe
validar_sintoma(Sintoma) :-
    sintoma(Sintoma).

% Validar que una condición existe
validar_condicion(Condicion) :-
    condicion(Condicion).

% ==================== PONDERACIÓN POR SEVERIDAD ====================

% Peso de severidad para cálculos ponderados
peso_severidad(severo, 3).      % Síntoma severo: peso 3
peso_severidad(moderado, 2).    % Síntoma moderado: peso 2
peso_severidad(leve, 1).        % Síntoma leve: peso 1
peso_severidad('Severo', 3).    % Alternativa mayúscula
peso_severidad('Moderado', 2).
peso_severidad('Leve', 1).

% Calcular coincidencias ponderadas por severidad
contar_coincidencias_ponderadas([], _, 0).
contar_coincidencias_ponderadas([H|T], Condicion, PesoTotal) :-
    relacion(H, Condicion),
    !,
    % Aquí se incluiría el análisis de severidad si está disponible
    contar_coincidencias_ponderadas(T, Condicion, PesoResto),
    PesoTotal is PesoResto + 1.
contar_coincidencias_ponderadas([_|T], Condicion, PesoTotal) :-
    contar_coincidencias_ponderadas(T, Condicion, PesoTotal).

% Clasificar síntomas críticos (alta severidad) que requieren diagnósticos urgentes
sintomas_criticos(Sintomas, CriticosPresentes) :-
    findall(S, (member(S, Sintomas), severidad(S, alta)), CriticosPresentes).

% Aumentar relevancia de condiciones si hay síntomas críticos presentes
diagnosticos_ajustados_por_criticidad(Sintomas, Diagnosticos) :-
    findall(Cond-(Count + Bonus),
            (condicion(Cond),
             contar_coincidencias(Sintomas, Cond, Count),
             Count > 0,
             (sintomas_criticos(Sintomas, [_|_]) -> Bonus = 1 ; Bonus = 0)),
            DiagnosticosAjustados),
    sort(2, @>=, DiagnosticosAjustados, Diagnosticos).

% ==================== MEDICAMENTOS ====================
% Base de datos de medicamentos disponibles

% Definición de medicamentos por categoría
medicamento(paracetamol, analgesico_antipiretico).
medicamento(ibuprofeno, antiinflamatorio_analgesico).
medicamento(aspirina, antiinflamatorio_anticoagulante).
medicamento(amoxicilina, antibiotico_penicilina).
medicamento(azitromicina, antibiotico_macrolido).
medicamento(omeprazol, inhibidor_bomba_protones).
medicamento(ranitidina, antagonista_h2).
medicamento(metformina, antidiabetico).
medicamento(metoprolol, beta_bloqueante).
medicamento(atenolol, beta_bloqueante).
medicamento(losartan, antagonista_angiotensina_ii).
medicamento(enalapril, inhibidor_eca).
medicamento(loratadina, antihistaminico).
medicamento(fexofenadina, antihistaminico).
medicamento(salbutamol, broncodilatador).
medicamento(fluticasona, corticosteroide_inhalado).
medicamento(sertralina, inhibidor_recaptacion_serotonina).
medicamento(fluoxetina, inhibidor_recaptacion_serotonina).
medicamento(trazodona, antidepresivo_heterociclico).
medicamento(diclofenaco, aine).
medicamento(meloxicam, aine).
medicamento(acetilcisteina, mucolytico).
medicamento(carbocisteina, mucolytico).
medicamento(loperamida, antidiarreico).
medicamento(bismuto_subsalicilato, antidiarreico).
medicamento(metoclopramida, antiemetico).
medicamento(ondansetron, antagonista_5ht3).
medicamento(domperidona, antagonista_dopamina).
medicamento(trimetazidina, antianginal).
medicamento(nitroglicerina, vasodilatador).
medicamento(amlodipina, bloqueante_calcio).

% Relación: medicamento trata enfermedad
trata(paracetamol, gripe).
trata(paracetamol, resfriado).
trata(paracetamol, migrana).
trata(paracetamol, tension).
trata(ibuprofeno, gripe).
trata(ibuprofeno, migrana).
trata(ibuprofeno, tension).
trata(ibuprofeno, artritis).
trata(aspirina, migrana).
trata(aspirina, dolor_pecho).
trata(amoxicilina, faringitis).
trata(amoxicilina, laringitis).
trata(amoxicilina, amigdalitis).
trata(amoxicilina, bronquitis).
trata(azitromicina, bronquitis).
trata(azitromicina, neumonia).
trata(omeprazol, gastritis).
trata(omeprazol, ulcera).
trata(omeprazol, reflujo_gastrico).
trata(ranitidina, gastritis).
trata(ranitidina, ulcera).
trata(metformina, diabetes_tipo_2).
trata(metoprolol, hipertension).
trata(metoprolol, taquicardia).
trata(metoprolol, angina).
trata(atenolol, hipertension).
trata(atenolol, taquicardia).
trata(losartan, hipertension).
trata(enalapril, hipertension).
trata(enalapril, insuficiencia_cardiaca).
trata(loratadina, alergia).
trata(loratadina, rinitis_alergica).
trata(fexofenadina, alergia).
trata(fexofenadina, urticaria).
trata(salbutamol, asma).
trata(salbutamol, bronquitis).
trata(salbutamol, enfisema).
trata(fluticasona, asma).
trata(fluticasona, rinitis_alergica).
trata(sertralina, depresion).
trata(sertralina, ansiedad).
trata(sertralina, trastorno_panico).
trata(fluoxetina, depresion).
trata(fluoxetina, ansiedad).
trata(trazodona, depresion).
trata(trazodona, insomnio).
trata(diclofenaco, artritis).
trata(diclofenaco, dolor_musculoesqueletico).
trata(meloxicam, artritis).
trata(meloxicam, dolor_inflamatorio).
trata(acetilcisteina, bronquitis).
trata(acetilcisteina, asma).
trata(carbocisteina, bronquitis).
trata(loperamida, diarrea).
trata(loperamida, gastroenteritis).
trata(bismuto_subsalicilato, diarrea).
trata(bismuto_subsalicilato, gastroenteritis).
trata(metoclopramida, nauseas).
trata(metoclopramida, vomito).
trata(ondansetron, nauseas).
trata(ondansetron, vomito).
trata(domperidona, nauseas).
trata(domperidona, vomito).

% Información detallada de medicamentos
% tipo_medicamento(Medicamento, Tipo)
tipo_medicamento(paracetamol, 'Analgesico/Antipiretico').
tipo_medicamento(ibuprofeno, 'Antiinflamatorio (AINE)').
tipo_medicamento(aspirina, 'Antiinflamatorio (AINE)').
tipo_medicamento(amoxicilina, 'Antibiótico').
tipo_medicamento(azitromicina, 'Antibiótico').
tipo_medicamento(omeprazol, 'Inhibidor de Bomba de Protones').
tipo_medicamento(ranitidina, 'Antagonista H2').
tipo_medicamento(metformina, 'Antidiabético').
tipo_medicamento(loratadina, 'Antihistamínico').
tipo_medicamento(salbutamol, 'Broncodilatador').
tipo_medicamento(sertralina, 'Antidepresivo (ISRS)').
tipo_medicamento(fluoxetina, 'Antidepresivo (ISRS)').

% Dosis recomendadas (para adultos)
dosis_recomendada(paracetamol, '500-1000 mg cada 6-8 horas (máx 4g/día)').
dosis_recomendada(ibuprofeno, '200-400 mg cada 6-8 horas (máx 1.2g/día)').
dosis_recomendada(aspirina, '300-500 mg cada 8 horas (máx 3g/día)').
dosis_recomendada(amoxicilina, '250-500 mg cada 8 horas (depende condición)').
dosis_recomendada(azitromicina, '500 mg día 1, luego 250 mg diarios').
dosis_recomendada(omeprazol, '20-40 mg una vez diaria').
dosis_recomendada(ranitidina, '150-300 mg cada 12 horas').
dosis_recomendada(loratadina, '10 mg una vez diaria').
dosis_recomendada(fexofenadina, '180 mg una vez diaria').
dosis_recomendada(salbutamol, '100-200 mcg inhalado según sea necesario').
dosis_recomendada(sertralina, '50-200 mg una vez diaria').
dosis_recomendada(fluoxetina, '20-80 mg una vez diaria').

% Contraindicaciones por condición
% contraindicacion(Medicamento, Condicion adversa)
contraindicacion(aspirina, ulcera_activa).
contraindicacion(aspirina, insuficiencia_renal_severa).
contraindicacion(aspirina, asma).
contraindicacion(ibuprofeno, ulcera_activa).
contraindicacion(ibuprofeno, insuficiencia_renal_severa).
contraindicacion(ibuprofeno, hipertension_no_controlada).
contraindicacion(metformina, insuficiencia_renal_severa).
contraindicacion(metformina, enfermedad_hepatica).
contraindicacion(amoxicilina, alergia_penicilina).
contraindicacion(azitromicina, problemas_hepaticos).
contraindicacion(metoprolol, asma).
contraindicacion(metoprolol, bradicardia).
contraindicacion(atenolol, asma).
contraindicacion(atenolol, bradicardia).

% Efectos secundarios comunes
% efecto_secundario(Medicamento, Efecto)
efecto_secundario(paracetamol, 'Raramente: erupcion cutanea, reacciones alergicas').
efecto_secundario(ibuprofeno, 'Molestias gastricas, mareos, erupcion cutanea').
efecto_secundario(amoxicilina, 'Molestias estomacales, diarrea, alergia/erupcion').
efecto_secundario(azitromicina, 'Diarrea, náuseas, dolor abdominal').
efecto_secundario(omeprazol, 'Dolor de cabeza, diarrea, náuseas').
efecto_secundario(metformina, 'Sabor metalico, diarrea, nauseas').
efecto_secundario(sertralina, 'Insomnio, náuseas, disfunción sexual').
efecto_secundario(fluoxetina, 'Ansiedad inicial, insomnio, náuseas').
efecto_secundario(salbutamol, 'Temblor, taquicardia, dolor de cabeza').
efecto_secundario(loratadina, 'Somnolencia, sequedad bucal').
efecto_secundario(fexofenadina, 'Minimos efectos secundarios, raramente mareos').

% Consultas útiles para medicamentos

% Obtener medicamentos para una enfermedad
medicamentos_para(Enfermedad, Medicamentos) :-
    findall(Med, trata(Med, Enfermedad), Medicamentos).

% Obtener todas las enfermedades que trata un medicamento
enfermedades_tratadas_por(Medicamento, Enfermedades) :-
    findall(Enf, trata(Medicamento, Enf), Enfermedades).

% Verificar si un medicamento trata una enfermedad
trata_enfermedad(Medicamento, Enfermedad) :-
    trata(Medicamento, Enfermedad).

% Obtener información completa de un medicamento
info_medicamento(Medicamento, Tipo, Dosis, Efectos) :-
    tipo_medicamento(Medicamento, Tipo),
    dosis_recomendada(Medicamento, Dosis),
    efecto_secundario(Medicamento, Efectos).

% Verificar contraindicaciones
tiene_contraindicacion(Medicamento, Condicion) :-
    contraindicacion(Medicamento, Condicion).

% Obtener todos los medicamentos
todos_medicamentos(Medicamentos) :-
    findall(Med, medicamento(Med, _), Medicamentos).

% Medicamentos seguros (sin contraindicaciones listadas)
medicamento_seguro(Medicamento) :-
    medicamento(Medicamento, _),
    \+ contraindicacion(Medicamento, _).

% ==================== SUGERENCIAS DE TRATAMIENTO ====================
% Reglas para sugerir medicamentos basados en diagnóstico

sugerir_medicamentos(Diagnostico, MedicamentosSugeridos) :-
    findall(Med, trata(Med, Diagnostico), MedicamentosSugeridos),
    MedicamentosSugeridos \= [].

sugerir_medicamentos(_, ['Consulte con su médico para recomendación de medicamentos']) :-
    !.

% Tratamiento recomendado: información completa
tratamiento_completo(Diagnostico, ListaTratamiento) :-
    medicamentos_para(Diagnostico, Medicamentos),
    findall(med(Med, Tipo, Dosis, Efectos),
            (member(Med, Medicamentos),
             tipo_medicamento(Med, Tipo),
             dosis_recomendada(Med, Dosis),
             efecto_secundario(Med, Efectos)),
            ListaTratamiento).

% ==================== MEDICAMENTOS SEGUROS POR PERFIL DEL PACIENTE ====================

% Normalizar alergias: convertir "Penicilina" a "alergia_penicilina"
normalizar_alergia(Alergia, AlergiaProlog) :-
    atom_concat('alergia_', Alergia, AlergiaProlog).

normalizar_alergia(Alergia, AlergiaProlog) :-
    downcase_atom(Alergia, MinusculaAlergia),
    atom_string(MinusculaAlergia, StringMin),
    split_string(StringMin, " ", "", Partes),
    atomic_list_concat(Partes, '_', AlergiaSinEspacios),
    atom_concat('alergia_', AlergiaSinEspacios, AlergiaProlog).

% Normalizar enfermedades crónicas: convertir "Hipertensión" a "hipertension"
normalizar_enfermedad(Enfermedad, EnfermedadProlog) :-
    downcase_atom(Enfermedad, EnfermedadProlog), !.

normalizar_enfermedad(Enfermedad, EnfermedadProlog) :-
    atom_string(Enfermedad, _),
    downcase_atom(Enfermedad, MinusculaEnfermedad),
    atom_string(MinusculaEnfermedad, StringMin),
    split_string(StringMin, " ", "", Partes),
    atomic_list_concat(Partes, '_', EnfermedadProlog).

% Verificar si un medicamento está contraindicado para un paciente
medicamento_contraindicado(Medicamento, Alergias, EnfermedadesCronicas) :-
    (   member(A, Alergias),
        normalizar_alergia(A, AlergiaProlog),
        contraindicacion(Medicamento, AlergiaProlog)
    ;   member(E, EnfermedadesCronicas),
        normalizar_enfermedad(E, EnfermedadProlog),
        contraindicacion(Medicamento, EnfermedadProlog)
    ).

% Medicamentos seguros para un diagnóstico y perfil de paciente
medicamentos_seguros_para_paciente(Diagnostico, Alergias, EnfermedadesCronicas, MedicamentosSeguros) :-
    medicamentos_para(Diagnostico, TodosMedicamentos),
    findall(Med,
            (member(Med, TodosMedicamentos),
             \+ medicamento_contraindicado(Med, Alergias, EnfermedadesCronicas)),
            MedicamentosSeguros).

% Medicamentos bloqueados con motivo para un diagnóstico y perfil de paciente
medicamentos_bloqueados_para_paciente(Diagnostico, Alergias, EnfermedadesCronicas, MedicamentosBloqueados) :-
    medicamentos_para(Diagnostico, TodosMedicamentos),
    findall(med_bloqueado(Med, Motivo),
            (member(Med, TodosMedicamentos),
             medicamento_bloqueado_con_motivo(Med, Alergias, EnfermedadesCronicas, Motivo)),
            MedicamentosBloqueados).

% Determinar motivo de bloqueo (alergia o enfermedad crónica)
medicamento_bloqueado_con_motivo(Medicamento, Alergias, _, motivo(alergia, Alergia)) :-
    member(A, Alergias),
    normalizar_alergia(A, AlergiaProlog),
    contraindicacion(Medicamento, AlergiaProlog),
    Alergia = A, !.

medicamento_bloqueado_con_motivo(Medicamento, _, EnfermedadesCronicas, motivo(enfermedad_cronica, Enfermedad)) :-
    member(E, EnfermedadesCronicas),
    normalizar_enfermedad(E, EnfermedadProlog),
    contraindicacion(Medicamento, EnfermedadProlog),
    Enfermedad = E.

