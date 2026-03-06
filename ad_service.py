from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, Tls
import os
import ssl
from dotenv import load_dotenv
from logging import getLogger


logger = getLogger(__name__)

load_dotenv()

PASS_AD: str = os.getenv("PASS_AD")
SERVER_AD_IP: str = os.getenv("SERVER_AD_IP")
DOMAIN = "AD_SERVICE"
USERNAME = "Administrator"
BASE_DN = "DC=ad_service,DC=local"
USERS_OU = "OU=Empleados,DC=ad_service,DC=local"

tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)




def get_ldap_connection():
    server = Server(host=SERVER_AD_IP, use_ssl=True, tls=tls_config, get_info=ALL)

    conn = Connection(
        server,
        user=f"{DOMAIN}\\{USERNAME}",
        password=PASS_AD,
        auto_bind=True
    )

    return conn


def create_ad_user(username: str,  nombre: str, email: str):

    conn = get_ldap_connection()

    password = f"AD_{username[::-1]}.rt!!d"

    print(password)

    object_class = ["top", "person", "organizationalPerson", "user"]

    user_dn = f"CN={nombre},{USERS_OU}"
    
    # Establecer contraseña (requiere formato UTF-16-LE y comillas)
    password_value = f'"{password}"'.encode("utf-16-le")


    print("Password_value encode", password_value)

    attributes = {
        "sAMAccountName": username,
        "userPrincipalName": f"{username}@ad_service.local",
        'mail': email,
        "displayName": nombre,
        'unicodePwd': password_value,
        "givenName": nombre,
        "userAccountControl": 512
    }

    
    conn.add(dn=user_dn,object_class=object_class ,attributes=attributes)

    if not conn.result["description"] == "success":
        logger.error(conn.result)
        return False
    
    conn.modify(user_dn, {'pwdLastSet': [(MODIFY_REPLACE, [0])]})
    conn.unbind()
    return True





def enable_or_disable_user(username: str, userAccountControl: int):
    """
    userAccountControl :
      512 -> enable user account
      514 -> disable user account
    """

    if userAccountControl not in [512, 514]:
        return False
    
    print(userAccountControl)
    conn = get_ldap_connection()

    conn.search(
        BASE_DN,
        f"(sAMAccountName={username})",
        attributes=["distinguishedName"]
    )

    if not conn.entries:
        return False

    user_dn = conn.entries[0].distinguishedName.value

    conn.modify(user_dn, {
        "userAccountControl": [(2, [userAccountControl])]
    })

    conn.unbind()
    return True



def generate_join_script(username: str):
    password = f"AD_{username[::-1]}.rt!!d"

    script = f"""
    Add-Computer -DomainName "ad_service.local" `
    -Credential (New-Object System.Management.Automation.PSCredential(
    "AD_SERVICE\\{username}",
    (ConvertTo-SecureString "{password}" -AsPlainText -Force)
    )) `
    -Restart
    """

    file_path = f"/var/clients_config/{username}.ps1.txt"

    with open(file_path, "w") as f:
        f.write(script)

    return file_path


