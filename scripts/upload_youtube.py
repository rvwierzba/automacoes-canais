import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
import sys

# Ajusta o path para importar config_loader do nível acima
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_loader import carregar_config_canais, obter_canal_por_nome

def carregar_credenciais(client_secrets_file, scopes):
    # Aqui o token.json será criado no mesmo diretório de execução.
    # Você pode preferir guardá-lo no mesmo nível do client_secret.json
    token_path = os.path.join(os.path.dirname(client_secrets_file), 'token.json')
    if os.path.exists(token_path):
        with open(token_path, 'r') as token_file:
            creds_data = json.load(token_file)
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_info(creds_data, scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
            with open(token_path, 'w') as token_file:
                token_file.write(creds.to_json())
        return creds
    else:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        creds = flow.run_console()
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        return creds

def upload_to_youtube(file_path, title, description, tags, category_id='22', privacy_status='public'):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    # O client_secret.json está em ../config/client_secret.json
    client_secrets_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'client_secret.json')

    credentials = carregar_credenciais(client_secrets_file, scopes)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": category_id,
                    "title": title,
                    "description": description,
                    "tags": tags
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            },
            media_body=googleapiclient.http.MediaFileUpload(file_path)
        )
        response = request.execute()
        print(f"Vídeo enviado com sucesso: https://www.youtube.com/watch?v={response['id']}")
    except googleapiclient.errors.HttpError as e:
        print(f"Erro ao enviar o vídeo: {e}")

def main():
    canais = carregar_config_canais()
    canal_youtube = obter_canal_por_nome("FizzQuirkYouTube", canais)
    if not canal_youtube:
        print("Canal FizzQuirkYouTube não encontrado.")
        return

    generated_videos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_videos')
    
    for arquivo_video in os.listdir(generated_videos_dir):
        if arquivo_video.endswith(".mp4"):
            titulo = arquivo_video.replace('.mp4', '').replace('_', ' ')
            caminho_video = os.path.join(generated_videos_dir, arquivo_video)
            descricao = f"Discover more about {titulo} in this fascinating video!"
            tags = canal_youtube.get("hashtags", [])
            upload_to_youtube(caminho_video, titulo, descricao, tags)

if __name__ == "__main__":
    main()
