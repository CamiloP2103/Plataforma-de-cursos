from gradio_client import Client, file
import os
import shutil
from uuid import uuid4

def generar_podcast_desde_pdf(pdf_path, tono="Fun", duracion="Medium (3-5 min)", idioma="", pregunta=""):
    client = Client("https://bb83a1f5396c4759dc.gradio.live/")
    try:
        result = client.predict(
            files=[file(pdf_path)],
            url="",
            question=pregunta,
            tone=tono,
            length=duracion,
            language=idioma,
            use_advanced_audio=False,
            api_name="/generate_podcast"
        )

        ruta_temporal_mp3, transcripcion = result

        # Crear ruta de destino
        output_dir = os.path.join("static", "podcasts")
        os.makedirs(output_dir, exist_ok=True)
        filename = f"podcast_{uuid4().hex}.mp3"
        output_path = os.path.join(output_dir, filename)

        # Copiar archivo local generado por Gradio a static/podcasts/ Definitivo 
        shutil.copy(ruta_temporal_mp3, output_path)

        ruta_relativa = os.path.join("static", "podcasts", filename)
        return ruta_relativa, transcripcion


    except Exception as e:
        return f"Error al generar podcast: {e}"


