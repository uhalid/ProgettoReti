import socket
import struct
import time
import os
import json


def checksum(data):
    """Calcola il checksum ICMP."""
    s = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        s += (data[i] << 8) + data[i + 1]
    if n:
        s += (data[-1] << 8)
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


def ping_host(host, timeout):
    """
    Invia un pacchetto ICMP ECHO_REQUEST e attende la risposta ECHO_REPLY.

    Args:
        host (str): L'indirizzo IP o il nome host da raggiungere.
        timeout (int): Timeout in secondi. Default è 2 secondi.

    Returns:
        bool: True se l'host risponde entro il timeout, False altrimenti.
    """
    try:
        dest_addr = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"Impossibile risolvere l'host: {host}")
        return False

    icmp = socket.getprotobyname("icmp")
    try:
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        if e.errno == 1:
            e.msg += " - Prova ad eseguire come amministratore."
        print(f"Errore nella creazione del socket: {e}")
        return False

    icmp_socket.settimeout(timeout)

    icmp_type = 8  # ECHO_REQUEST
    icmp_code = 0
    icmp_checksum = 0
    icmp_id = os.getpid() & 0xFFFF  # Usa il PID processo come ID
    icmp_seq = 1
    header = struct.pack('!BBHHH', icmp_type, icmp_code,
                         icmp_checksum, icmp_id, icmp_seq)

    # Aggiungo il payload 
    payload = b'A' * 41
    packet = header + payload
    icmp_checksum = checksum(packet)
    header = struct.pack('!BBHHH', icmp_type, icmp_code,
                         icmp_checksum, icmp_id, icmp_seq)
    packet = header + payload

    try:
        icmp_socket.sendto(packet, (dest_addr, 0))
    except socket.error as e:
        print(f"Errore nell'invio del pacchetto: {e}")
        return False

    try:
        packet, _ = icmp_socket.recvfrom(1024)
        icmp_header = packet[20:28]
        _type, _code, _checksum, _id, _seq = struct.unpack(
            '!BBHHH', icmp_header)
        if _type == 0 and _id == icmp_id:  # ECHO_REPLY
            return True
    except socket.timeout:
        return False
    except socket.error as e:
        print(f"Errore nella ricezione del pacchetto: {e}")
        return False
    finally:
        icmp_socket.close()

    return False


def monitor_hosts(hosts, sleep_time, timeout):
    """
    Monitora lo stato di una lista di host tramite ping e stampa il loro stato.

    Args:
        hosts: Una lista di indirizzi IP o nomi host da monitorare.
        sleep_time: Tempo di attesa tra un controllo e l'altro.
        timeout: Timeout per il ping in secondi.
    """
    while True:
        for host in hosts:
            if ping_host(host, timeout):
                print(f"{host} è online")
            else:
                print(f"{host} è offline")
        time.sleep(sleep_time)


def load_config(config_file):
    """
    Carica la configurazione dal file JSON.

    Args:
        config_file (str): Percorso del file di configurazione JSON.

    Returns:
        dict: Dizionario con i parametri di configurazione.
    """
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File di configurazione non trovato: {config_file}")
        raise
    except json.JSONDecodeError:
        print(f"Errore nel parsing del file di configurazione: {config_file}")
        raise


def read_hosts_from_file(file_path):
    """
    Legge gli host da un file.

    Args:
        file_path (str): Percorso del file contenente gli host.

    Returns:
        list: Lista degli host letti dal file.
    """
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File degli host non trovato: {file_path}")
        raise
    except Exception as e:
        print(f"Errore nella lettura del file degli host: {e}")
        raise


def read_hosts_from_console():
    """
    Legge gli host dalla console fino a quando viene fornito un input vuoto.

    Returns:
        list: Lista degli host inseriti dall'utente.
    """
    hosts = []
    while True:
        host = input("Inserisci un host (lascia vuoto per terminare): ")
        if not host:
            break
        hosts.append(host)
    return hosts


if __name__ == "__main__":
    try:
        config = load_config('config.json')

        mode = config.get('mode', 'console') # default è 'console'
        sleep_time = config.get('sleep_time', 5) # default è 5 secondi
        timeout = config.get('timeout', 2) # default è 2 secondi

        if mode == 'file':
            hosts_da_monitorare = read_hosts_from_file(config['hosts_file'])
        else:
            hosts_da_monitorare = read_hosts_from_console()

        monitor_hosts(hosts_da_monitorare,
                      sleep_time, timeout)

    except Exception as e:
        print(f"Errore critico: {e}")
