import os
import sys
import logging
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
from PIL import Image

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('criar_video.log', mode='a')
    ]
)

def carregar_imagem_background(caminho_background: str) -> ImageClip:
    """
    Carrega a imagem de fundo a partir do caminho especificado.
    
    :param caminho_background: Caminho para a imagem de fundo.
    :return: Um objeto ImageClip do moviepy.
    """
    if not os.path.exists(caminho_background):
        logging.error(f"Imagem de fundo '{caminho_background}' não encontrada.")
        sys.exit(1)
    
    try:
        # Carrega a imagem usando Pillow para verificar se está correta
        img = Image.open(caminho_background)
        logging.info(f"Imagem de fundo '{caminho_background}' carregada com sucesso.")
        # Cria um ImageClip com a duração definida posteriormente
        background = ImageClip(caminho_background).set_duration(60)  # Duração padrão de 60 segundos
        return background
    except Exception as e:
        logging.error(f"Erro ao carregar a imagem de fundo: {e}")
        sys.exit(1)

def adicionar_texto(video_clip: ImageClip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white') -> CompositeVideoClip:
    """
    Adiciona texto ao vídeo.
    
    :param video_clip: Clip de vídeo de fundo.
    :param texto: Texto a ser adicionado.
    :param posicao: Posição do texto no vídeo (x, y).
    :param fontsize: Tamanho da fonte do texto.
    :param color: Cor do texto.
    :return: Um objeto CompositeVideoClip com o texto adicionado.
    """
    try:
        txt_clip = TextClip(texto, fontsize=fontsize, color=color, font='Arial-Bold')
        txt_clip = txt_clip.set_position(posicao).set_duration(video_clip.duration)
        composite = CompositeVideoClip([video_clip, txt_clip])
        logging.info(f"Texto '{texto}' adicionado ao vídeo na posição {posicao}.")
        return composite
    except Exception as e:
        logging.error(f"Erro ao adicionar texto ao vídeo: {e}")
        sys.exit(1)

def combinar_audio_video(video_clip: CompositeVideoClip, caminho_audio: str) -> CompositeVideoClip:
    """
    Combina o áudio com o vídeo.
    
    :param video_clip: Clip de vídeo com texto adicionado.
    :param caminho_audio: Caminho para o arquivo de áudio.
    :return: Um objeto CompositeVideoClip com áudio adicionado.
    """
    if not os.path.exists(caminho_audio):
        logging.error(f"Arquivo de áudio '{caminho_audio}' não encontrado.")
        sys.exit(1)
    
    try:
        audio_clip = AudioFileClip(caminho_audio)
        # Ajusta a duração do áudio para coincidir com o vídeo
        audio_clip = audio_clip.set_duration(video_clip.duration)
        video_com_audio = video_clip.set_audio(audio_clip)
        logging.info(f"Áudio '{caminho_audio}' combinado com o vídeo com sucesso.")
        return video_com_audio
    except Exception as e:
        logging.error(f"Erro ao combinar áudio com vídeo: {e}")
        sys.exit(1)

def salvar_video(video_com_audio: CompositeVideoClip, caminho_saida: str):
    """
    Salva o vídeo final no caminho especificado.
    
    :param video_com_audio: Clip de vídeo com áudio.
    :param caminho_saida: Caminho onde o vídeo será salvo.
    """
    try:
        # Garante que o diretório de saída existe
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        video_com_audio.write_videofile(caminho_saida, codec='libx264', audio_codec='aac')
        logging.info(f"Vídeo salvo com sucesso em '{caminho_saida}'.")
    except Exception as e:
        logging.error(f"Erro ao salvar o vídeo: {e}")
        sys.exit(1)

def main():
    """
    Função principal que coordena a criação do vídeo.
    """
    logging.info("Iniciando a criação do vídeo...")
    
    # Defina os caminhos corretos para os arquivos
    caminho_background = os.path.join('..', 'assets', 'background.png')  # ../assets/background.png
    caminho_audio = os.path.join('..', 'audios', 'audio.mp3')  # Atualize conforme necessário
    caminho_saida = os.path.join('..', 'videos', 'output_video.mp4')  # Atualize conforme necessário
    
    # Carrega a imagem de fundo
    background = carregar_imagem_background(caminho_background)
    
    # Adiciona texto ao vídeo
    texto = "The Unexpected Physics Of Whispering Galleries"
    posicao_texto = ('center', 'bottom')  # Posição centralizada na parte inferior
    video_com_texto = adicionar_texto(background, texto, posicao_texto)
    
    # Combina áudio com vídeo
    video_final = combinar_audio_video(video_com_texto, caminho_audio)
    
    # Salva o vídeo final
    salvar_video(video_final, caminho_saida)
    
    logging.info("Processo de criação do vídeo concluído com sucesso.")

if __name__ == "__main__":
    main()
