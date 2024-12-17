# scripts/upload_tiktok.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import sys
import logging

from config_loader import carregar_config_canais, obter_canal_por_nome

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('upload_tiktok.log', mode='a', encoding='utf-8')
    ]
)

def upload_to_tiktok(video_path, caption, email, senha):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executa o navegador em modo headless
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.tiktok.com/upload?lang=en")

    # Tempo para realizar o login manualmente, se necessário
    logging.info("Por favor, faça login no TikTok manualmente na interface do navegador e aguarde...")
    time.sleep(300)  # Tempo aumentado para login manual (5 minutos)

    try:
        upload_button = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_button.send_keys(os.path.abspath(video_path))
        logging.info("Arquivo de vídeo enviado.")
        time.sleep(30)  # Ajuste conforme necessário

        caption_box = driver.find_element(By.XPATH, "//textarea[@placeholder='Add a caption']")
        caption_box.send_keys(caption)
        logging.info("Legenda adicionada.")

        post_button = driver.find_element(By.XPATH, "//button[contains(text(),'Post')]")
        post_button.click()
        logging.info("Vídeo publicado no TikTok com sucesso!")

    except Exception as e:
        logging.error(f"Erro durante o upload: {e}")
    finally:
        time.sleep(10)
        driver.quit()

def main():
    canais = carregar_config_canais()
    canal_tiktok = obter_canal_por_nome("FizzQuirkTikTok", canais)
    if not canal_tiktok:
        logging.error("Canal FizzQuirkTikTok não encontrado.")
        sys.exit(1)

    tiktok_email = canal_tiktok.get("tiktok_email")
    tiktok_password = canal_tiktok.get("tiktok_password")

    if not tiktok_email or not tiktok_password:
        logging.error("Credenciais do TikTok não estão definidas.")
        sys.exit(1)

    # Pastas um nível acima, depois 'generated_videos'
    generated_videos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_videos')
    
    for arquivo_video in os.listdir(generated_videos_dir):
        if arquivo_video.endswith(".mp4"):
            caminho_video = os.path.join(generated_videos_dir, arquivo_video)
            titulo = arquivo_video.replace('.mp4', '').replace('_', ' ')
            descricao = f"Discover more about {titulo} in this fascinating video!"
            upload_to_tiktok(caminho_video, descricao, tiktok_email, tiktok_password)

if __name__ == "__main__":
    main()
