# run_pipeline.py
import os
import json
import sys
import logging

from config_loader import carregar_config_canais, obter_canal_por_nome

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('run_pipeline.log', mode='a', encoding='utf-8')
    ]
)

def gerar_temas(caminho_saida_novos: str, caminho_saida_usados: str):
    """
    Gera um arquivo JSON com temas para a geração de áudio e move temas para usados.

    :param caminho_saida_novos: Caminho para o arquivo de temas novos.
    :param caminho_saida_usados: Caminho para o arquivo de temas usados.
    """
    canais = carregar_config_canais()
    canal = obter_canal_por_nome("FizzQuirkTikTok", canais)  # Usando gemini_api_key do TikTok
    if not canal:
        logging.error("Canal FizzQuirkTikTok não encontrado nas configurações.")
        sys.exit(1)
    
    gemini_api_key = canal.get("gemini_api_key")
    if not gemini_api_key:
        logging.error("gemini_api_key não encontrada para o canal FizzQuirkTikTok.")
        sys.exit(1)
    
    # Chamar a API Gemini para gerar temas
    # Aqui você deve implementar a chamada à API Gemini para obter os temas dinamicamente.
    # Por enquanto, vamos usar temas estáticos como exemplo.
    temas = [
        {"tema": "The Unexpected Physics Of Sneezing", "descricao": "Why Are Sneezes So Loud"},
        {"tema": "The Art of Minimalism"},
        {"tema": "The Science Behind Whispering Galleries"}
    ]
    
    try:
        # Garante que o diretório de saída existe
        os.makedirs(os.path.dirname(caminho_saida_novos), exist_ok=True)
        os.makedirs(os.path.dirname(caminho_saida_usados), exist_ok=True)
        
        with open(caminho_saida_novos, 'w', encoding='utf-8') as f_novos, \
             open(caminho_saida_usados, 'a', encoding='utf-8') as f_usados:
            for tema in temas:
                json.dump(tema, f_novos)
                f_novos.write('\n')
                # Opcional: Registrar os temas gerados como usados imediatamente
                # f_usados.write(json.dumps(tema) + '\n')
        
        logging.info(f"Arquivo de temas novos gerado com sucesso em '{caminho_saida_novos}'.")
    except Exception as e:
        logging.error(f"Erro ao gerar arquivo de temas: {e}")
        sys.exit(1)

def main():
    """
    Função principal que coordena a geração do arquivo de temas.
    """
    logging.info("Iniciando o pipeline de geração de temas...")
    
    # Defina os caminhos corretos para os arquivos
    caminho_saida_novos = os.path.join('data', 'temas_novos.json')  # data/temas_novos.json
    caminho_saida_usados = os.path.join('data', 'temas_usados.txt')  # data/temas_usados.txt
    
    gerar_temas(caminho_saida_novos, caminho_saida_usados)
    
    logging.info("Pipeline de geração de temas concluído com sucesso.")

if __name__ == "__main__":
    main()
