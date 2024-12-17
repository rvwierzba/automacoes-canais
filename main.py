# main.py
import os
import sys
import logging

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
    Chama o script run_pipeline.py para gerar temas.
    """
    logging.info("Gerando temas...")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_pipeline.py')
    ret = os.system(f"python {script_path}")
    if ret != 0:
        logging.error("Erro na geração de temas.")
        sys.exit(1)
    logging.info("Temas gerados com sucesso.")

def gerar_video():
    """
    Chama o script de criação de vídeo.
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
    Chama o script upload_youtube.py para enviar vídeos para o YouTube.
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
    Chama o script upload_tiktok.py para enviar vídeos para o TikTok.
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

    # 2. Gera vídeo a partir dos temas
    gerar_video()

    # 3. Faz upload no YouTube
    upload_youtube()

    # 4. Faz upload no TikTok
    upload_tiktok()

    logging.info("Pipeline completo finalizado com sucesso.")

if __name__ == "__main__":
    main()
