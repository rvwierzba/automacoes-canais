import os
import re
import json
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import time  # Importado para possíveis delays

# Configuração básica de logging
logging.basicConfig(
    filename='generate_theme.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a API Gemini com a chave da API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY não está definida no arquivo .env.")
    print("Erro: GEMINI_API_KEY não está definida no arquivo .env.")
    exit(1)

genai.configure(api_key=api_key)

# Defina os caminhos dos arquivos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
TEMAS_USADOS_FILE = os.path.join(DATA_DIR, 'temas_usados.txt')
TEMAS_NOVOS_FILE = os.path.join(DATA_DIR, 'temas_novos.json')

def carregar_temas_usados(arquivo_usados):
    if not os.path.exists(arquivo_usados):
        logging.info(f"Arquivo '{arquivo_usados}' não encontrado. Criando um novo.")
        return set()
    with open(arquivo_usados, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f.readlines())

def salvar_tema_usado(tema, arquivo_usados):
    with open(arquivo_usados, 'a', encoding='utf-8') as f:
        f.write(tema + '\n')
    logging.info(f"Tema '{tema}' salvo em '{arquivo_usados}'.")

def gerar_tema_unico(temas_usados):
    prompt = (
        "Provide a unique and interesting curiosity topic in English that has not been used before. "
        "The topic should be concise and suitable for creating an educational video."
    )
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Modelo correto
        response = model.generate_content(prompt)
        tema = response.text.strip()
        
        # Limpeza básica do tema
        tema = re.sub(r'[^A-Za-z0-9\s\-]', '', tema)
        tema = tema.title()
        
        if tema and tema not in temas_usados:
            logging.info(f"Tema gerado: {tema}")
            return tema
        else:
            logging.warning("Tema já utilizado ou inválido. Tentando novamente...")
            return gerar_tema_unico(temas_usados)
    except Exception as e:
        logging.error(f"Erro ao gerar tema: {e}")
        return None

def main():
    try:
        # Carregar temas usados
        temas_usados = carregar_temas_usados(TEMAS_USADOS_FILE)
        logging.info(f"Número de temas já usados: {len(temas_usados)}")
        
        # Gerar um novo tema único
        novo_tema = gerar_tema_unico(temas_usados)
        
        if novo_tema:
            # Salvar o novo tema na lista de temas usados
            salvar_tema_usado(novo_tema, TEMAS_USADOS_FILE)
            print(f"Novo tema gerado: {novo_tema}")
            
            # Salvar o novo tema em temas_novos.json para uso posterior
            with open(TEMAS_NOVOS_FILE, 'a', encoding='utf-8') as f:
                json.dump({"titulo": novo_tema}, f)
                f.write('\n')
            logging.info(f"Tema '{novo_tema}' salvo em '{TEMAS_NOVOS_FILE}'.")
        else:
            print("Não foi possível gerar um novo tema no momento.")
            logging.error("Não foi possível gerar um novo tema no momento.")
    finally:
        # Adicionando um delay para permitir o encerramento adequado do gRPC
        time.sleep(1)
        try:
            if hasattr(genai, 'shutdown'):
                genai.shutdown()
                logging.info("Encerramento do SDK Gemini realizado com sucesso.")
            else:
                logging.warning("Método 'shutdown' não encontrado no SDK Gemini.")
        except Exception as e:
            logging.error(f"Erro ao encerrar o SDK Gemini: {e}")

if __name__ == "__main__":
    main()
