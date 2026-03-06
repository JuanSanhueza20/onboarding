import os
import subprocess
from dotenv import load_dotenv
from db import regenerate_config_from_db, insertar_peer, obtener_peer
from ip import obtener_ip_siguiente
from logging import getLogger
import textwrap

logger = getLogger(__name__)
load_dotenv()




WG_DIR = "/home/adUser/onboarding"
PEERS_DIR = os.path.join(WG_DIR, "peers")
BASE_CONFIG = os.path.join(WG_DIR, "wg0_base.conf")
FINAL_CONFIG = os.path.join(WG_DIR, "wg0.conf")
INTERFACE = "wg0"

SERVER_PUBLIC_KEY = os.getenv("SERVER_PUBLIC_KEY")
ENDPOINT = os.getenv("ENDPOINT")
VPN_NETWORK = os.getenv("VPN_NETWORK")
DNS_SERVER = os.getenv("SERVER_AD_IP")

def generate_keys():
    private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public_key = subprocess.check_output(
        ["wg", "pubkey"], input=private_key.encode()
    ).decode().strip()
    return private_key, public_key



def regenerate_config():

    peers = regenerate_config_from_db()

    logger.info(f"Peers: {peers}")

    with open(BASE_CONFIG) as f:
        config = f.read()

    peer_configs = []
    for peer in peers:  # peer es RealDictRow (dict-like)
        public_key = peer['public_key']
        ip = peer['ip']
        peer_configs.append(textwrap.dedent(f"""
        \n
        [Peer]
        PublicKey = {public_key}
        AllowedIPs = {ip}/32
    """).strip())


    config += "\n".join(peer_configs) + "\n"

    with open(f"{WG_DIR}/onboarding/wg_build/wg0.conf", "w") as f:
        f.write(config.rstrip())

    subprocess.run(["sudo", "/usr/local/bin/wg_manager.sh"], check=True)


def add_peer(username: str):
    private_key, public_key = generate_keys()

    logger.info(f"Keys: privada = {private_key}, publica = {public_key}")
    
    allowed_ip = obtener_ip_siguiente()


    if allowed_ip["error"]:
        return False
    
    ip = f"{allowed_ip['ip']}/32"

    
    resultado = insertar_peer(username, public_key, private_key ,ip)

    logger.info(f"Resultado insertar peer: {resultado}")

    if not resultado:
        return False

    regenerate_config()


    with open(f"{WG_DIR}/control_ip.txt", "a") as f:
        f.write(f"{username} --- {ip} \n ")

    return True




def generate_client_config(username: str):

    user = obtener_peer(username)

    if not user:
        return False
    
    private_key = user["private_key"]
    ip = user["ip"]



    client_config = f"""[Interface]
    PrivateKey = {private_key}
    Address = {ip}/32
    DNS = {DNS_SERVER}

    [Peer]
    PublicKey = {SERVER_PUBLIC_KEY}
    Endpoint = {ENDPOINT}
    AllowedIPs = {VPN_NETWORK}
    PersistentKeepalive = 25
    """

    file_path = f"/var/clients_config/{username}.conf"

    with open(file_path, "w") as f:
        f.write(client_config)

    return file_path
