from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import os
import logging
import sys

def criar_video(tema):
    try:
        logging.info(f"Criando vídeo para o tema: {tema}")
        # Criar um clipe de fundo
        fundo = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=10)  # Fundo preto de 10 segundos

        # Criar um clipe de texto
        texto = TextClip(tema, fontsize=70, color='white').set_position('center').set_duration(10)

        # Combinar os clipes
        video = CompositeVideoClip([fundo, texto])

        # Salvar o vídeo
        video_path = f"generated_videos/{tema.replace(' ', '_')}.mp4"
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        video.write_videofile(video_path, codec='libx264', audio=False)
        logging.info(f"Vídeo criado em: {video_path}")
        return video_path
    except Exception as e:
        logging.error(f"Erro ao criar vídeo: {e}")
        sys.exit(1)
