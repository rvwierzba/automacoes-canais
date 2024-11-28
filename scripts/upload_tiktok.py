from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def upload_to_tiktok(video_path, caption, email, senha):
    # Configuração do WebDriver (certifique-se de que o ChromeDriver está no PATH)
    driver = webdriver.Chrome()
    driver.get("https://www.tiktok.com/upload?lang=en")

    # Tempo para o usuário fazer login manualmente
    print("Por favor, faça login no TikTok manualmente e aguarde...")
    time.sleep(60)  # Ajuste o tempo conforme necessário

    try:
        # Localizar o botão de upload de arquivo
        upload_button = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_button.send_keys(os.path.abspath(video_path))
        print("Arquivo de vídeo enviado.")

        # Aguardar o processamento do vídeo
        time.sleep(30)  # Ajuste conforme necessário

        # Adicionar legenda
        caption_box = driver.find_element(By.XPATH, "//textarea[@placeholder='Add a caption']")
        caption_box.send_keys(caption)
        print("Legenda adicionada.")

        # Publicar o vídeo
        post_button = driver.find_element(By.XPATH, "//button[contains(text(),'Post')]")
        post_button.click()
        print("Vídeo publicado no TikTok com sucesso!")

    except Exception as e:
        print(f"Erro durante o upload: {e}")
    finally:
        time.sleep(10)
        driver.quit()

def main():
    # Carregar credenciais do TikTok do .env
    tiktok_email = os.getenv("TIKTOK_EMAIL")
    tiktok_senha = os.getenv("TIKTOK_SENHA")
    
    # Diretório de vídeos gerados
    generated_videos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_videos')
    
    for arquivo_video in os.listdir(generated_videos_dir):
        if arquivo_video.endswith(".mp4"):
            caminho_video = os.path.join(generated_videos_dir, arquivo_video)
            titulo = arquivo_video.replace('.mp4', '').replace('_', ' ')
            descricao = f"Discover more about {titulo} in this fascinating video!"
            upload_to_tiktok(caminho_video, descricao, tiktok_email, tiktok_senha)

if __name__ == "__main__":
    main()
