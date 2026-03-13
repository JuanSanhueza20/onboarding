from db import  validar_usuario_admin, crear_usuario, desactivar_usuario_db, activar_usuario_db, actualizar_todo, actualizar_contraseña, actualizar_email, obtener_usuario
import logging 
import getpass
import bcrypt
from sendMail import enviarMail
from wireguard import add_peer, generate_client_config, regenerate_config
from ad_service import enable_or_disable_user, create_ad_user, generate_join_script
import subprocess
# Configuracion del logging para guardado de logs
logging.basicConfig(filename="info.log", level=logging.INFO)




def pedir_contraseña ():
    password = getpass.getpass("Ingresa la nueva Contraseña: ").strip().encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())

    return hashed


def validar_admin () -> bool:
    username = input("Ingresa el nombre de usuario admin:  ").strip()
    email = input("Ingresa el email de usuario admin:  ").strip()
    password = getpass.getpass("Ingresa la contraseña de usuario admin:  ").strip()

    
    return validar_usuario_admin(username, password, email)



def ingresar_usuario ():
    nombre = input("Ingresa el nombre del nuevo usuario:  ").strip()
    username = input("Ingresa el nombre de usuario:  ").strip()
    email = input("Ingresa el email del nuevo usuario:  ").strip()
    hashed = pedir_contraseña()
    respuesta_user = crear_usuario(nombre, username, email, hashed)
    respuesta_peer = add_peer(username)
    respuesta_ad = create_ad_user(username, nombre, email)
    message = respuesta_user["message"]

    if not respuesta_user["created"] and not respuesta_peer and not respuesta_ad:
        logging.info(f"error: {message} --- user: {username}, {email}")
        return False
    

    return True



def enviar_archivos ():
    print("Seccion Para administracion de servicios usuarios.")

    print("""
        Opciones:
          1) Enviar archivos de Configuracion a usuario.
          2) Volver
    """)

    opcion = input("Ingrese una Opcion: ")

    if int(opcion) > 1:
        return

    username = input("Ingresa el nombre de usuario:  ").strip()
    user = obtener_usuario(username)

    if user["state"] == "disabled":
        print("El Usuario se encuentra deshabilitado")
        return
    
    wireguard_file = generate_client_config(username)
    ad_union_file = generate_join_script(username, "123456789")

    if not wireguard_file and not ad_union_file:
        print("Error al generar la configuracion del cliente -- Intenta Nuevamente")
        return
    


    email = user["email"]

    if not email:
        print("Error al obtener el email del Usuario -- Intenta Nuevamente")
        return
    
    respuesta = enviarMail(email, [wireguard_file, ad_union_file], user["nombre"])

    

    if respuesta["error"]:
        print("Error al envia el correo -- Intenta Nuevamente")
        return
    
    subprocess.run(["rm", "/tmp/clients_config/*"], check=True)
    print(f"Correo enviado para usuario {username} -- {email}")
    return

    



def desactivar_usuario(): 
    username = input("Ingresa el nombre de usuario:  ").strip()

    user = obtener_usuario(username)

    if user["state"] == "disabled":
        print("El usuario ya se encuentra desactivado")
        return

    respuesta = desactivar_usuario_db(username)
    respuesta_ad = enable_or_disable_user(username, 514)

    if not respuesta and respuesta_ad:
        print("Error al intentar desactivar el usuario")
        return
    

    print(f"Usuario {username} Desactivado.")
    regenerate_config()
    

def activar_usuario(): 
    username = input("Ingresa el nombre de usuario:  ").strip()

    user = obtener_usuario(username)
    
    if user["state"] == "active":
        print("El usuario ya se encuentra habilitado")
        return
    
    respuesta = activar_usuario_db(username)
    respuesta_ad = enable_or_disable_user(username, 512)

    if not respuesta and respuesta_ad:
        print("Error al intentar Activar el usuario")
        return

    print(f"Usuario {username} Habilitado.")
    regenerate_config()



def actualizar_usuario ():
    print("Actualizando Usuario Del Sistema")
    print("""
        Opciones:
            1) Actualizar Contraseña.
            2) Actualizar Correo.
            3) Actualizar Contraseña y Correo.
            4) Volver.
    """)

    opcion = input("Ingresa una opcion: ")

    if int(opcion) > 3:
        return
    username = input("Ingresa el nombre de usuario a actualizar: ").strip()

    user = obtener_usuario(username)

    if user["state"] == "disabled":
        print("El Usuario se encuentra deshabilitado")
        return


    if opcion == "1":
        hashed = pedir_contraseña()
        if  not actualizar_contraseña(username=username, password=hashed):
            print("Error al actualizar la contraseña")
        print("Contraseña actualizada")

    elif opcion == "2":
        email = input("Ingresa el nuevo email: ").strip()
        if  not actualizar_email(username=username, email=email):
            print("Error al actualizar el Correo")
        print("Correo actualizado")

    elif opcion == "3":
        email = input("Ingresa el nuevo email: ").strip()
        hashed = pedir_contraseña()
        if not actualizar_todo(email=email, password=hashed,username=username):
            print("Ocurrio un error al intentar actulizar el usuario")

        print(f"Usuario {username} Actualizado")


def menu ():
    print("Bienvenido Al Sistema Para Administracion de Usuarios")
    """ if not validar_admin():
            print("Usuario Admin No validado Intenta nuevamente!")
            return """
    while True:
        try: 
          
        
        

            print("""
                Opciones:
                1) Ingresar Usuario Nuevo Al Sistema.
                2) Desactivar Usuario Del Sistema.
                3) Actualizar Usuario Del Sistema.
                4) Habilitar Usuario Del Sistema.
                5) Opciones Extras (en desarrollo).
                6) Salir.
                """)
            opcion = input("Elige una Opcion:  ")

            if opcion == "1":
                if not ingresar_usuario():
                    print("Error al crear el usuario.")
                    continue
                        
                print("Usuario Creado con exito.")
                
            elif opcion == "2":
                    desactivar_usuario()
            elif opcion == "3":
                    actualizar_usuario()
            elif opcion == "4":
                    activar_usuario()
            elif opcion == "5":
                    enviar_archivos()
            elif opcion == "6":
                    print("Saliendo Del Sistema de Administracion de Usuarios....")
                    break
            else:
                    print("Opcion no valida.")
        except KeyboardInterrupt as e:
            print("Saliendo Del Sistema de Administracion de Usuarios....")
            return
        except Exception as e:
            logging.error(e)
            print("Error intenta nuevamente...")
            
            







def main ():
    menu ()


if __name__ == "__main__":
    main()



