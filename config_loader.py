# config_loader.py
import yaml
import os
import logging
import sys

def carregar_config_canais():
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'canais.yaml')
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Atualiza as credenciais sensíveis a partir das variáveis de ambiente
        for canal in config["canais"]:
            if canal["plataforma"] == "TikTok":
                canal["gemini_api_key"] = os.getenv("GEMINI_API_KEY")
                canal["tiktok_email"] = os.getenv("TIKTOK_EMAIL")
                canal["tiktok_password"] = os.getenv("TIKTOK_PASSWORD")
            elif canal["plataforma"] == "YouTube":
                canal["gemini_api_key"] = os.getenv("GEMINI_API_KEY")
                canal["youtube_api_key"] = os.getenv("YOUTUBE_API_KEY")
                canal["youtube_channel_id"] = os.getenv("YOUTUBE_CHANNEL_ID")
            # Adicione outras plataformas conforme necessário
        return config["canais"]
    except FileNotFoundError:
        logging.error(f"Arquivo de configuração '{caminho}' não encontrado.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logging.error(f"Erro ao ler o arquivo YAML: {e}")
        sys.exit(1)

def obter_canal_por_nome(nome_canal, canais):
    for canal in canais:
        if canal["nome"] == nome_canal:
            return canal
    logging.error(f"Canal '{nome_canal}' não encontrado nas configurações.")
    return None
