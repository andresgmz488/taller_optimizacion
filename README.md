# RedSalud – Optimización de la distribución de medicamentos

Aplicación en Streamlit que resuelve el problema de transporte de RedSalud con PuLP.
Capacidades, demandas, costos y el límite de la ruta Rionegro → Hospital Central
se editan desde la interfaz; el escenario inicial aparece como valor predeterminado.

## Archivos
- `modelo.py` – modelo de programación lineal en PuLP (Parte 2).
- `app.py` – interfaz en Streamlit (Parte 3).
- `requirements.txt` – dependencias para Streamlit Community Cloud.
- `.streamlit/config.toml` – tema de colores.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```
Prueba solo el modelo por consola: `python modelo.py`

## Desplegar desde GitHub (Streamlit Community Cloud)
1. Crea un repositorio **público** en GitHub, por ejemplo `redsalud-app`.
2. Sube estos archivos a la raíz del repositorio (incluida la carpeta `.streamlit`):
   ```bash
   git init
   git add .
   git commit -m "App de optimización RedSalud"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/redsalud-app.git
   git push -u origin main
   ```
   (También puedes usar *Add file → Upload files* en la web de GitHub.)
3. Entra a https://share.streamlit.io e inicia sesión con tu cuenta de GitHub.
4. Pulsa **Create app → Deploy a public app from GitHub**.
5. Elige el repositorio, la rama `main` y como *Main file path* escribe `app.py`.
6. (Opcional) En *App URL* elige un subdominio, p. ej. `redsalud-optimizacion`.
7. Pulsa **Deploy**. En 1–3 minutos tendrás un enlace `https://<nombre>.streamlit.app`:
   ese es el enlace que se entrega.

Cada `git push` a `main` actualiza la app desplegada automáticamente.
