import os
import re
from moviepy import ImageClip, TextClip, CompositeVideoClip, AudioFileClip

def sanitize_filename(filename):
    # Remove caracteres inválidos para nomes de arquivos
    return re.sub(r'[\\/*?:"<>|]', "", filename).replace(' ', '_')

def create_video(background_path, logo_path, audio_path, output_video, title, subtitle_text):
    try:
        # Carregar áudio
        audio = AudioFileClip(audio_path)
        
        # Carregar imagem de fundo e definir duração para a duração do áudio
        background = ImageClip(background_path).set_duration(audio.duration).resize(height=720)
        background = background.resize(width=1280)  # Ajusta a largura para 1280
        
        # Carregar o logo e redimensionar (se existir)
        if os.path.exists(logo_path):
            logo = ImageClip(logo_path, transparent=True).set_duration(audio.duration)
            logo = logo.resize(height=100)  # Redimensiona o logo para 100 pixels de altura
            # Posicionar o logo no canto inferior direito com margem
            logo = logo.set_position(("right", "bottom")).margin(right=10, bottom=10, opacity=0)
        else:
            logo = None
            print(f"Logo não encontrado em {logo_path}. O vídeo será criado sem logo.")
        
        # Criar um clipe de texto para o título
        txt_clip = TextClip(title, fontsize=70, color='white', stroke_color='black', stroke_width=2)
        txt_clip = txt_clip.set_position('top').set_duration(audio.duration).margin(top=10, opacity=0)
        
        # Criar um clipe de texto para as legendas (subtitles)
        subtitle_clip = TextClip(subtitle_text, fontsize=40, color='white', stroke_color='black', stroke_width=1, method='caption', size=(1100, None))
        subtitle_clip = subtitle_clip.set_position(('center', 'bottom')).set_duration(audio.duration).margin(bottom=50, opacity=0)
        
        # Combinar todos os elementos
        if logo:
            video = CompositeVideoClip([background, logo, txt_clip, subtitle_clip])
        else:
            video = CompositeVideoClip([background, txt_clip, subtitle_clip])
        
        # Adicionar áudio ao vídeo
        video = video.set_audio(audio)
        
        # Exportar o vídeo
        video.write_videofile(output_video, fps=24, codec='libx264', audio_codec='aac')
        
        # Fechar os clipes para liberar recursos
        audio.close()
        background.close()
        if logo:
            logo.close()
        txt_clip.close()
        subtitle_clip.close()
        video.close()
        
        print(f"Vídeo criado: {output_video}")
    except Exception as e:
        print(f"Erro ao criar o vídeo {output_video}: {e}")

def main():
    # Caminhos
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
    background_path = os.path.join(assets_dir, 'background.png')  # Substitua por assets/background.png
    logo_path = os.path.join(assets_dir, 'logo.png')  # Utilize a versão transparente do logo
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio')
    generated_videos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generated_videos')
    
    # Verifique se a pasta de vídeos gerados existe, caso contrário, crie
    if not os.path.exists(generated_videos_dir):
        os.makedirs(generated_videos_dir)
    
    for arquivo_audio in os.listdir(audio_dir):
        if arquivo_audio.endswith(".mp3"):
            titulo = arquivo_audio.replace('.mp3', '').replace('_', ' ')
            caminho_audio = os.path.join(audio_dir, arquivo_audio)
            nome_video = f"{sanitize_filename(titulo)}.mp4"
            caminho_video = os.path.join(generated_videos_dir, nome_video)
            
            # Defina as legendas (subtitles) com base no tema
            # Você pode personalizar este texto conforme necessário
            subtitle_text = f"Did you know about {titulo}? Let's dive into some fascinating facts!"
            
            # Criar vídeo
            create_video(background_path, logo_path, caminho_audio, caminho_video, titulo, subtitle_text)

if __name__ == "__main__":
    main()
