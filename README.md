# TP5 — Firewall, IDS y Honeypot (laboratorio Docker)

Entorno reproducible de la Unidad 5 (ARyS · IF046): simula tres máquinas en una
red bridge aislada `10.0.0.0/24` con IPs estáticas.

| Contenedor | IP | Contenido |
|---|---|---|
| `servidor` | `10.0.0.10` | nftables, `python3 -m http.server`, Suricata + reglas ET Open, SSH |
| `honeypot` | `10.0.0.20` | `cowrie/cowrie` (SSH en el puerto 22 dentro del contenedor) |
| `atacante` | `10.0.0.30` | nmap, curl, sshpass, openssh-client |

## Requisitos

- Docker Engine / Docker Desktop con la integración WSL activada (si estás en WSL 2).
- Jupyter Notebook o JupyterLab **en el host**, con `nbconvert`, `nbformat` e `ipykernel`.
- El CLI `docker` debe estar en el `PATH` del host, porque el notebook ejecuta
  `docker exec`.

Verificá rápido:

```bash
docker --version
docker compose version
python3 -m pip install notebook nbconvert ipykernel
```

Si la subnet `10.0.0.0/24` ya está en uso en tu máquina (`ip route | grep 10.0.0.`),
cambiá el `subnet` en `docker-compose.yml` y actualizá las IPs en el notebook.

## Arranque

```bash
cd tp5rys
docker compose up -d --build
docker compose ps
```

El build de `servidor` ejecuta `suricata-update` para congelar las reglas ET Open
dentro de la imagen. Si no hay red durante el build, el build no falla: se usa
`suricata/local.rules` (reglas de detección de SYN scan) como respaldo.

## Ejecutar el laboratorio

```bash
jupyter notebook TP5_Laboratorio.ipynb
```

Ejecutá las celdas en orden. Cada celda de código lanza comandos `docker exec`
contra los contenedores y deja la salida real impresa. Las consignas teóricas
están respondidas en celdas Markdown.

Para **grabar las salidas reales dentro del `.ipynb`**:

```bash
jupyter nbconvert --to notebook --execute --inplace TP5_Laboratorio.ipynb
```

Para generar el PDF final con el nombre que pide la cátedra:

```bash
jupyter nbconvert --to pdf TP5_Laboratorio.ipynb --output TP5_ApellidoNombre.pdf
# si no tenés LaTeX instalado:
jupyter nbconvert --to html TP5_Laboratorio.ipynb --output TP5_ApellidoNombre.html
```

## Detalle de las partes

- **A:** cadena `input` con `policy drop` + `ct state established,related accept`,
  `iif lo accept` y `tcp dport 22 accept`. Prueba: `nmap -p 22,8080 10.0.0.10`
  desde el atacante (8080 = *filtered*).
- **B:** DNAT del puerto 80 al 8000 interno. Se agregó
  `tcp dport 8000 ct original proto-dst 80 accept` para que el paquete DNATeado
  pueda pasar por la cadena `input` sin abrir el 8000 directo (esto último es un
  ajuste necesario respecto del enunciado; está explicado en el notebook).
- **C:** Suricata en modo IDS sobre `eth0`, `nmap -sS -sV` desde el atacante y
  lectura de `fast.log` / `eve.json`.
- **D:** login SSH contra Cowrie con `sshpass` y lectura de
  `/cowrie/cowrie-git/var/log/cowrie/cowrie.json`. Cowrie 3.x usa `jsonlog` como
  output por defecto (no genera el `cowrie.log` de versiones anteriores) y su
  imagen es distroless, así que el log se lee con el Python del contenedor.

## Apagado y limpieza

```bash
docker compose down
# si ademas querés borrar la red y las imágenes construidas:
docker compose down --rmi local
```

## Nota sobre el alcance

`nftables` y Suricata corren dentro del network namespace de los contenedores:
reproducen fielmente un **firewall de host** y un **NIDS de endpoint**, no un
firewall perimetral de toda la bridge. Para simular un gateway con DNAT hacia
una DMZ real haría falta un cuarto contenedor con dos interfaces; se menciona
en el apéndice del notebook.
