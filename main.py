# main.py

import os
import sys
import logging
from moviepy.config import change_settings
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('main.log', mode='a', encoding='utf-8')
        ]
    )

def main():
    configurar_logging()
    logging.info("Iniciando pipeline completo...")

    # Obter variáveis de ambiente
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    youtube_channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    imagemagick_binary = os.getenv('IMAGEMAGICK_BINARY')

    logging.info(f"GEMINI_API_KEY: {'***' if gemini_api_key else 'Não definida'}")
    logging.info(f"YOUTUBE_API_KEY: {'***' if youtube_api_key else 'Não definida'}")
    logging.info(f"YOUTUBE_CHANNEL_ID: {'***' if youtube_channel_id else 'Não definida'}")
    logging.info(f"IMAGEMAGICK_BINARY: {imagemagick_binary}")

    # Verificar se todas as variáveis estão definidas
    if not all([gemini_api_key, youtube_api_key, youtube_channel_id, imagemagick_binary]):
        logging.error("Uma ou mais variáveis de ambiente necessárias não estão definidas.")
        sys.exit(1)

    # Configurar MoviePy para usar o ImageMagick 7 via 'magick'
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary})

    # Gerar temas (exemplo simplificado)
    temas = ["Tecnologia", "Saúde", "Educação"]
    logging.info(f"Temas gerados: {temas}")

    # Criar vídeo para o primeiro tema
    tema = temas[0]
    logging.info(f"Criando vídeo para o tema: {tema}")

    try:
        # Criar um clipe de fundo
        fundo = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=10)  # Fundo preto de 10 segundos

        # Criar um clipe de texto com uma fonte específica
        texto = TextClip(tema, fontsize=70, color='white', font='DejaVu-Sans').set_position('center').set_duration(10)

        # Combinar os clipes
        video = CompositeVideoClip([fundo, texto])

        # Salvar o vídeo com fps=24
        video_path = f"generated_videos/{tema.replace(' ', '_')}.mp4"
        os.makedirs(os.path.dirname(video_path), exist_ok=True)
        video.write_videofile(video_path, codec='libx264', audio=False, fps=24)
        logging.info(f"Vídeo criado em: {video_path}")

    except Exception as e:
        logging.error(f"Erro ao criar vídeo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
