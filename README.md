# Lodoro Analytics

Sistema de gestión y análisis de órdenes para marketplaces (Paris, Ripley, Falabella).

## Características

- Dashboard con resumen de órdenes por marketplace
- Pistoleo de órdenes para marcarlas como procesadas o impresas
- Visualización de órdenes por marketplace con filtros
- Análisis de ventas con gráficos y estadísticas
- Monitoreo de estado de APIs

## Requisitos

- Python 3.9+
- MySQL/MariaDB
- Base de datos existente con tablas de órdenes

## Instalación

1. Clonar el repositorio:
```
git clone https://github.com/tu-usuario/lodoro-analytics.git
cd lodoro-analytics
```

2. Crear y activar entorno virtual:
```
python -m venv venv
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```
pip install -r requirements.txt
```

4. Configurar la base de datos en `settings.py` (ya está configurada para la base de datos existente).

5. Aplicar migraciones (solo para las nuevas tablas del sistema):
```
python manage.py makemigrations
python manage.py migrate
```

6. Crear un superusuario:
```
python manage.py createsuperuser
```

7. Ejecutar el servidor:
```
python manage.py runserver
```

## Importante sobre la Base de Datos

Este sistema está diseñado para trabajar con una base de datos existente sin modificarla. Los modelos de Django están configurados para:

- **Tablas existentes**: Los modelos de `marketplace` usan `managed=False` para no alterar las tablas existentes.
- **Nuevas tablas**: Solo se crearán nuevas tablas para las funcionalidades adicionales (análisis, escaneos, etc.) con prefijo `lodoro_`.

## Uso

1. Acceder a `http://localhost:8000/` e iniciar sesión con el superusuario creado.
2. Navegar por las diferentes secciones:
   - Dashboard principal
   - Pistoleo de órdenes
   - Órdenes por marketplace
   - Análisis de ventas
   - Estado de APIs

## Estructura del Proyecto

- `core/`: Funcionalidades principales (login, dashboard, pistoleo)
- `marketplace/`: Gestión de órdenes por marketplace
- `analytics/`: Análisis de ventas y rendimiento de productos

## Notas Técnicas

- El sistema usa Bootstrap 5 para la interfaz de usuario
- Los gráficos se generan con Chart.js
- Las consultas a la base de datos están optimizadas para grandes volúmenes de datos 