name: Pipeline de Automação de Vídeos

on:
  push:
    branches:
      - main
  workflow_dispatch:
  schedule:
    - cron: '0 5 * * *'  # Executa todos os dias às 05:00 UTC (~2h da manhã no Brasil)
    - cron: '0 19 * * *' # Executa todos os dias às 19:00 UTC (~16h da tarde no Brasil)

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      # Passo 1: Checkout do Código
      - name: Checkout Repository
        uses: actions/checkout@v3

      # Passo 2: Configurar Python
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      # Passo 3: Remover ImageMagick 6 se instalado
      - name: Remove ImageMagick 6
        run: |
          sudo apt-get remove -y imagemagick
        shell: bash

      # Passo 4: Adicionar PPA e Instalar ImageMagick 7 e Fonts DejaVu
      - name: Add PPA and Install ImageMagick 7
        run: |
          sudo apt-get update
          sudo apt-get install -y software-properties-common
          sudo add-apt-repository ppa:ubuntuhandbook1/imagemagick7 -y
          sudo apt-get update
          sudo apt-get install -y imagemagick fonts-dejavu
          magick -version
        shell: bash

      # Passo 5: Ajustar as Políticas de Segurança do ImageMagick 7 para PNG e PNG32
      - name: Adjust ImageMagick 7 Policies for PNG and PNG32
        run: |
          POLICY_FILE="/etc/ImageMagick-7/policy.xml"
          if [ ! -f "$POLICY_FILE" ]; then
            echo "Arquivo policy.xml não encontrado em $POLICY_FILE."
            exit 1
          fi
          # Fazer backup do arquivo policy.xml
          sudo cp "$POLICY_FILE" "${POLICY_FILE}.bak"
          # Remover políticas restritivas existentes para PNG e PNG32
          sudo sed -i '/<policy domain="coder" rights="none" pattern="PNG" \/>/d' "$POLICY_FILE"
          sudo sed -i '/<policy domain="coder" rights="none" pattern="PNG32" \/>/d' "$POLICY_FILE"
          # Adicionar políticas que permitem leitura e escrita para PNG e PNG32
          echo '<policy domain="coder" rights="read|write" pattern="PNG" />' | sudo tee -a "$POLICY_FILE"
          echo '<policy domain="coder" rights="read|write" pattern="PNG32" />' | sudo tee -a "$POLICY_FILE"
          echo "Políticas ajustadas em $POLICY_FILE."
        shell: bash

      # Passo 6: Verificar as Políticas Ajustadas
      - name: Verify ImageMagick 7 Policies
        run: |
          POLICY_FILE="/etc/ImageMagick-7/policy.xml"

          echo "Verificando políticas no arquivo $POLICY_FILE:"
          grep '<policy domain="coder" rights="read|write" pattern="PNG" />' "$POLICY_FILE" && echo "Política para PNG encontrada."
          grep '<policy domain="coder" rights="read|write" pattern="PNG32" />' "$POLICY_FILE" && echo "Política para PNG32 encontrada."
          echo ""
        shell: bash

      # Passo 7: Testar ImageMagick 7 com PNG32
      - name: Test ImageMagick 7 with PNG32
        run: |
          # Criar uma imagem PNG32 de teste
          magick -size 100x100 xc:transparent PNG32:test_png32.png

          # Verificar se a imagem foi criada com sucesso
          if [[ -f "test_png32.png" ]]; then
            echo "PNG32 image created successfully."
          else
            echo "Failed to create PNG32 image."
            exit 1
          fi
        shell: bash

      # Passo 8: Instalar Dependências Python
      - name: Install Python Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
        shell: bash

      # Passo 9: Decodificar e Criar `client_secret.json` e `token.json`
      - name: Decode Secrets and Create JSON Files
        run: |
          echo "${{ secrets.CLIENT_SECRET_JSON }}" | base64 --decode > client_secret.json
          echo "${{ secrets.YOUTUBE_TOKEN_JSON }}" | base64 --decode > token.json
        shell: bash

      # Passo 10: Exportar Variáveis de Ambiente e Configurar MoviePy
      - name: Export Environment Variables and Configure MoviePy
        run: |
          echo "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" >> $GITHUB_ENV
          echo "YOUTUBE_API_KEY=${{ secrets.YOUTUBE_API_KEY }}" >> $GITHUB_ENV
          echo "YOUTUBE_CHANNEL_ID=${{ secrets.YOUTUBE_CHANNEL_ID }}" >> $GITHUB_ENV
          # Configurar MoviePy para usar o ImageMagick 7 via 'magick'
          echo "IMAGEMAGICK_BINARY=magick" >> $GITHUB_ENV
        shell: bash

      # Passo 11: Executar o Script Principal
      - name: Run Main Script
        run: |
          python main.py
        shell: bash

      # Passo 12: Upload de Logs (Opcional)
      - name: Upload Logs
        uses: actions/upload-artifact@v3
        with:
          name: logs
          path: |
            main.log
            run_pipeline.log
            criar_video.log
            upload_youtube.log
            upload_tiktok.log

      # Passo 13: Listar Políticas Ativas do ImageMagick 7 (Para Depuração)
      - name: List Active ImageMagick 7 Policies
        run: |
          magick -list policy
        shell: bash
