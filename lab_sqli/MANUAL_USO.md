# Manual de uso del laboratorio SQLi

## 1. Preparación

Desde la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

Si deseas verificar la versión de Python y que las dependencias estén disponibles:

```bash
python --version
python -m pip list
```

## 2. Ejecutar la aplicación vulnerable

```bash
python app_vulnerable.py
```

Abre en el navegador:

- `http://127.0.0.1:5000`

Prueba lo siguiente:

- Login válido: `admin` / `admin123`
- Login con payload: `admin' --` / `x`
- Búsqueda con: `' OR 1=1 --`

## 3. Ejecutar la aplicación segura

```bash
python app_segura.py
```

Abre en el navegador:

- `http://127.0.0.1:5001`

Prueba los mismos ataques para comprobar que la aplicación rechaza entradas peligrosas.

## 4. Ejecutar pruebas automatizadas

```bash
python ataque_sql_i.py --url http://127.0.0.1:5000
python ataque_sql_i.py --url http://127.0.0.1:5001
```

El script genera un archivo CSV en la carpeta `resultados/` con los resultados de la prueba.

## 5. Escaneo de puertos locales

```bash
python escaneo_red.py --host 127.0.0.1 --inicio 1 --fin 1024
```

Esto permite verificar si existen servicios abiertos en el entorno local.

## 6. Endurecimiento de la base de datos

```bash
python hardening_db.py --force
```

Este script recrea la base de datos segura con contraseñas hasheadas.

## 7. Detecciones esperadas

- En `app_vulnerable.py`, los payloads maliciosos pueden funcionar.
- En `app_segura.py`, los intentos se rechazan o devuelven credenciales inválidas.
- En `ataque_sql_i.py`, se registran resultados en CSV para documentar la evidencia.

## 8. Consideraciones de seguridad

Este laboratorio debe ejecutarse únicamente en un entorno de pruebas local y aislado. No debe usarse contra sistemas reales o sin autorización.
## EVELYN ASIPUELA 
