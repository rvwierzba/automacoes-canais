# upload_youtube.py

import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_video_to_youtube(video_path, title, description, tags, category_id, privacy_status, token_file='token.json'):
    logging.info(f"Iniciando upload do vídeo {video_path} para o YouTube.")

    # Carregar as credenciais do token.json
    try:
        creds = Credentials.from_authorized_user_file(token_file, scopes=["https://www.googleapis.com/auth/youtube.upload"])
        logging.info("Credenciais carregadas com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao carregar credenciais: {e}")
        raise

    youtube = build('youtube', 'v3', credentials=creds)

    try:
        request_body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/mp4')

        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logging.info(f"Progresso do upload: {int(status.progress() * 100)}%")

        logging.info(f"Vídeo {video_path} enviado com sucesso. ID do Vídeo: {response.get('id')}")

    except Exception as e:
        logging.error(f"Erro durante o upload do vídeo para o YouTube: {e}")
        raise
