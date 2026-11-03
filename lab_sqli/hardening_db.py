#!/usr/bin/env python3
"""Aplica endurecimiento básico a la base de datos del laboratorio seguro."""

import argparse
from pathlib import Path

from app_segura import DB, init_db


def harden_database(db_path: str = DB, force_recreate: bool = False) -> None:
    """Recrea la BD segura con contraseñas hasheadas y verifica la estructura."""
    archivo = Path(db_path)
    if force_recreate or not archivo.exists():
        init_db(db=str(archivo), hashed=True)
        print(f"Base de datos recreada: {archivo}")
        return

    print(f"Validando base de datos existente: {archivo}")
    init_db(db=str(archivo), hashed=True)
    print("Se aplicó corrección de endurecimiento a la base de datos existente.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Endurece la base de datos del laboratorio seguro.")
    parser.add_argument("--db", default=DB, help="Ruta de la base de datos SQLite.")
    parser.add_argument("--force", action="store_true", help="Elimina y recrea la base de datos.")
    args = parser.parse_args()

    harden_database(db_path=args.db, force_recreate=args.force)


if __name__ == "__main__":
    main()
