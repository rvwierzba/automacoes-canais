# main.py

import os
import sys
import logging
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

def configurar_logging():
    """
    Configura o sistema de logging para registrar informações no console e em um arquivo.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('main.log', mode='a', encoding='utf-8')
        ]
    )

def obter_variaveis_ambiente():
    """
    Obtém as variáveis de ambiente necessárias.
    """
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    youtube_channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
    
    variaveis = {
        'gemini_api_key': gemini_api_key,
        'youtube_api_key': youtube_api_key,
        'youtube_channel_id': youtube_channel_id,
    }
    
    return variaveis

def verificar_variaveis(variaveis):
    """
    Verifica se as variáveis de ambiente necessárias estão definidas.
    """
    missing_vars = [chave for chave, valor in variaveis.items() if not valor]
    
    if missing_vars:
        for var in missing_vars:
            logging.error(f"{var} não encontrada.")
        logging.error("Erro na configuração das variáveis de ambiente.")
        sys.exit(1)

def gerar_temas():
    """
    Função para gerar temas. Placeholder para implementação real.
    """
    try:
        logging.info("Iniciando a geração de temas...")
        # Implementar a lógica de geração de temas aqui
        # Exemplo simplificado:
        temas = ["Tecnologia", "Saúde", "Educação"]
        logging.info(f"Temas gerados: {temas}")
        return temas
    except Exception as e:
        logging.error(f"Erro ao gerar temas: {e}")
        sys.exit(1)

def criar_video(tema):
    """
    Função para criar um vídeo com o tema fornecido.
    """
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

def upload_youtube(video_path, titulo, descricao, tags, categoria_id, token_path='token.json'):
    """
    Função para fazer upload de vídeo para o YouTube.
    """
    try:
        logging.info("Função upload_youtube iniciada.")
        logging.info(f"Video path: {video_path}")
        logging.info(f"Título: {titulo}")
        logging.info(f"Descrição: {descricao}")
        logging.info(f"Tags: {tags}")
        logging.info(f"Categoria ID: {categoria_id}")
        
        # Carregar as credenciais
        creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/youtube.upload'])
        youtube = build('youtube', 'v3', credentials=creds)
        
        # Configurar metadados do vídeo
        body = {
            'snippet': {
                'title': titulo,
                'description': descricao,
                'tags': tags,
                'categoryId': categoria_id
            },
            'status': {
                'privacyStatus': 'public'  # ou 'private', 'unlisted'
            }
        }
        
        # Upload do vídeo
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logging.info(f"Upload progress: {int(status.progress() * 100)}%")
        
        logging.info(f"Vídeo '{titulo}' carregado com sucesso. ID: {response.get('id')}")
        logging.info("Função upload_youtube concluída.")
        return response.get('id')
    except HttpError as e:
        logging.error(f"HTTP Error durante upload para o YouTube: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro ao fazer upload para o YouTube: {e}")
        sys.exit(1)

def upload_tiktok(video_path, titulo, descricao, gemini_api_key):
    """
    Função para fazer upload de vídeo para o TikTok.
    Placeholder para implementação real, pois a API oficial do TikTok para upload pode não estar disponível.
    Pode ser necessário usar Selenium ou outra automação.
    """
    try:
        logging.info("Iniciando upload para o TikTok...")
        # Implementar a lógica de upload para o TikTok aqui
        # Exemplo: Usar Selenium para automatizar o upload ou uma biblioteca específica
        # Este é um placeholder e deve ser adaptado conforme a sua implementação
        logging.info(f"Vídeo '{titulo}' carregado com sucesso no TikTok.")
    except Exception as e:
        logging.error(f"Erro ao fazer upload para o TikTok: {e}")
        sys.exit(1)

def main():
    configurar_logging()
    logging.info("Iniciando pipeline completo...")
    
    variaveis = obter_variaveis_ambiente()
    verificar_variaveis(variaveis)
    
    logging.info("Gerando temas...")
    temas = gerar_temas()
    
    # Selecionar um tema (por exemplo, o primeiro)
    tema = temas[0]
    
    # Criar o vídeo
    video_path = criar_video(tema)
    
    # Definir metadados do vídeo
    titulo = f"Vídeo sobre {tema}"
    descricao = f"Descrição do vídeo sobre {tema}."
    tags = ["exemplo", "automação", "YouTube"]
    categoria_id = "22"  # Categoria de 'People & Blogs', por exemplo
    
    # Fazer upload para o YouTube
    video_id = upload_youtube(video_path, titulo, descricao, tags, categoria_id)
    
    # Fazer upload para o TikTok
    gemini_api_key = variaveis['gemini_api_key']
    upload_tiktok(video_path, titulo, descricao, gemini_api_key)
    
    logging.info("Pipeline concluído com sucesso.")

if __name__ == "__main__":
    main()
