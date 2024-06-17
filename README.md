#Progetto 3


## Requisiti

- Python 3
- Privilegi amministrativi (per l'accesso ai socket raw)
- File di configurazione (`config.json`)

## Configurazione

Il file `config.json` definisce i parametri per l'utilità di monitoraggio:

- `mode` (string): Specifica la modalità di lettura degli host (`"console"` o `"file"`).
- `hosts_file` (string): Percorso del file degli host (usato se `mode` è `"file"`).
- `sleep_time` (integer): Tempo di attesa tra un controllo e l'altro (in secondi).
- `timeout` (integer): Timeout per il ping (in secondi).

Esempio di `config.json`:

```json
{
    "mode": "console",
    "hosts_file": "hosts.txt",
    "sleep_time": 5,
    "timeout": 2
}
```
## Utilizzo

- Modificare config.json per impostare i parametri desiderati
- Eseguire lo script con privilegi amministrativi:
```bash
sudo python3 main.py
```

Lo script stamperà lo stato di ciascun host a intervalli regolari.
