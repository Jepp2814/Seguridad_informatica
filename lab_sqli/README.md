# Laboratorio SQL Injection

Este proyecto muestra dos versiones de una aplicación web simple con SQLite:

- una versión intencionalmente vulnerable a SQL Injection,
- una versión segura con consultas parametrizadas y hashes de contraseñas.

## Estructura

- `app_vulnerable.py`: aplicación vulnerable para demostración.
- `app_segura.py`: aplicación protegida con medidas básicas de seguridad.
- `ataque_sql_i.py`: script para probar inyección SQL mediante login y búsqueda.
- `escaneo_red.py`: escaneo básico de puertos locales.
- `hardening_db.py`: recreación y endurecimiento de la base de datos segura.
- `requirements.txt`: dependencias necesarias.

## Objetivo educativo

El laboratorio permite:

1. comprender cómo funciona una inyección SQL,
2. observar la diferencia entre consultas concatenadas y parametrizadas,
3. practicar mitigaciones básicas como:
   - consultas preparadas,
   - validación de entrada,
   - hashing de contraseñas,
   - límites de longitud,
   - separación clara entre entorno vulnerable y seguro.

## Ejecución rápida

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar la app vulnerable

```bash
python app_vulnerable.py
```

La app queda en `http://127.0.0.1:5000`.

### 3. Ejecutar la app segura

```bash
python app_segura.py
```

La app queda en `http://127.0.0.1:5001`.

### 4. Probar SQL injection

```bash
python ataque_sql_i.py --url http://127.0.0.1:5000
```

## Resultados esperados

- En la app vulnerable, los payloads maliciosos pueden evadir el login y exponer datos.
- En la app segura, los mismos intentos deben rechazarse.
- El script `ataque_sql_i.py` genera un CSV en la carpeta `resultados/` con los resultados.

## Recomendación

Este laboratorio debe usarse exclusivamente en un entorno local y controlado, con fines académicos y de aprendizaje.
