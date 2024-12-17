import os
import sys
import logging
import json

from config_loader import carregar_config_canais, obter_canal_por_nome

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('main.log', mode='a', encoding='utf-8')
    ]
)

def gerar_temas(caminho_saida_novos: str, caminho_saida_usados: str):
    """
    Gera um conjunto de temas exemplo e salva em temas_novos.json.
    Em um cenário real, você chamaria a função que gera temas via API Gemini.
    """
    temas = [
        {"tema": "The Unexpected Physics Of Sneezing", "descricao": "Why Are Sneezes So Loud"},
        {"tema": "The Art of Minimalism"},
        {"tema": "The Science Behind Whispering Galleries"}
    ]
    
    try:
        os.makedirs(os.path.dirname(caminho_saida_novos), exist_ok=True)
        os.makedirs(os.path.dirname(caminho_saida_usados), exist_ok=True)
        
        with open(caminho_saida_novos, 'w', encoding='utf-8') as f_novos:
            for tema in temas:
                json.dump(tema, f_novos)
                f_novos.write('\n')
        
        logging.info(f"Arquivo de temas novos gerado em '{caminho_saida_novos}'.")
    except Exception as e:
        logging.error(f"Erro ao gerar arquivo de temas: {e}")
        sys.exit(1)

def gerar_video():
    """
    Chama o script de criação de vídeo.
    Presumindo que criar_video.py gera o vídeo final em 'generated_videos/'.
    Caso queira integrar a lógica diretamente, basta importar e chamar a função.
    """
    logging.info("Gerando vídeo...")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'criar_video.py')
    ret = os.system(f"python {script_path}")
    if ret != 0:
        logging.error("Erro na geração do vídeo.")
        sys.exit(1)
    logging.info("Vídeo gerado com sucesso.")

def upload_youtube():
    """
    Chama o upload_youtube.py para enviar todos os vídeos da pasta generated_videos para o YouTube.
    """
    logging.info("Fazendo upload para YouTube...")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'upload_youtube.py')
    ret = os.system(f"python {script_path}")
    if ret != 0:
        logging.error("Erro ao enviar vídeo para o YouTube.")
    else:
        logging.info("Vídeo enviado ao YouTube com sucesso.")

def upload_tiktok():
    """
    Chama o upload_tiktok.py para enviar todos os vídeos da pasta generated_videos para o TikTok.
    """
    logging.info("Fazendo upload para TikTok...")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'upload_tiktok.py')
    ret = os.system(f"python {script_path}")
    if ret != 0:
        logging.error("Erro ao enviar vídeo para o TikTok.")
    else:
        logging.info("Vídeo enviado ao TikTok com sucesso.")

def main():
    logging.info("Iniciando pipeline completo...")

    # 1. Gera temas novos
    caminho_saida_novos = os.path.join('data', 'temas_novos.json')
    caminho_saida_usados = os.path.join('data', 'temas_usados.txt')
    gerar_temas(caminho_saida_novos, caminho_saida_usados)

    # 2. Gera vídeo a partir dos temas (criar_video.py deve ler temas_novos.json, selecionar um tema e gerar)
    gerar_video()

    # 3. Faz upload no YouTube
    upload_youtube()

    # 4. Faz upload no TikTok
    upload_tiktok()

    logging.info("Pipeline completo finalizado com sucesso.")

if __name__ == "__main__":
    main()
