1. Clona el proyecto y entra a la carpeta.
2. Crea un entorno virtual (recomendado): 
   - Linux/mac: python -m venv venv && source venv/bin/activate
   - Windows: python -m venv venv && venv\Scripts\activate
3. Instala dependencias: pip install -r requirements.txt
4. Cambia la `app.secret_key` en app.py por una cadena segura.
5. Ejecuta: python app.py
6. Abre http://127.0.0.1:5000 en tu navegador.

Notas:
- Los videos de YouTube en data/courses.json deben usar el formato embed: https://www.youtube.com/embed/VIDEO_ID
- La encuesta final está deshabilitada (botón disabled). La implementamos cuando quieras.
"# pagina_estudiantes" 
