#!/usr/bin/env python3
"""Ajusta el suricata.yaml provisto por el paquete para el laboratorio TP5.

No reemplazamos el archivo completo (seria frágil entre versiones de Suricata):
solo parcheamos las claves que necesita el laboratorio y avisamos si alguna
no aparece, para que el build no falle silenciosamente.
"""

import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "/etc/suricata/suricata.yaml"
with open(path, encoding="utf-8") as fh:
    text = fh.read()


def replace_line(pattern: str, replacement: str, label: str) -> None:
    global text
    text, n = re.subn(pattern, replacement, text, count=1)
    if n == 0:
        print(f"WARNING: no se encontro {label}; se conserva el valor por defecto")
    else:
        print(f"OK: {label}")


replace_line(r"(?m)^(\s*HOME_NET:\s*).*$", r'\1"[10.0.0.0/24]"', "HOME_NET")
replace_line(r"(?m)^(\s*EXTERNAL_NET:\s*).*$", r'\1"!$HOME_NET"', "EXTERNAL_NET")
replace_line(
    r"(?m)^(\s*checksum-validation:\s*)(yes|true)",
    r"\1no",
    "checksum-validation (necesario con veth de Docker)",
)
replace_line(
    r"(?m)^(\s*default-rule-path:\s*).*$",
    r"\1/var/lib/suricata/rules",
    "default-rule-path",
)

text, n = re.subn(
    r"(?m)^(\s*)- suricata\.rules\s*$",
    r"\1- suricata.rules\n\1- local.rules",
    text,
    count=1,
)
print("OK: local.rules agregado" if n else "WARNING: local.rules no se agrego")

with open(path, "w", encoding="utf-8") as fh:
    fh.write(text)
print(f"suricata.yaml configurado: {path}")
