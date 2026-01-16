# PRUEBA.APP

Aplicación escolar con Flask, SQLAlchemy y Flask-Login.

## Despliegue en Render

Para desplegar esta aplicación en Render, usa las siguientes configuraciones:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

## Características

- Gestión de Estudiantes y Profesores (CRUD).
- Registro de Asistencia por fechas y turnos.
- Exportación de asistencia a CSV.
- Autenticación de usuarios.
