import os
import json
import sys
import logging

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('run_pipeline.log', mode='a')
    ]
)

def gerar_temas(caminho_saida_novos: str, caminho_saida_usados: str):
    """
    Gera um arquivo JSON com temas para a geração de áudio e move temas para usados.
    
    :param caminho_saida_novos: Caminho para o arquivo de temas novos.
    :param caminho_saida_usados: Caminho para o arquivo de temas usados.
    """
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
