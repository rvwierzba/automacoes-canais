import os
import sys
import json
import logging
import re
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
import moviepy.editor as mpe
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from PIL import ImageFont

# Configurações
load_dotenv()
LOG_FILE = 'criar_video.log'
OUTPUT_VIDEO_DIR = "videos"
OUTPUT_AUDIO_DIR = "audio"
IMAGES_DIR = "imagens"
TEMAS_NOVOS_FILE = "temas_novos.json"
TEMAS_USADOS_FILE = "temas_usados.json"

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    ]
)

def obter_caminho_absoluto(relativo):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, relativo))

def limpar_texto(texto: str) -> str:
    return re.sub(r'[\*_]', '', texto)

def adicionar_texto(video_clip: ImageClip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white') -> CompositeVideoClip:
    try:
        texto_limpo = limpar_texto(texto)
        try:
            fonte = ImageFont.truetype("arial.ttf", fontsize)
        except OSError:
            try:
                fonte = ImageFont.truetype("DejaVuSans.ttf", fontsize)
            except OSError:
                logging.warning("Fontes padrão não encontradas. Usando fonte padrão do MoviePy.")
                fonte = None
        txt_clip = TextClip(texto_limpo, fontsize=fontsize, color=color, font=fonte, method='caption').set_position(posicao).set_duration(video_clip.duration)
        composite = CompositeVideoClip([video_clip, txt_clip])
        return composite
    except Exception as e:
        logging.error(f"Erro ao adicionar texto: {e}")
        return video_clip # Retorna o vídeo original em caso de erro

def gerar_audio(texto: str, caminho_audio: str):
    try:
        tts = gTTS(text=texto, lang='pt-br')
        tts.save(caminho_audio)
        logging.info(f"Áudio gerado em: {caminho_audio}")
    except Exception as e:
        logging.error(f"Erro ao gerar áudio: {e}")
        return None # Indica falha na geração do áudio

def combinar_audio_video(video_clip: CompositeVideoClip, caminho_audio: str) -> CompositeVideoClip:
    if not os.path.exists(caminho_audio):
        logging.warning(f"Áudio não encontrado: {caminho_audio}")
        return video_clip
    try:
        audio_clip = AudioFileClip(caminho_audio).set_duration(video_clip.duration)
        return video_clip.set_audio(audio_clip)
    except Exception as e:
        logging.error(f"Erro ao combinar áudio/vídeo: {e}")
        return video_clip

def gerar_temas_via_gemini() -> list:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY não definida.")
        return None  # Retorna None em caso de falha

    prompt = ("Gere uma lista de 5 tópicos de vídeo do YouTube completamente únicos e originais relacionados à ciência. "
                "Cada tópico deve ser inovador, não replicar nenhum conteúdo existente e estar em total conformidade com as leis de direitos autorais. "
                "Evite quaisquer referências diretas ou semelhanças a materiais existentes.")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        temas = [t.strip() for t in response.text.strip().split('\n') if t.strip()]
        return temas
    except Exception as e:
        logging.error(f"Erro na API Gemini: {e}")
        return None # Retorna None em caso de falha

def carregar_temas(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("temas", [])  # Retorna uma lista vazia se "temas" não existir
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning(f"Arquivo {caminho_arquivo} não encontrado ou inválido. Gerando novos temas.")
        return []

def atualizar_temas(caminho_arquivo: str, novos_temas: list):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({"temas": novos_temas}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Erro ao atualizar arquivo: {e}")

def selecionar_tema(caminho_temas_novos: str, caminho_temas_usados: str) -> str:
    temas = carregar_temas(caminho_temas_novos)
    if not temas:
        return None

    tema = temas.pop(0)
    atualizar_temas(caminho_temas_novos, temas)
    try:
        with open(caminho_temas_usados, 'a', encoding='utf-8') as f_usados:
            f_usados.write(json.dumps({"tema": tema}, ensure_ascii=False) + '\n')
    except Exception as e:
      logging.error(f"Erro ao salvar temas usados {e}")
    return tema

def salvar_video(video_com_audio: CompositeVideoClip, caminho_saida: str):
    try:
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        video_com_audio.write_videofile(caminho_saida, codec='libx264', audio_codec='aac', fps=24)
        logging.info(f"Vídeo salvo em: {caminho_saida}")
    except Exception as e:
        logging.error(f"Erro ao salvar o vídeo: {e}")

def main():
    try:
        caminho_imagem = obter_caminho_absoluto(os.path.join(IMAGES_DIR,"background.jpg"))
        caminho_audio = obter_caminho_absoluto(os.path.join(OUTPUT_AUDIO_DIR, "audio.mp3"))
        caminho_video_saida = obter_caminho_absoluto(os.path.join(OUTPUT_VIDEO_DIR, "video_final.mp4"))
        caminho_temas_novos = obter_caminho_absoluto(TEMAS_NOVOS_FILE)
        caminho_temas_usados = obter_caminho_absoluto(TEMAS_USADOS_FILE)

        tema = selecionar_tema(caminho_temas_novos, caminho_temas_usados)

        if not tema:
            logging.error("Nenhum tema disponível.")
            return

        if not gerar_audio(tema, caminho_audio):
          logging.error("Falha ao gerar áudio. Abortando")
          return
        
        if not os.path.exists(caminho_imagem):
          logging.error(f"Imagem não encontrada: {caminho_imagem}")
          return

        video_clip = ImageClip(caminho_imagem).set_duration(5)
        video_
