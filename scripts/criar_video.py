import os
import sys
import json
import logging
import re
import time
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
import moviepy.editor as mpe
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from PIL import ImageFont

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('criar_video.log', mode='a')
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
        logging.info(f"Texto limpo: {texto_limpo}")

        try:
            fonte = ImageFont.truetype("arial.ttf", fontsize)
        except OSError:
            try:
                fonte = ImageFont.truetype("DejaVuSans.ttf", fontsize)
            except OSError:
                logging.warning("Fontes padrão não encontradas. Usando fonte padrão do MoviePy.")
                fonte = None

        txt_clip = TextClip(
            texto_limpo,
            fontsize=fontsize,
            color=color,
            font=fonte,
            method='caption'
        ).set_position(posicao).set_duration(video_clip.duration)

        composite = CompositeVideoClip([video_clip, txt_clip])
        return composite
    except Exception as e:
        logging.error(f"Erro ao adicionar texto: {e}")
        sys.exit(1)

def gerar_audio(texto: str, caminho_audio: str):
    try:
        tts = gTTS(text=texto, lang='pt-br') # Mudança para Português Brasileiro
        tts.save(caminho_audio)
        logging.info(f"Áudio gerado em: {caminho_audio}")
    except Exception as e:
        logging.error(f"Erro ao gerar áudio: {e}")
        sys.exit(1)

def combinar_audio_video(video_clip: CompositeVideoClip, caminho_audio: str) -> CompositeVideoClip:
    if os.path.exists(caminho_audio):
        try:
            audio_clip = AudioFileClip(caminho_audio)
            audio_clip = audio_clip.set_duration(video_clip.duration)
            video_com_audio = video_clip.set_audio(audio_clip)
            return video_com_audio
        except Exception as e:
            logging.error(f"Erro ao combinar áudio/vídeo: {e}")
            sys.exit(1)
    else:
        logging.warning(f"Áudio não encontrado: {caminho_audio}")
        return video_clip

def gerar_temas_via_gemini() -> list:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY não definida.")
        sys.exit(1)

    prompt = (
        "Gere uma lista de 5 tópicos de vídeo do YouTube completamente únicos e originais relacionados à ciência. "
        "Cada tópico deve ser inovador, não replicar nenhum conteúdo existente e estar em total conformidade com as leis de direitos autorais. "
        "Evite quaisquer referências diretas ou semelhanças a materiais existentes."
    )

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        temas = response.text.strip().split('\n')
        temas = [t.strip() for t in temas if t.strip()]
        return temas

    except Exception as e:
        logging.error(f"Erro na API Gemini: {e}")
        return [
            "A Ciência por Trás dos Gadgets do Cotidiano",
            "Computação Quântica: O Futuro da Tecnologia",
            "O Papel da IA na Medicina Moderna",
            "Inovações em Energia Renovável Transformando o Mundo",
            "Mistérios da Matéria Escura e Energia Escura"
        ]

def carregar_temas(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        logging.error(f"Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().strip()
            if not conteudo:
                logging.warning(f"Arquivo vazio. Gerando temas via Gemini.")
                temas = gerar_temas_via_gemini()
                atualizar_temas(caminho_arquivo, temas)
                return {"temas": temas}

            data = json.loads(conteudo)
            return data

    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar JSON em {caminho_arquivo}. Gerando temas via Gemini.")
        temas = gerar_temas_via_gemini()
        atualizar_temas(caminho_arquivo, temas)
        return {"temas": temas}
    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {caminho_arquivo}")
        sys.exit(1)

def atualizar_temas(caminho_arquivo: str, novos_temas: list):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({"temas": novos_temas}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Erro ao atualizar arquivo: {e}")
        sys.exit(1)

def selecionar_tema(caminho_temas_novos: str, caminho_temas_usados: str) -> str:
    try:
        with open(caminho_temas_novos, 'r', encoding='utf-8') as f_novos:
            data = json.load(f_novos)
        
        temas = data.get("temas", [])
        if not temas:
            logging.warning("Nenhum tema disponível.")
            return None
        
        tema = temas.pop(0)
        
        with open(caminho_temas_usados, 'a', encoding='utf-8') as f_usados:
            f_usados.write(json.dumps({"tema": tema}, ensure_ascii=False) + '\n')

        atualizar_temas(caminho_temas_novos, temas)
        return tema
    except json.JSONDecodeError:
        logging.error("Erro ao decodificar JSON.")
        sys.exit(1)
    except FileNotFoundError:
        logging.error("Arquivo não encontrado.")
        sys.exit(1)

def salvar_video(video_com_audio: CompositeVideoClip, caminho_saida: str):
    try:
        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
        video_com_audio.write_videofile(caminho_saida, codec='libx264', audio_codec='aac', fps=24) # Adicionado fps
        logging.info(f"Vídeo salvo em: {caminho_saida}")
    except Exception as e:
        logging.error(f"Erro ao salvar o vídeo: {e}")
        sys.exit(1)


def main():
    try:
        # Caminhos
        caminho_imagem = obter_caminho_absoluto("imagens/
