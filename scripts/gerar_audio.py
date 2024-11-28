from gtts import gTTS
import os
import json

def gerar_audio(texto, arquivo_audio):
    try:
        tts = gTTS(text=texto, lang='en')
        tts.save(arquivo_audio)
        print(f"Áudio salvo em {arquivo_audio}")
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")

def main():
    # Caminhos
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    temas_novos_file = os.path.join(data_dir, 'temas_novos.json')
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio')
    
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    with open(temas_novos_file, 'r', encoding='utf-8') as f:
        for linha in f:
            if linha.strip():
                tema = json.loads(linha)
                titulo = tema.get('titulo', '').strip()
                if not titulo:
                    continue
                # Crie o texto para a narração
                texto = f"Did you know about {titulo}? Let's dive into some fascinating facts!"
                # Nome do arquivo de áudio
                nome_arquivo = f"{titulo.replace(' ', '_')}.mp3"
                caminho_audio = os.path.join(audio_dir, nome_arquivo)
                # Gerar áudio
                gerar_audio(texto, caminho_audio)

if __name__ == "__main__":
    main()
from gtts import gTTS
import os
import json

def gerar_audio(texto, arquivo_audio):
    try:
        tts = gTTS(text=texto, lang='en')
        tts.save(arquivo_audio)
        print(f"Áudio salvo em {arquivo_audio}")
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")

def main():
    # Caminhos
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    temas_novos_file = os.path.join(data_dir, 'temas_novos.json')
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio')
    
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    with open(temas_novos_file, 'r', encoding='utf-8') as f:
        for linha in f:
            if linha.strip():
                tema = json.loads(linha)
                titulo = tema.get('titulo', '').strip()
                if not titulo:
                    continue
                # Crie o texto para a narração
                texto = f"Did you know about {titulo}? Let's dive into some fascinating facts!"
                # Nome do arquivo de áudio
                nome_arquivo = f"{titulo.replace(' ', '_')}.mp3"
                caminho_audio = os.path.join(audio_dir, nome_arquivo)
                # Gerar áudio
                gerar_audio(texto, caminho_audio)

if __name__ == "__main__":
    main()
