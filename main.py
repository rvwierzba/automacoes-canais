# main.py

import os
import sys
import logging
from moviepy.config import change_settings
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
from scripts.upload_youtube import upload_video_to_youtube
from scripts.upload_tiktok import upload_video_to_tiktok

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('main.log', mode='a', encoding='utf-8')
        ]
    )

def criar_video(tema):
    logging.info(f"Iniciando criação do vídeo para o tema: {tema}")
    fundo = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=10)
    texto = TextClip(tema, fontsize=70, color='white', font='DejaVu-Sans').set_position('center').set_duration(10)
    video = CompositeVideoClip([fundo, texto])
    video_path = f"generated_videos/{tema.replace(' ', '_')}.mp4"
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    logging.info(f"Escrevendo o vídeo para o caminho: {video_path}")
    video.write_videofile(video_path, codec='libx264', audio=False, fps=24)
    logging.info(f"Vídeo criado em: {video_path}")
    return video_path

def upload_video(video_path, plataforma, credentials):
    logging.info(f"Iniciando upload do vídeo: {video_path} para {plataforma}")
    try:
        if plataforma.lower() == 'youtube':
            title = "Título do Vídeo"
            description = "Descrição do vídeo."
            tags = ["tag1", "tag2"]
            category_id = "22"  # Categoria de exemplo (22 = People & Blogs)
            privacy_status = "public"  # Ou "private", "unlisted"
            upload_video_to_youtube(video_path, title, description, tags, category_id, privacy_status)
        elif plataforma.lower() == 'tiktok':
            access_token = credentials.get('tiktok_access_token')
            if not access_token:
                logging.error("Access token para TikTok não fornecido.")
                return
            title = "Título do Vídeo"
            upload_video_to_tiktok(video_path, access_token, title)
        else:
            logging.warning(f"Plataforma de upload '{plataforma}' não reconhecida.")
    except Exception as e:
        logging.error(f"Erro ao fazer upload do vídeo {video_path} para {plataforma}: {e}")
        sys.exit(1)

def main():
    configurar_logging()
    logging.info("Iniciando pipeline completo...")

    # Obter variáveis de ambiente
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')  # Pode ser usado dependendo da implementação
    youtube_channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    imagemagick_binary = os.getenv('IMAGEMAGICK_BINARY')
    tiktok_access_token = os.getenv('TIKTOK_ACCESS_TOKEN')  # Adicionado para TikTok

    logging.info(f"GEMINI_API_KEY: {'***' if gemini_api_key else 'Não definida'}")
    logging.info(f"YOUTUBE_API_KEY: {'***' if youtube_api_key else 'Não definida'}")
    logging.info(f"YOUTUBE_CHANNEL_ID: {'***' if youtube_channel_id else 'Não definida'}")
    logging.info(f"IMAGEMAGICK_BINARY: {imagemagick_binary}")
    logging.info(f"TIKTOK_ACCESS_TOKEN: {'***' if tiktok_access_token else 'Não definida'}")

    # Verificar se todas as variáveis estão definidas
    if not all([gemini_api_key, youtube_api_key, youtube_channel_id, imagemagick_binary, tiktok_access_token]):
        logging.error("Uma ou mais variáveis de ambiente necessárias não estão definidas.")
        sys.exit(1)

    # Configurar MoviePy para usar o ImageMagick 7 via 'magick'
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary})
    logging.info("Configurando MoviePy para usar o ImageMagick 7 via 'magick'.")

    # Gerar temas (exemplo simplificado)
    temas = ["Tecnologia", "Saúde", "Educação"]
    logging.info(f"Temas gerados: {temas}")

    # Credenciais para upload
    credentials = {
        'tiktok_access_token': tiktok_access_token
    }

    # Criar e fazer upload dos vídeos
    for tema in temas:
        video_path = criar_video(tema)
        upload_video(video_path, 'youtube', credentials)
        upload_video(video_path, 'tiktok', credentials)

if __name__ == "__main__":
    main()
