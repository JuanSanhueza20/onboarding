# 🏢 Laboratorio: Infraestructura Empresarial con Active Directory + VPN WireGuard en AWS

## 📌 Descripción

Este laboratorio implementa una arquitectura corporativa simulada en AWS que permite el acceso remoto seguro a recursos internos mediante VPN, con autenticación centralizada en Active Directory y gestión automatizada de usuarios.

El objetivo es reproducir un entorno empresarial donde los empleados trabajan de forma remota y deben conectarse a la red corporativa para acceder a servicios internos.

---

## 🧠 Arquitectura General

La infraestructura se despliega en una VPC privada utilizando Terraform e incluye:

- Controlador de Dominio (Active Directory)
- Servidor Interno con base de datos + ejecucion de la app
- Bastion VPN (WireGuard)
- Subredes públicas y privadas
- NAT Gateway para acceso saliente seguro

---

## 🏗️ Arquitectura en AWS

```mermaid
flowchart TB

    Internet((Internet))

    subgraph VPC["VPC 10.1.0.0/16"]

        subgraph PublicA["Public Subnet (10.1.10.0/24)"]
            VPN["VPN Bastion<br/>WireGuard"]
            WEBPUB["Servidor Web Público"]
        end

        subgraph PrivateA["Private Subnet A (10.1.20.0/24)"]
            AD["Controlador de Dominio<br/>Active Directory"]
        end

        subgraph PrivateB["Private Subnet B (10.1.30.0/24)"]
            WEBINT["Servidor Web Interno<br/>+ Base de Datos"]
        end

        NAT["NAT Gateway"]
        IGW["Internet Gateway"]

    end

    Client["Usuario Remoto<br/>Cliente VPN"]

    Client -->|VPN WireGuard<br/>192.168.50.0/24| VPN

    Internet --> IGW
    IGW --> VPN
    IGW --> WEBPUB

    VPN --> AD
    VPN --> WEBINT

    PrivateA --> NAT
    PrivateB --> NAT
    NAT --> IGW
- VPC CIDR: `10.1.0.0/16`
- Red VPN: `10.10.10.0/24`

---

## 🔐 Componentes Principales

### 🧩 Active Directory (AD)

- Autenticación centralizada de usuarios
- Gestión de identidades corporativas
- Integración mediante LDAP desde Python
- Forzado de cambio de contraseña en primer inicio

---

### 🛡️ VPN WireGuard

- Punto de entrada seguro a la red interna
- Gestión dinámica de peers
- Configuración generada automáticamente
- Acceso solo a usuarios activos

---

### 🗄️ Base de Datos

Almacena metadatos de usuarios:

- Información personal
- Estado (activo/deshabilitado)
- Rol
- IP asignada para VPN

La autenticación real se delega a Active Directory.

---

### 🖥️ Servidor Interno

- API de gestión de usuarios
- Generación de configuraciones WireGuard
- Integración con LDAP/AD
- Orquestación del sistema

---

## 👤 Flujo de Onboarding de Usuario

1. Administrador crea usuario en el sistema
2. El backend realiza automáticamente:

   - Creación en Base de Datos
   - Creación en Active Directory
   - Generación de claves WireGuard
   - Asignación de IP VPN
   - Actualización de configuración del servidor VPN

3. Se generan dos archivos para el usuario:

   - Configuración VPN WireGuard (.conf)
   - Script para unir el equipo al dominio

---

## 🧑‍💻 Flujo de Acceso Remoto

### 🟢 Primera vez (Onboarding)

1. Usuario instala WireGuard
2. Importa archivo de configuración VPN
3. Activa la VPN
4. Ejecuta el script de unión al dominio
5. Reinicia el equipo

---

### 🔵 Uso diario

1. El usuario inicia sesión normalmente
2. Activa la VPN cuando necesita recursos internos
3. Accede a servicios corporativos

---

## 🚫 Control de Acceso

Si un usuario es deshabilitado:

- Se marca como inactivo en la base de datos
- Se elimina automáticamente su peer VPN
- Se corta la conexión activa
- Pierde acceso a la red interna

---

## ⚙️ Infraestructura como Código

Toda la infraestructura se despliega mediante Terraform:

- VPC
- Subredes públicas y privadas
- Internet Gateway
- NAT Gateway
- Tablas de rutas
- Instancias EC2
- Bastion VPN

---

## 🔧 Requisitos

- Cuenta AWS
- Terraform >= 1.x
- WireGuard
- Python 3.x
- Acceso administrativo al dominio

---

## 🚀 Despliegue

```bash
terraform init
terraform plan
terraform apply

Posibles Mejoras Futuras

- Always-On VPN

- Integración con grupos de AD para control de acceso

- Multi-factor authentication (MFA)

- Automatización completa del onboarding

- Monitoreo y logging centralizado

- Alta disponibilidad
