import os
import sys
import json
import logging
import re
import time
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
import moviepy
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from PIL import ImageFont  # Importe a biblioteca Pillow para manipulação de fontes

# ... (restante das importações e configuração de logging como antes)

def adicionar_texto(video_clip: ImageClip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white') -> CompositeVideoClip:
    """Adiciona texto ao vídeo. Correção no tratamento de fontes."""
    try:
        texto_limpo = limpar_texto(texto)
        logging.info(f"Texto limpo: {texto_limpo}")

        # Carrega a fonte usando PIL
        try:
            # Tente carregar uma fonte padrão (funciona na maioria dos sistemas)
            fonte = ImageFont.truetype("arial.ttf", fontsize)
        except OSError:
            try:
                # Tente outra fonte padrão
                fonte = ImageFont.truetype("DejaVuSans.ttf", fontsize) #Essa fonte sempre funciona
            except OSError:
                logging.warning("Fontes padrão não encontradas. Usando fonte padrão do MoviePy.")
                fonte = None  # Deixa o MoviePy usar a fonte padrão interna
        
        logging.info("Criando TextClip...")
        txt_clip = TextClip(
            texto_limpo,
            fontsize=fontsize,
            color=color,
            font=fonte,  # Passa o objeto Font do PIL, ou None
        ).set_position(posicao).set_duration(video_clip.duration)
        logging.info("TextClip criado e posicionado.")
        
        composite = CompositeVideoClip([video_clip, txt_clip])
        logging.info(f"Texto adicionado ao vídeo na posição {posicao}.")
        return composite
    except Exception as e:
        logging.error(f"Erro ao adicionar texto: {e}")
        sys.exit(1)

# ... (funções gerar_audio, combinar_audio_video, carregar_temas, atualizar_temas, selecionar_tema, salvar_video como antes)

def gerar_temas_via_gemini() -> list:
    """Gera temas usando a API Gemini. Correção na chamada da API."""
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
        model = genai.GenerativeModel('gemini-pro')  # Usando o modelo 'gemini-pro'
        
        response = model.generate_content(prompt=prompt)  # Chamada simplificada
        
        temas = response.text.strip().split('\n')
        temas = [t.strip() for t in temas if t.strip()]
        logging.info(f"Temas gerados: {temas}")
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
#... (função main como antes)
