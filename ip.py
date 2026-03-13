import ipaddress
from dotenv import load_dotenv
import os
from db import obtener_ips

load_dotenv()

def obtener_ip_siguiente():
    network = ipaddress.IPv4Network(os.getenv("VPN_NETWORK"))
    used_ips_db = obtener_ips()
    
    # obtener_ips retorna una lista de diccionarios, extraemos la IP en formato texto
    used_ips = [str(row["ip"]).split('/')[0] for row in used_ips_db]

    for ip in network.hosts():
        ip_str = str(ip)
        ultimo_octeto = int(ip_str.split('.')[-1])

        # El rango disponible para asignar es desde .10 a .254
        # Esto automáticamente excluye la .1 (servidor) y cualquier otra menor a .10
        if 10 <= ultimo_octeto <= 254:
            if ip_str not in used_ips:
                return {"ip": ip_str, "error": False}

    return {"message": "No hay IPs disponibles", "error": True}







