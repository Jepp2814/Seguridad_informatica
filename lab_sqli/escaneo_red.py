#!/usr/bin/env python3
"""Escaneo mínimo de puertos para el laboratorio local de SQLi."""

import argparse
import socket
from typing import List, Tuple


def escanear_puerto(host: str, puerto: int, timeout: float = 0.5) -> bool:
    """Devuelve True si un puerto responde en el host indicado."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        resultado = sock.connect_ex((host, puerto))
        return resultado == 0
    except OSError:
        return False
    finally:
        sock.close()


def escanear_rango(host: str, inicio: int, fin: int, timeout: float = 0.5) -> List[Tuple[int, str]]:
    """Escanea un rango de puertos y devuelve los abiertos."""
    abiertos = []
    for puerto in range(inicio, fin + 1):
        if escanear_puerto(host, puerto, timeout=timeout):
            abiertos.append((puerto, "abierto"))
    return abiertos


def main() -> None:
    parser = argparse.ArgumentParser(description="Escanea puertos locales del laboratorio.")
    parser.add_argument("--host", default="127.0.0.1", help="Host a escanear.")
    parser.add_argument("--inicio", type=int, default=1, help="Puerto inicial del rango.")
    parser.add_argument("--fin", type=int, default=1024, help="Puerto final del rango.")
    parser.add_argument("--timeout", type=float, default=0.5, help="Timeout por conexión.")
    args = parser.parse_args()

    print(f"Escaneando {args.host} desde el puerto {args.inicio} hasta {args.fin}")
    abiertos = escanear_rango(args.host, args.inicio, args.fin, timeout=args.timeout)

    if not abiertos:
        print("No se detectaron puertos abiertos en ese rango.")
        return

    for puerto, estado in abiertos:
        print(f"Puerto {puerto}: {estado}")


if __name__ == "__main__":
    main()
