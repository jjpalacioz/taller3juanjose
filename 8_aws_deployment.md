# 🚀 Despliegue en AWS EC2

Esta guía explica cómo desplegar el proyecto Django de películas en una instancia **AWS EC2** con Ubuntu.

---

## 📋 Requisitos previos

- Cuenta de AWS activa
- Par de claves SSH (`.pem`) descargado
- El repositorio actualizado en GitHub (incluyendo los cambios de `settings.py`)

---

## 1️⃣ Lanzar una instancia EC2

1. Inicia sesión en la consola de AWS → **EC2 → Launch Instance**.
2. Configuración recomendada:
   | Campo | Valor |
   |---|---|
   | **Name** | `django-moviereviews` |
   | **AMI** | Ubuntu Server 24.04 LTS (free tier eligible) |
   | **Instance type** | `t2.micro` (free tier) |
   | **Key pair** | Crea uno nuevo o selecciona uno existente (guarda el `.pem`) |
   | **Security group** | Permite **SSH (22)** desde tu IP y **HTTP personalizado (8000)** desde `0.0.0.0/0` |

   > ⚠️ Permitir el puerto 8000 desde `0.0.0.0/0` lo expone a Internet. Para una app académica esto es suficiente, pero en producción real usa el puerto 80/443 con nginx y restringe las reglas de acceso.

3. Haz clic en **Launch Instance** y espera a que el estado sea **running**.
4. Anota la **Public IPv4 address** de la instancia (ej. `34.230.71.87`).

---

## 2️⃣ Conectarse por SSH

```bash
# Ajusta los permisos del archivo .pem (solo la primera vez)
chmod 400 tu-clave.pem

# Conectarse
ssh -i tu-clave.pem ubuntu@<PUBLIC_IP>
```

---

## 3️⃣ Preparar el servidor (instalar dependencias)

Ejecuta los siguientes comandos **dentro de la instancia EC2**:

```bash
sudo apt update && sudo apt upgrade -y

# Python 3.11 y herramientas
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Verificar instalación
python3.11 --version
git --version
```

---

## 4️⃣ Clonar el repositorio

```bash
git clone https://github.com/jjpalacioz/taller3juanjose.git
cd taller3juanjose/DjangoProjectBase
```

---

## 5️⃣ Instalar las dependencias de Python

```bash
# (Opcional pero recomendado) crear un entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

> Si `requirements.txt` está en la raíz del repo, usa:
> ```bash
> pip install -r ../requirements.txt
> ```

---

## 6️⃣ Crear el archivo `openAI.env`

El archivo **nunca se sube a GitHub** (está en `.gitignore`). Debes crearlo manualmente en el servidor:

```bash
# Ubicación correcta: DjangoProjectBase/openAI.env
nano openAI.env
```

Contenido del archivo:
```
openai_apikey=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Guarda con `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## 7️⃣ Configurar variables de entorno

Antes de iniciar el servidor establece las variables necesarias:

```bash
# Deshabilitar modo debug en producción
export DJANGO_DEBUG=False

# IP pública de tu EC2 (reemplaza con tu IP real)
export DJANGO_ALLOWED_HOSTS="34.230.71.87"

# Si tienes también el DNS público de la instancia, agrégalo separado por coma:
# export DJANGO_ALLOWED_HOSTS="34.230.71.87,ec2-34-230-71-87.compute.amazonaws.com"
```

> 💡 Para que estas variables persistan entre sesiones, agrégalas al final de `~/.bashrc` y ejecuta `source ~/.bashrc`.

---

## 8️⃣ Aplicar migraciones y recolectar archivos estáticos

```bash
# Dentro de DjangoProjectBase/
python3.11 manage.py migrate
python3.11 manage.py collectstatic --noinput
```

---

## 9️⃣ Iniciar el servidor

### Opción A — Script de inicio automático (recomendado)

```bash
chmod +x start_server.sh
./start_server.sh
```

El script automáticamente obtiene la IP pública de la instancia vía el servicio de metadatos de EC2, corre las migraciones y levanta el servidor.

### Opción B — Manual

```bash
python3.11 manage.py runserver 0.0.0.0:8000
```

---

## 🌐 Acceder a la aplicación

Abre el navegador y navega a:

```
http://<PUBLIC_IP>:8000
```

Por ejemplo: `http://34.230.71.87:8000`

---

## 🔒 Verificación del Security Group

Asegúrate de que el **Security Group** de tu instancia tenga la siguiente regla de entrada:

| Type | Protocol | Port | Source |
|---|---|---|---|
| Custom TCP | TCP | 8000 | 0.0.0.0/0 |
| SSH | TCP | 22 | Tu IP |

Puedes ajustar esto desde **EC2 → Security Groups → Inbound rules → Edit inbound rules**.

---

## ⚙️ Opción avanzada: gunicorn + nginx (producción real)

Para un despliegue de producción más robusto, reemplaza `runserver` con **gunicorn** detrás de **nginx**:

```bash
pip install gunicorn

# Iniciar gunicorn
gunicorn moviereviews.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

Y configura nginx como proxy inverso apuntando al puerto 8000, sirviendo los archivos estáticos desde `staticfiles/` y los archivos de media desde `media/`.

---

## 🛑 Detener el servidor

Presiona `Ctrl+C` en la terminal donde corre el servidor, o encuentra el proceso y mátalo:

```bash
# Encontrar el PID del proceso Django
ps aux | grep manage.py
kill <PID>
```

---

## 📝 Resumen de comandos

```bash
# En tu máquina local (reemplaza valores)
chmod 400 /ruta/tu-clave.pem
ssh -i /ruta/tu-clave.pem ubuntu@<PUBLIC_IP>
```

```bash
# Dentro de EC2 (Ubuntu)
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Clonar y entrar al proyecto
git clone https://github.com/jjpalacioz/taller3juanjose.git
cd taller3juanjose/DjangoProjectBase

# Crear y activar entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de API key (no subir a git)
# IMPORTANTE: reemplaza con tu API key real y no debes subir openAI.env al repositorio.
cat > openAI.env << 'EOF'
openai_apikey=YOUR_OPENAI_API_KEY_HERE
EOF

# Configurar variables de entorno
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS="<PUBLIC_IP>,<PUBLIC_DNS_OPCIONAL>"

# Arrancar app (ejecuta migrate y collectstatic automáticamente)
./start_server.sh
```

Luego abre en tu navegador:
`http://<PUBLIC_IP>:8000`
