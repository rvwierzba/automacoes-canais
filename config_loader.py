import yaml
import os

def carregar_config_canais():
    # Localiza o canais.yaml na pasta config que está na raiz do projeto
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'canais.yaml')
    with open(caminho, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config["canais"]

def obter_canal_por_nome(nome_canal, canais):
    for canal in canais:
        if canal["nome"] == nome_canal:
            return canal
    return None
