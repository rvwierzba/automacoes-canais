import os
import sys
import json
import logging
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, TextClip
import moviepy
import requests
from dotenv import load_dotenv

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

def adicionar_texto(video_clip: ImageClip, texto: str, posicao: tuple, fontsize: int = 70, color: str = 'white') -> CompositeVideoClip:
    try:
        # Chamada correta do TextClip com argumentos posicionais
        txt_clip = TextClip(texto, 'Arial-Bold', fontsize, color)

        txt_clip = txt_clip.set_position(posicao).set_duration(video_clip.duration)
        composite = CompositeVideoClip([video_clip, txt_clip])
        logging.info(f"Texto '{texto}' adicionado ao vídeo na posição {posicao}.")
        return composite
    except Exception as e:
        logging.error(f"Erro ao adicionar texto ao vídeo: {e}")
        sys.exit(1)

def combinar_audio_video(video_clip: CompositeVideoClip, caminho_audio: str) -> CompositeVideoClip:
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

def gerar_temas_via_gemini() -> list:
    """
    Gera uma lista de temas utilizando a API do Gemini.

    :return: Lista de temas gerados.
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY não está definida no arquivo .env.")
        sys.exit(1)
    
    endpoint = "https://api.gemini.com/v1/generate_themes"  # Substitua pelo endpoint real da API Gemini
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "num_themes": 5  # Número de temas a serem gerados
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        temas = data.get("temas", [])
        if not temas:
            logging.warning("Gemini retornou uma lista vazia de temas.")
        else:
            logging.info(f"Temas gerados via Gemini: {temas}")
        return temas
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao chamar a API do Gemini: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar resposta JSON da API do Gemini: {e}")
        sys.exit(1)

def carregar_temas(caminho_arquivo):
    caminho_absoluto = os.path.abspath(caminho_arquivo)
    logging.info(f"Caminho absoluto do arquivo de temas: {caminho_absoluto}")
    
    if not os.path.exists(caminho_arquivo):
        logging.error(f"Arquivo de temas '{caminho_arquivo}' não encontrado.")
        sys.exit(1)
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read().strip()
        logging.info(f"Conteúdo do arquivo de temas: {conteudo}")  # Log do conteúdo
        try:
            if not conteudo:
                logging.warning(f"Arquivo de temas '{caminho_arquivo}' está vazio. Gerando novos temas via Gemini.")
                temas = gerar_temas_via_gemini()
                atualizar_temas(caminho_arquivo, temas)
                return {"temas": temas}
            data = json.loads(conteudo)
            logging.info(f"Dados carregados do JSON: {data}")  # Log dos dados carregados
            return data
        except json.JSONDecodeError as e:
            logging.error(f"Erro ao decodificar JSON no arquivo de temas novos: {e}")
            sys.exit(1)

def atualizar_temas(caminho_arquivo: str, novos_temas: list):
    """
    Atualiza o arquivo de temas com os novos temas gerados.

    :param caminho_arquivo: Caminho para o arquivo de temas novos.
    :param novos_temas: Lista de novos temas a serem adicionados.
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
    Seleciona o primeiro tema disponível no arquivo de temas novos e move para temas usados.

    :param caminho_temas_novos: Caminho para o arquivo de temas novos.
    :param caminho_temas_usados: Caminho para o arquivo de temas usados.
    :return: O tema selecionado ou None se não houver temas disponíveis.
    """
    try:
        with open(caminho_temas_novos, 'r', encoding='utf-8') as f_novos:
            data = json.load(f_novos)
            logging.info(f"Dados carregados do JSON de temas novos: {data}")
        
        temas = data.get("temas", [])
        logging.info(f"Temas disponíveis: {temas}")
        
        if not temas:
            logging.warning("Nenhum tema disponível para processar.")
            return None
        
        tema = temas.pop(0)
        logging.info(f"Tema selecionado: '{tema}'")
        
        # Escreve o tema usado no arquivo de temas usados
        with open(caminho_temas_usados, 'a', encoding='utf-8') as f_usados:
            f_usados.write(json.dumps({"tema": tema}, ensure_ascii=False) + '\n')
            logging.info(f"Tema '{tema}' escrito em '{caminho_temas_usados}'.")
        
        # Atualiza o arquivo de temas novos
        with open(caminho_temas_novos, 'w', encoding='utf-8') as f_novos_write:
            json.dump({"temas": temas}, f_novos_write, indent=2, ensure_ascii=False)
            logging.info(f"Arquivo de temas novos atualizado em '{caminho_temas_novos}'.")
        
        return tema
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar JSON no arquivo de temas novos: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Erro ao selecionar tema: {e}")
        sys.exit(1)

def main():
    """
    Função principal que coordena a criação do vídeo.
    """
    logging.info("Iniciando a criação do vídeo...")

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
        logging.error("Nenhum tema disponível para criar o vídeo. Encerrando o script.")
        sys.exit(1)

    # Carrega a imagem de fundo
    background = carregar_imagem_background(caminho_background)

    # Adiciona texto ao vídeo
    posicao_texto = ('center', 'bottom')  # Posição centralizada na parte inferior
    video_com_texto = adicionar_texto(background, tema, posicao_texto)

    # Combina áudio com vídeo
    video_final = combinar_audio_video(video_com_texto, caminho_audio)

    # Salva o vídeo final
    salvar_video(video_final, caminho_saida)

    logging.info("Processo de criação do vídeo concluído com sucesso.")

if __name__ == "__main__":
    main()
