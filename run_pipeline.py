import subprocess
import os
from dotenv import load_dotenv

def run_script(script_path):
    try:
        subprocess.run(['python', script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_path}: {e}")
        exit(1)  # Encerra o pipeline em caso de erro

def main():
    # Carrega as variáveis de ambiente do .env
    load_dotenv()

    # Define o diretório dos scripts relativo à localização atual (raiz do projeto)
    scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts')

    # Defina os caminhos completos para os scripts
    gerar_tema = os.path.join(scripts_dir, 'generate_theme.py')
    gerar_audio = os.path.join(scripts_dir, 'gerar_audio.py')
    criar_video = os.path.join(scripts_dir, 'criar_video.py')
    upload_youtube = os.path.join(scripts_dir, 'upload_youtube.py')
    upload_tiktok = os.path.join(scripts_dir, 'upload_tiktok.py')  # Se aplicável

    print("Iniciando o pipeline de automação...")

    # Passo 1: Gerar Tema Único
    print("\n[Passo 1] Gerando tema único...")
    run_script(gerar_tema)

    # Passo 2: Gerar Áudio
    print("\n[Passo 2] Gerando áudio...")
    run_script(gerar_audio)

    # Passo 3: Criar Vídeo com Legendas
    print("\n[Passo 3] Criando vídeo com legendas...")
    run_script(criar_video)

    # Passo 4: Upload para YouTube
    print("\n[Passo 4] Fazendo upload para o YouTube...")
    run_script(upload_youtube)

    # Passo 5: Upload para TikTok (Opcional)
    # print("\n[Passo 5] Fazendo upload para o TikTok...")
    # run_script(upload_tiktok)

    print("\nPipeline de automação concluído com sucesso!")

if __name__ == "__main__":
    main()
