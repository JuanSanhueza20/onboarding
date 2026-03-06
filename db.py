import psycopg2
from psycopg2.extensions import connection as Connection
from psycopg2.extensions import cursor as Cursor
from logging import getLogger
from psycopg2.extras import RealDictCursor
from psycopg2 import errors


logger = getLogger(__name__)




def crear_conexion():
    conexion: Connection = psycopg2.connect(
    host = "192.168.2.15",
    dbname= "ad_users",
    user="api_user",    
    password="Juanito#2005"
    )
    cursor: Cursor = conexion.cursor(cursor_factory=RealDictCursor)

    return conexion, cursor





def terminar_conexion(conexion: Connection, cursor: Cursor):
    
    conexion.commit()
    cursor.close()
    conexion.close()
    


def validar_usuario_admin(username: str, password: str, email: str) -> bool:
    conexion, cursor = crear_conexion()

    
    cursor.execute("""
        SELECT username, password, email FROM users WHERE username = %s
    """, (username, ))

    admin = cursor.fetchone()


    if not admin:
        return False
    
    terminar_conexion(conexion, cursor)

    logger.info(f"comprobacion de contraseña: {admin['password'] == password}")
    return admin["password"] == password and admin["email"] == email

    



def crear_usuario(nombre: str, username: str, email: str, password: str):
    conexion, cursor = crear_conexion()

    try:
        cursor.execute("""
        INSERT INTO users (nombre, username, email, password, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, username, email, password, 'user', ))


        terminar_conexion(conexion, cursor) 
        return {"message": "Usuario Creado", "created": True}       
    except errors.UniqueViolation:
        terminar_conexion(conexion, cursor) 
        return {"message": "Error al crear el usuario, Violacion de politica de interna", "created": False}
    




def obtener_usuario(username: str):
    conexion, cursor = crear_conexion()

    try:
        cursor.execute("""
            SELECT * FROM users WHERE username = %s
        """, (username,))

        

        user = cursor.fetchone()
        terminar_conexion(conexion, cursor)
        return user
    except Exception as e:
        terminar_conexion(conexion, cursor)
        return False
       
    




def desactivar_usuario_db(username:str):
    conexion, cursor = crear_conexion()

    try:
        cursor.execute("""
            UPDATE users SET state = 'disabled'
            WHERE username = %s
        """, (username,))

        cursor.execute("""
            UPDATE wireguard_peers 
            SET active = FALSE
            WHERE username = %s
        """, (username,))
        terminar_conexion(conexion, cursor)
        return True

    except:
        terminar_conexion(conexion, cursor)
    
    



def activar_usuario_db(username:str):
    conexion, cursor = crear_conexion()

    try:
        cursor.execute("""
            UPDATE users 
            SET state = 'active'
            WHERE username = %s
        """, (username,))

        cursor.execute("""
            UPDATE wireguard_peers 
            SET active = TRUE
            WHERE username = %s
        """, (username,))
        terminar_conexion(conexion, cursor)
        return True
    except:
        terminar_conexion(conexion, cursor)
    
    




def actualizar_todo(username: str, email: str = None, password: str = None):
    conexion, cursor = crear_conexion()

    try:
        cursor.execute("""
            UPDATE users 
            SET email = %s, password = %s
            WHERE username = %s
        """, (email, password, username, ))

    except:
        terminar_conexion(conexion, cursor)
    
    terminar_conexion(conexion, cursor)
    return True




def actualizar_contraseña (username: str, password: str):
    conexion, cursor = crear_conexion()

    try:
        cursor.execute("""
            UPDATE users 
            SET password = %s
            WHERE username = %s
        """, (password, username, ))

    except:
        terminar_conexion(conexion, cursor)
        return False
    
    terminar_conexion(conexion, cursor)
    return True


def actualizar_email (username: str, email: str):
    conexion, cursor = crear_conexion()
    try:
        cursor.execute("""
            UPDATE users 
            SET email = %s
            WHERE username = %s
        """, (email, username, ))

    except:
        terminar_conexion(conexion, cursor)
        return False
    
    terminar_conexion(conexion, cursor)
    return True




def regenerate_config_from_db():
    conexion, cursor = crear_conexion()
    
    cursor.execute("""
        SELECT public_key, ip
        FROM wireguard_peers
        WHERE active = TRUE
    """)

    peers = cursor.fetchall()

    terminar_conexion(conexion, cursor)
    return peers

    


def insertar_peer (username: str, public_key: str, private_key: str, ip: str) -> bool:
    conexion, cursor = crear_conexion()
    try:

        cursor.execute("""
            INSERT INTO wireguard_peers
            (username, public_key, private_key, ip) VALUES (%s, %s, %s , %s)
        """, (username, public_key, private_key, ip, ) )
        terminar_conexion(conexion, cursor)
        return True
    except errors.UniqueViolation as e:
        terminar_conexion(conexion, cursor)
        return False




def obtener_peer (username: str):
    conexion, cursor = crear_conexion()
    cursor.execute("""
            SELECT private_key, ip from wireguard_peers
            WHERE username = %s
        """, (username, ) )
    
    user = cursor.fetchone()
    terminar_conexion(conexion, cursor)

    return user



def obtener_ips():
    conexion, cursor = crear_conexion()

    cursor.execute("""
        SELECT ip
        FROM wireguard_peers
    """)

    ips = cursor.fetchall()
    terminar_conexion(conexion, cursor)
    return ips






def obtener_usuarios(state: str = "all"):
    '''
    state: str = all -> return all users (default) \n
    state: str = active -> return active users \n
    state: str = disabled -> return disabled users
    '''
    conexion, cursor = crear_conexion()
    base_query = "SELECT * FROM users WHERE 1=1"
    params = []

    if state in ("active", "disabled"):
        base_query += " AND state = %s"
        params.append(state)

    
    base_query += " AND role = 'user'"
    cursor.execute(base_query, params)
    users = cursor.fetchall()
    terminar_conexion(conexion, cursor)
    return users

