import yagmail
from dotenv import load_dotenv
import os
from logging import getLogger

logger = getLogger(__name__)

load_dotenv()

APP_PASS = os.getenv("APP_PASS_GMAIL")



servicio_yag = yagmail.SMTP("integracion2jb@gmail.com",APP_PASS)


def enviarMail(email: str, archivos: list[str], nombre: str ):
    if len(email) < 9 or not email.endswith("@gmail.com"):
        return {"message": "Error!, correo no enviado por errores de formato", "error": True}
    
    
    body = f"""
    <h2>Bienvenido {nombre}</h2>
    <p>Aqui se encuentran los archivos para poder ingresar a los servicios</p>

    <ul>
    <li>El archivo .conf es usado en wireguard para acceder a la red interna </li>
    <li>El archivo .ps1 es usado para unirse al dominio una vez activa la conexion VPN </li>
    </ul>

    <a href="https://www.tp-link.com/es/support/faq/3989/">Informacion wireguard cliente</a>
    """

    try:
        servicio_yag.send(
        to = email,
        subject = "Bienvenido a la empresa -- Envio de Archivos de Acceso" ,
        contents = body,
        attachments=archivos
        )

        return {"message": "Correo Enviado", "error": False}
    except Exception as e:
        logger.error(f"Error en correo: {e}")
        return {"message": "Error!, correo no enviado por errores de formato", "error": True}


