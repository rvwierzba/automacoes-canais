# upload_tiktok.py

import logging
import requests
import os

def upload_video_to_tiktok(video_path, access_token, title=""):
    logging.info(f"Iniciando upload do vídeo {video_path} para o TikTok.")

    url = "https://open-api.tiktok.com/share/video/upload/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    files = {
        "video": open(video_path, "rb")
    }
    data = {
        "title": title
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        if result.get("status_code") == 0:
            logging.info(f"Vídeo {video_path} enviado com sucesso para o TikTok.")
        else:
            logging.error(f"Erro no upload para o TikTok: {result}")
            raise Exception(result)

    except Exception as e:
        logging.error(f"Erro durante o upload do vídeo para o TikTok: {e}")
        raise
