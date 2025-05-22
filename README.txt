# Lodoro Analytics

Sistema de análisis y gestión de órdenes para marketplaces (Paris, Ripley, Falabella, Mercado Libre) desarrollado en Django.

---

## 🚀 Características principales

- Dashboard de bienvenida con resumen de órdenes por marketplace.
- Análisis de ventas y exportación a Excel.
- Paginación y filtros avanzados en las vistas de órdenes.
- Despacho por escaneo de código de barras (compatible con dispositivos móviles).
- Gestión de usuarios y perfiles.
- Plantillas modernas y responsivas.
- Soporte para despliegue en Heroku y conexión a base de datos MySQL externa.

---

## 🛠️ Instalación local

1. Clona el repositorio:
   git clone https://github.com/tu_usuario/tu_repo.git
   cd tu_repo

2. Crea y activa un entorno virtual:
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

3. Instala las dependencias:
   pip install -r requirements.txt

4. Configura las variables de entorno:
   - Crea un archivo .env con tus credenciales de base de datos y otras variables sensibles.

5. Aplica migraciones y carga datos iniciales:
   python manage.py migrate
   python manage.py createsuperuser

6. Ejecuta el servidor:
   python manage.py runserver

---

## ⚙️ Despliegue en Heroku

1. Agrega los buildpacks necesarios:
   heroku buildpacks:add --index 1 heroku/python --app <nombre-app>
   heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt --app <nombre-app>

2. Configura las variables de entorno en Heroku:
   - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, SECRET_KEY, etc.

3. Haz deploy:
   git push heroku main --app <nombre-app>

4. Ejecuta migraciones:
   heroku run python manage.py migrate --app <nombre-app>

---

## 📦 Dependencias principales

- Django
- django-bootstrap5
- python-barcode
- Pillow
- MySQLclient
- whitenoise

---

## 📸 Funcionalidades destacadas

- Dashboard: Resumen visual de órdenes por marketplace.
- Órdenes: Filtros avanzados, paginación y exportación a Excel.
- Despacho por escaneo: Escaneo de códigos de barras para marcar órdenes como despachadas.
- Gestión de usuarios: Perfil, login/logout, permisos.

---

## 🧪 Plan de pruebas

### Pruebas funcionales

1. Login y logout
   - [ ] El usuario puede iniciar y cerrar sesión correctamente.
   - [ ] El acceso a vistas protegidas redirige a login si no está autenticado.

2. Dashboard
   - [ ] Se muestra el resumen de órdenes por marketplace.
   - [ ] Los datos reflejan correctamente el estado de la base de datos.

3. Órdenes
   - [ ] Se listan las órdenes de cada marketplace.
   - [ ] La paginación funciona correctamente.
   - [ ] Los filtros (estado, año, impreso, etc.) funcionan y actualizan la vista.
   - [ ] La exportación a Excel descarga el archivo correcto.

4. Despacho por escaneo
   - [ ] El escáner de código de barras funciona en dispositivos móviles y escritorio.
   - [ ] Al escanear una orden válida, se marca como despachada y muestra feedback.
   - [ ] Al escanear una orden inválida, muestra mensaje de error.

5. Perfil de usuario
   - [ ] Se muestra la información relevante del usuario.
   - [ ] El usuario puede ver su historial de acceso.

6. Errores y UX
   - [ ] La página 404 personalizada aparece cuando corresponde.
   - [ ] El sidebar y menú se ocultan correctamente en login y para usuarios no autenticados.

### Pruebas de integración

- [ ] Conexión a base de datos MySQL externa desde Heroku.
- [ ] Generación y visualización de códigos de barras en Heroku.
- [ ] Manejo de archivos estáticos en producción (Heroku/WhiteNoise).

### Pruebas de seguridad

- [ ] No se puede acceder a vistas protegidas sin autenticación.
- [ ] Las credenciales y datos sensibles no están expuestos en el código.

---

## 📞 Soporte

Para dudas o soporte, contacta a: [tu_email@dominio.com] 