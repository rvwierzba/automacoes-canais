from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import sys

# Ajusta o path para importar config_loader do nível acima
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_loader import carregar_config_canais, obter_canal_por_nome

def upload_to_tiktok(video_path, caption, email, senha):
    driver = webdriver.Chrome()
    driver.get("https://www.tiktok.com/upload?lang=en")

    print("Por favor, faça login no TikTok manualmente e aguarde...")
    time.sleep(60)  # Tempo para login manual, se necessário

    try:
        upload_button = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_button.send_keys(os.path.abspath(video_path))
        print("Arquivo de vídeo enviado.")
        time.sleep(30)  # Ajuste conforme necessário

        caption_box = driver.find_element(By.XPATH, "//textarea[@placeholder='Add a caption']")
        caption_box.send_keys(caption)
        print("Legenda adicionada.")

        post_button = driver.find_element(By.XPATH, "//button[contains(text(),'Post')]")
        post_button.click()
        print("Vídeo publicado no TikTok com sucesso!")

    except Exception as e:
        print(f"Erro durante o upload: {e}")
    finally:
        time.sleep(10)
        driver.quit()

def main():
    canais = carregar_config_canais()
    canal_tiktok = obter_canal_por_nome("FizzQuirkTikTok", canais)
    if not canal_tiktok:
        print("Canal FizzQuirkTikTok não encontrado.")
        return

    tiktok_email = canal_tiktok["tiktok_email"]
    tiktok_password = canal_tiktok["tiktok_password"]

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
