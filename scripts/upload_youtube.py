import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def upload_to_youtube(file_path, title, description, tags, category_id='22', privacy_status='public'):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    # Defina os caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    client_secrets_file = os.path.join(os.path.dirname(script_dir), 'credentials.json')  # Coloque credentials.json na raiz do projeto

    # Autenticação
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", credentials=credentials)

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
    # Caminho para os vídeos gerados
    generated_videos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_videos')
    
    for arquivo_video in os.listdir(generated_videos_dir):
        if arquivo_video.endswith(".mp4"):
            titulo = arquivo_video.replace('.mp4', '').replace('_', ' ')
            caminho_video = os.path.join(generated_videos_dir, arquivo_video)
            descricao = f"Discover more about {titulo} in this fascinating video!"
            tags = ["curiosities", "education", "facts"]
            upload_to_youtube(caminho_video, titulo, descricao, tags)

if __name__ == "__main__":
    main()
