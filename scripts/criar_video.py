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

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('criar_video.log', mode='a')
    ]
)

def obter_caminho_absoluto(relativo):
    """
    Converte um caminho relativo para absoluto baseado na localização do script.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, relativo))

def limpar_texto(texto: str) -> str:
    """
    Remove a formatação Markdown do texto (**, _, etc.).
    """
    texto_limpo = re.sub(r'[\*_]', '', texto)
    return texto_limpo

def adicionar_texto(video_clip: ImageClip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white') -> CompositeVideoClip:
    """
    Adiciona texto ao vídeo usando TextClip.
    Removido o 'method' para evitar conflito com 'font'.
    """
    try:
        texto_limpo = limpar_texto(texto)
        logging.info(f"Texto limpo para adicionar: {texto_limpo}")
        
        # Utilize um nome de fonte reconhecido pelo ImageMagick
        fonte = "DejaVu-Sans"
        logging.info(f"Usando fonte: {fonte}")
        
        logging.info("Criando TextClip...")
        # Removido o method='caption'
        txt_clip = TextClip(
            texto_limpo,
            fontsize=fontsize,
            color=color,
            font=fonte
        )
        logging.info("TextClip criado com sucesso.")
        
        # Ajusta a posição e duração do texto
        txt_clip = txt_clip.set_position(posicao).set_duration(video_clip.duration)
        logging.info(f"TextClip posicionado em {posicao} com duração {video_clip.duration} segundos.")
        
        composite = CompositeVideoClip([video_clip, txt_clip])
        logging.info(f"Texto adicionado ao vídeo na posição {posicao}.")
        return composite
    except TypeError as e:
        logging.error(f"Erro ao adicionar texto ao vídeo: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro inesperado ao adicionar texto ao vídeo: {e}")
        sys.exit(1)

def gerar_audio(texto: str, caminho_audio: str):
    """
    Gera um arquivo de áudio a partir do texto usando gTTS.
    """
    try:
        tts = gTTS(text=texto, lang='en')
        tts.save(caminho_audio)
        logging.info(f"Áudio gerado com sucesso em '{caminho_audio}'.")
    except Exception as e:
        logging.error(f"Erro ao gerar áudio: {e}")
        sys.exit(1)

def combinar_audio_video(video_clip: CompositeVideoClip, caminho_audio: str) -> CompositeVideoClip:
    """
    Combina um arquivo de áudio com o vídeo, se o áudio existir.
    """
    if os.path.exists(caminho_audio):
        try:
            audio_clip = AudioFileClip(caminho_audio)
            audio_clip = audio_clip.set_duration(video_clip.duration)
            video_com_audio = video_clip.set_audio(audio_clip)
            logging.info(f"Áudio '{caminho_audio}' combinado com o vídeo com sucesso.")
            return video_com_audio
        except Exception as e:
            logging.error(f"Erro ao combinar áudio com vídeo: {e}")
            sys.exit(1)
    else:
        logging.warning(f"Arquivo de áudio '{caminho_audio}' não encontrado. Criando vídeo sem áudio.")
        return video_clip

def gerar_temas_via_gemini() -> list:
    """
    Gera uma lista de temas utilizando a API do Gemini do Google.
    Agora utilizando genai.generate_text de forma adequada.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY não está definida no arquivo .env ou nos Secrets do GitHub.")
        sys.exit(1)
    
    max_retries = 3
    retry_delay = 5
    
    prompt = (
        "Generate a list of 5 completely unique and original YouTube video topics related to science. "
        "Each topic should be innovative, not replicate any existing content, and fully comply with copyright laws. "
        "Avoid any direct references or similarities to existing materials."
    )

    for attempt in range(1, max_retries + 1):
        try:
            genai.configure(api_key=api_key)
            
            logging.info("Chamando a API Gemini para gerar novos temas...")
            response = genai.generate_text(
                model="models/gemini-1.5-flash",
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=150
            )

            if not response.candidates:
                logging.error("A resposta da API não contém candidatos.")
                raise ValueError("Resposta inválida da API Gemini.")
            
            texto_gerado = response.candidates[0].output.strip()
            temas = []
            if texto_gerado:
                if '\n' in texto_gerado:
                    temas = [t.strip() for t in texto_gerado.split('\n') if t.strip()]
                else:
                    temas = [t.strip() for t in texto_gerado.split(',') if t.strip()]
            
            if not temas:
                logging.warning("A API Gemini retornou uma lista vazia de temas.")
            else:
                logging.info(f"Temas gerados via Gemini: {temas}")
            return temas
        except Exception as e:
            logging.error(f"Erro ao chamar a API Gemini na tentativa {attempt}: {e}")
        
        if attempt < max_retries:
            logging.info(f"Tentando novamente em {retry_delay} segundos...")
            time.sleep(retry_delay)
        else:
            logging.error("Número máximo de tentativas atingido. Utilizando temas de fallback.")
            return [
                "A Ciência por Trás dos Gadgets do Cotidiano",
                "Computação Quântica: O Futuro da Tecnologia",
                "O Papel da IA na Medicina Moderna",
                "Inovações em Energia Renovável Transformando o Mundo",
                "Mistérios da Matéria Escura e Energia Escura"
            ]

def carregar_temas(caminho_arquivo):
    """
    Carrega os temas do arquivo especificado. Se o arquivo estiver vazio, gera novos temas via Gemini.
    """
    caminho_absoluto = os.path.abspath(caminho_arquivo)
    logging.info(f"Caminho absoluto do arquivo de temas: {caminho_absoluto}")
    
    if not os.path.exists(caminho_arquivo):
        logging.error(f"Arquivo de temas '{caminho_arquivo}' não encontrado.")
        sys.exit(1)
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()
        logging.info(f"Conteúdo do arquivo de temas: {conteudo}")
        try:
            if not conteudo:
                logging.warning(f"Arquivo de temas '{caminho_arquivo}' está vazio. Gerando novos temas via Gemini.")
                temas = gerar_temas_via_gemini()
                atualizar_temas(caminho_arquivo, temas)
                return {"temas": temas}
            data = json.loads(conteudo)
            logging.info(f"Dados carregados do JSON: {data}")

            temas = data.get("temas", [])
            if not temas:
                logging.warning(f"Lista de temas no arquivo '{caminho_arquivo}' está vazia. Gerando novos temas via Gemini.")
                temas = gerar_temas_via_gemini()
                atualizar_temas(caminho_arquivo, temas)
                data["temas"] = temas
                return data

            return data
        except json.JSONDecodeError as e:
            logging.error(f"Erro de decodificação JSON no arquivo de temas: {e}")
            sys.exit(1)

def atualizar_temas(caminho_arquivo: str, novos_temas: list):
    """
    Atualiza o arquivo de temas com os novos temas gerados.
    """
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({"temas": novos_temas}, f, indent=2, ensure_ascii=False)
        logging.info(f"Arquivo de temas '{caminho_arquivo}' atualizado com novos temas.")
    except Exception as e:
        logging.error(f"Erro ao atualizar o arquivo de temas: {e}")
        sys.exit(1)

def selecionar_tema(caminho_temas_novos: str, caminho_temas_usados: str) -> str:
    """
    Seleciona o primeiro tema disponível no arquivo de novos temas e move para usados.
    """
    try:
        with open(caminho_temas_novos, 'r', encoding='utf-8') as f_novos:
            data = json.load(f_novos)
            logging.info(f"Dados carregados do JSON de novos temas: {data}")
        
        temas = data.get("temas", [])
        logging.info(f"Temas disponíveis: {temas}")
        
        if not temas:
            logging.warning("Nenhum tema disponível para processar.")
            return None
        
        tema = temas.pop(0)
        logging.info(f"Tema selecionado: '{tema}'")
        
        with open(caminho_temas_usados, 'a', encoding='utf-8') as f_usados:
            f_usados.write(json.dumps({"tema": tema}, ensure_ascii=False) + '\n')
            logging.info(f"Tema '{tema}' escrito no arquivo '{caminho_temas_usados}'.")

        atualizar_temas(caminho_temas_novos, temas)
        
        return tema
    except json.JSONDecodeError as e:
        logging.error(f"Erro de decodificação JSON no arquivo de novos temas: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro ao selecionar o tema: {e}")
        sys.exit(1)

def salvar_video(video_com_audio: CompositeVideoClip, caminho_saida: str):
    """
    Salva o vídeo final no caminho especificado.
    """
    try:
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
    logging.info("Iniciando o processo de criação de vídeo...")
    
    caminho_background = obter_caminho_absoluto('../assets/background.png')
    caminho_audio = obter_caminho_absoluto('../audios/audio.mp3')
    caminho_saida = obter_caminho_absoluto('../videos/output_video.mp4')
    caminho_temas_novos = obter_caminho_absoluto('../data/temas_novos.json')
    caminho_temas_usados = obter_caminho_absoluto('../data/temas_usados.txt')

    temas_data = carregar_temas(caminho_temas_novos)
    tema = selecionar_tema(caminho_temas_novos, caminho_temas_usados)
    if not tema:
        logging.error("Nenhum tema disponível para criar o vídeo. Encerrando o script.")
        sys.exit(1)

    background = ImageClip(caminho_background, duration=60)
    logging.info(f"Imagem de fundo '{caminho_background}' carregada com sucesso (Versão do MoviePy: {moviepy.__version__}).")

    video_com_texto = adicionar_texto(background, tema, ('center', 'bottom'))
    gerar_audio(tema, caminho_audio)
    video_final = combinar_audio_video(video_com_texto, caminho_audio)
    salvar_video(video_final, caminho_saida)

    logging.info("Processo de criação de vídeo concluído com sucesso.")

if __name__ == "__main__":
    main()
