# scripts/criar_video.py
import os
import json
import sys
import logging
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip
from gtts import gTTS

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('criar_video.log', mode='a', encoding='utf-8')
    ]
)

def listar_arquivos_diretorio(diretorio):
    try:
        arquivos = os.listdir(diretorio)
        logging.info(f"Arquivos no diretório '{diretorio}': {arquivos}")
    except Exception as e:
        logging.error(f"Erro ao listar arquivos no diretório '{diretorio}': {e}")

def selecionar_tema(caminho_temas_novos: str):
    try:
        with open(caminho_temas_novos, 'r', encoding='utf-8') as f:
            temas = [json.loads(line) for line in f if line.strip()]
        if not temas:
            logging.error("Nenhum tema disponível para gerar vídeo.")
            sys.exit(1)
        tema = temas.pop(0)  # Seleciona o primeiro tema
        return tema, temas
    except FileNotFoundError:
        logging.error(f"Arquivo de temas '{caminho_temas_novos}' não encontrado.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar JSON: {e}")
        sys.exit(1)

def atualizar_temas(caminho_temas_novos: str, novos_temas: list):
    try:
        with open(caminho_temas_novos, 'w', encoding='utf-8') as f:
            for tema in novos_temas:
                json.dump(tema, f)
                f.write('\n')
    except Exception as e:
        logging.error(f"Erro ao atualizar temas: {e}")
        sys.exit(1)

def gerar_audio(texto: str, caminho_audio: str):
    try:
        # Garante que o diretório 'audio/' exista
        os.makedirs(os.path.dirname(caminho_audio), exist_ok=True)
        # Atualiza o código do idioma para 'pt' para evitar depreciação
        tts = gTTS(text=texto, lang='pt')
        tts.save(caminho_audio)
        logging.info(f"Áudio gerado em: {caminho_audio}")
    except Exception as e:
        logging.error(f"Erro ao gerar áudio: {e}")
        sys.exit(1)

def adicionar_texto(video_clip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white'):
    try:
        txt_clip = TextClip(texto, fontsize=fontsize, color=color).set_position(posicao).set_duration(video_clip.duration)
        return CompositeVideoClip([video_clip, txt_clip])
    except Exception as e:
        logging.error(f"Erro ao adicionar texto: {e}")
        return video_clip

def combinar_audio_video(video_com_texto, caminho_audio: str):
    try:
        audio_clip = AudioFileClip(caminho_audio).set_duration(video_com_texto.duration)
        return video_com_texto.set_audio(audio_clip)
    except Exception as e:
        logging.error(f"Erro ao combinar áudio/vídeo: {e}")
        return video_com_texto

def salvar_video(video_com_audio, caminho_saida: str):
    try:
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        video_com_audio.write_videofile(caminho_saida, codec='libx264', audio_codec='aac', fps=24)
        logging.info(f"Vídeo salvo em: {caminho_saida}")
    except Exception as e:
        logging.error(f"Erro ao salvar o vídeo: {e}")
        sys.exit(1)

def main():
    logging.info("Iniciando a criação do vídeo...")
    
    # Determina o diretório base do projeto (root)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # assuming script is in 'scripts/'
    
    # Caminhos absolutos
    caminho_temas_novos = os.path.join(base_dir, 'data', 'temas_novos.json')
    caminho_temas_usados = os.path.join(base_dir, 'data', 'temas_usados.txt')
    caminho_background = os.path.join(base_dir, 'assets', 'background.png')
    caminho_audio = os.path.join(base_dir, 'audio', 'audio.mp3')
    caminho_saida_video = os.path.join(base_dir, 'generated_videos', 'video_final.mp4')

    # Listar arquivos na raiz para depuração
    listar_arquivos_diretorio(base_dir)
    
    # Seleciona o tema
    tema, novos_temas = selecionar_tema(caminho_temas_novos)
    descricao_tema = tema.get("descricao", "")
    
    # Atualiza os temas restantes
    atualizar_temas(caminho_temas_novos, novos_temas)
    
    # Gera áudio
    gerar_audio(descricao_tema, caminho_audio)
    
    # Cria o vídeo
    try:
        # Listar arquivos no diretório 'assets' antes de tentar abrir a imagem
        listar_arquivos_diretorio(os.path.join(base_dir, 'assets'))
        
        background = ImageClip(caminho_background).set_duration(60)  # 60 segundos
    except FileNotFoundError:
        logging.error(f"Imagem de fundo '{caminho_background}' não encontrada.")
        sys.exit(1)

    video_com_texto = adicionar_texto(background, tema["tema"], ('center', 'bottom'))
    video_com_audio = combinar_audio_video(video_com_texto, caminho_audio)
    salvar_video(video_com_audio, caminho_saida_video)

    logging.info("Vídeo criado com sucesso.")

if __name__ == "__main__":
    main()
