import os
import sys
import json
import logging
import re
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
    
    :param relativo: Caminho relativo.
    :return: Caminho absoluto.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(script_dir, relativo))

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
        # Log da versão do MoviePy
        logging.info(f"Versão do MoviePy: {moviepy.__version__}")
        
        # Cria um ImageClip com a duração definida diretamente no construtor
        background = ImageClip(caminho_background, duration=60)  # Duração padrão de 60 segundos
        logging.info(f"Imagem de fundo '{caminho_background}' carregada com sucesso.")
        return background
    except Exception as e:
        logging.error(f"Erro ao carregar a imagem de fundo: {e}")
        sys.exit(1)

def limpar_texto(texto: str) -> str:
    """
    Remove a formatação Markdown do texto.
    
    :param texto: Texto com formatação Markdown.
    :return: Texto limpo.
    """
    # Remove '**', '_', etc.
    texto_limpo = re.sub(r'[\*_]', '', texto)
    return texto_limpo

def adicionar_texto(video_clip: ImageClip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white') -> CompositeVideoClip:
    """
    Adiciona um texto ao vídeo na posição especificada.
    
    :param video_clip: Clip de vídeo base.
    :param texto: Texto a ser adicionado.
    :param posicao: Tupla indicando a posição do texto (e.g., ('center', 'bottom')).
    :param fontsize: Tamanho da fonte do texto.
    :param color: Cor do texto.
    :return: Um CompositeVideoClip com o texto adicionado.
    """
    try:
        # Limpa o texto de formatação Markdown
        texto_limpo = limpar_texto(texto)
        
        # Criação do TextClip especificando a fonte DejaVu-Sans
        txt_clip = TextClip(texto_limpo, fontsize=fontsize, color=color, font='DejaVu-Sans')
        
        # Ajusta a posição e duração do texto
        txt_clip = txt_clip.set_position(posicao).set_duration(video_clip.duration)
        
        # Combina o texto com o vídeo de fundo
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

    :param texto: Texto a ser convertido em áudio.
    :param caminho_audio: Caminho onde o arquivo de áudio será salvo.
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
    Combina um arquivo de áudio com o vídeo.

    :param video_clip: Clip de vídeo com texto.
    :param caminho_audio: Caminho para o arquivo de áudio.
    :return: Clip de vídeo com áudio combinado.
    """
    if os.path.exists(caminho_audio):
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
    else:
        logging.warning(f"Arquivo de áudio '{caminho_audio}' não encontrado. Criando vídeo sem áudio.")
        return video_clip

def gerar_temas_via_gemini() -> list:
    """
    Gera uma lista de temas utilizando a API do Gemini do Google.

    :return: Lista de temas gerados.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY não está definida no arquivo .env ou nos Secrets do GitHub.")
        sys.exit(1)
    
    try:
        # Configura a API key
        genai.configure(api_key=api_key)
        
        # Define o modelo
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Define o prompt para gerar temas em inglês
        prompt = "Generate a list of 5 interesting YouTube video topics related to science."
        logging.info("Calling Gemini API to generate new topics...")
        
        # Faz a requisição para gerar texto
        response = model.generate_content(prompt)
        logging.info("Response received from Gemini API.")
        
        # Extrai os temas gerados
        temas = []
        texto_gerado = response.text.strip()
        if texto_gerado:
            # Assume que os temas estão separados por linhas ou vírgulas
            if '\n' in texto_gerado:
                temas = [tema.strip() for tema in texto_gerado.split('\n') if tema.strip()]
            else:
                temas = [tema.strip() for tema in texto_gerado.split(',') if tema.strip()]
        
        if not temas:
            logging.warning("Gemini returned an empty list of topics.")
        else:
            logging.info(f"Topics generated via Gemini: {temas}")
        return temas
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        sys.exit(1)

def carregar_temas(caminho_arquivo):
    """
    Carrega os temas do arquivo especificado. Se o arquivo estiver vazio, gera novos temas via Gemini.

    :param caminho_arquivo: Caminho para o arquivo de temas.
    :return: Dicionário com a lista de temas.
    """
    caminho_absoluto = os.path.abspath(caminho_arquivo)
    logging.info(f"Absolute path of themes file: {caminho_absoluto}")
    
    if not os.path.exists(caminho_arquivo):
        logging.error(f"Themes file '{caminho_arquivo}' not found.")
        sys.exit(1)
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()
        logging.info(f"Themes file content: {conteudo}")  # Log do conteúdo
        try:
            if not conteudo:
                logging.warning(f"Themes file '{caminho_arquivo}' is empty. Generating new topics via Gemini.")
                temas = gerar_temas_via_gemini()
                atualizar_temas(caminho_arquivo, temas)
                return {"temas": temas}
            data = json.loads(conteudo)
            logging.info(f"Data loaded from JSON: {data}")  # Log dos dados carregados

            temas = data.get("temas", [])
            if not temas:
                logging.warning(f"Topics list in file '{caminho_arquivo}' is empty. Generating new topics via Gemini.")
                temas = gerar_temas_via_gemini()
                atualizar_temas(caminho_arquivo, temas)
                data["temas"] = temas
                return data

            return data
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in themes file: {e}")
            sys.exit(1)

def atualizar_temas(caminho_arquivo: str, novos_temas: list):
    """
    Atualiza o arquivo de temas com os novos temas gerados.

    :param caminho_arquivo: Caminho para o arquivo de novos temas.
    :param novos_temas: Lista de novos temas a serem adicionados.
    """
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump({"temas": novos_temas}, f, indent=2, ensure_ascii=False)
        logging.info(f"Themes file '{caminho_arquivo}' updated with new topics.")
    except Exception as e:
        logging.error(f"Error updating themes file: {e}")
        sys.exit(1)

def selecionar_tema(caminho_temas_novos: str, caminho_temas_usados: str) -> str:
    """
    Seleciona o primeiro tema disponível no arquivo de novos temas e move para usados.

    :param caminho_temas_novos: Caminho para o arquivo de novos temas.
    :param caminho_temas_usados: Caminho para o arquivo de temas usados.
    :return: O tema selecionado ou None se não houver temas disponíveis.
    """
    try:
        with open(caminho_temas_novos, 'r', encoding='utf-8') as f_novos:
            data = json.load(f_novos)
            logging.info(f"Data loaded from new themes JSON: {data}")
        
        temas = data.get("temas", [])
        logging.info(f"Available topics: {temas}")
        
        if not temas:
            logging.warning("No topics available to process.")
            return None
        
        tema = temas.pop(0)
        logging.info(f"Selected topic: '{tema}'")
        
        # Escreve o tema usado no arquivo de temas usados
        with open(caminho_temas_usados, 'a', encoding='utf-8') as f_usados:
            f_usados.write(json.dumps({"tema": tema}, ensure_ascii=False) + '\n')
            logging.info(f"Topic '{tema}' written to '{caminho_temas_usados}'.")
        
        # Atualiza o arquivo de novos temas
        with open(caminho_temas_novos, 'w', encoding='utf-8') as f_novos_write:
            json.dump({"temas": temas}, f_novos_write, indent=2, ensure_ascii=False)
            logging.info(f"New themes file updated at '{caminho_temas_novos}'.")
        
        return tema
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in new themes file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error selecting topic: {e}")
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
    logging.info("Starting video creation process...")

    # Defina os caminhos corretos para os arquivos usando caminhos absolutos
    caminho_background = obter_caminho_absoluto('../assets/background.png')        # ../assets/background.png
    caminho_audio = obter_caminho_absoluto('../audios/audio.mp3')                # ../audios/audio.mp3
    caminho_saida = obter_caminho_absoluto('../videos/output_video.mp4')         # ../videos/output_video.mp4
    caminho_temas_novos = obter_caminho_absoluto('../data/temas_novos.json')    # ../data/temas_novos.json
    caminho_temas_usados = obter_caminho_absoluto('../data/temas_usados.txt')    # ../data/temas_usados.txt

    # Carrega os temas disponíveis (ou gera novos se estiver vazio)
    temas_data = carregar_temas(caminho_temas_novos)
    
    # Seleciona um tema
    tema = selecionar_tema(caminho_temas_novos, caminho_temas_usados)
    if not tema:
        logging.error("No topics available to create the video. Exiting script.")
        sys.exit(1)

    # Carrega a imagem de fundo
    background = carregar_imagem_background(caminho_background)

    # Adiciona texto ao vídeo
    posicao_texto = ('center', 'bottom')  # Posição centralizada na parte inferior
    video_com_texto = adicionar_texto(background, tema, posicao_texto)

    # Gera áudio a partir do texto do tema
    gerar_audio(tema, caminho_audio)

    # Combina áudio com vídeo
    video_final = combinar_audio_video(video_com_texto, caminho_audio)

    # Salva o vídeo final sem usar o parâmetro 'subtitles'
    salvar_video(video_final, caminho_saida)

    logging.info("Video creation process completed successfully.")

if __name__ == "__main__":
    main()
