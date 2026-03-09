import os
import re
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont

COLUNAS = 2
LINHAS = 3
FOTOS_POR_PAGINA = COLUNAS * LINHAS

LARGURA_PAGINA = 595
ALTURA_PAGINA = 842

MARGEM_SUPERIOR = 150
MARGEM_LATERAL = 70
ESPACO = 15

TAMANHO_FONTE_TITULO = 38
TAMANHO_FONTE_NOME = 30

COR_TEXTO = (0, 0, 0)
POSICAO_TEXTO_X_PROP = 0.52
POSICAO_TEXTO_Y_PROP = 0.162
ESPACO_TEXTO_IMAGEM = 10

FONTE_PADRAO = "arial.ttf"

TEMPLATE_IMAGE = None

def natural_sort_key(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', s)
    ]

def carregar_template_como_imagem(template_path):
    doc = fitz.open(template_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img


def carregar_fontes():
    try:
        fonte_titulo = ImageFont.truetype(FONTE_PADRAO, TAMANHO_FONTE_TITULO)
        fonte_nome = ImageFont.truetype(FONTE_PADRAO, TAMANHO_FONTE_NOME)
    except Exception:
        fonte_titulo = ImageFont.load_default()
        fonte_nome = ImageFont.load_default()
    return fonte_titulo, fonte_nome


def gerar_paginas_com_fotos(fotos, template_image, nome_pasta):
    paginas = []
    largura_img, altura_img = template_image.size

    largura_util = LARGURA_PAGINA - 2 * MARGEM_LATERAL - (COLUNAS - 1) * ESPACO
    altura_util = ALTURA_PAGINA - MARGEM_SUPERIOR - 60 - (LINHAS - 1) * ESPACO

    largura_foto = largura_util / COLUNAS
    altura_foto = altura_util / LINHAS

    fonte_titulo, fonte_nome = carregar_fontes()

    for i in range(0, len(fotos), FOTOS_POR_PAGINA):
        pagina = template_image.copy()
        draw = ImageDraw.Draw(pagina)

        draw.text(
            (
                int(largura_img * POSICAO_TEXTO_X_PROP),
                int(altura_img * POSICAO_TEXTO_Y_PROP)
            ),
            nome_pasta,
            fill=COR_TEXTO,
            font=fonte_titulo,
            anchor="mm"
        )

        for idx, (img, nome_arquivo) in enumerate(fotos[i:i + FOTOS_POR_PAGINA]):
            col = idx % COLUNAS
            lin = idx // COLUNAS

            escala_w = largura_img / LARGURA_PAGINA
            escala_h = altura_img / ALTURA_PAGINA

            x = int((MARGEM_LATERAL + col * (largura_foto + ESPACO)) * escala_w)
            y = int((MARGEM_SUPERIOR + lin * (altura_foto + ESPACO)) * escala_h)

            slot_w = int(largura_foto * escala_w)
            slot_h = int(altura_foto * escala_h)

            prop_slot = slot_w / slot_h
            prop_img = img.width / img.height

            if prop_img > prop_slot:
                new_h = slot_h
                new_w = int(new_h * prop_img)
            else:
                new_w = slot_w
                new_h = int(new_w / prop_img)

            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            left = (new_w - slot_w) // 2
            top = (new_h - slot_h) // 2

            if img.height > img.width:
                img = img.rotate(90, expand=True)
            
            ratio = min(slot_w / img.width, slot_h / img.height)

            new_w = int(img.width * ratio)
            new_h = int(img.height * ratio)

            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            pos_x = x + (slot_w - new_w) // 2
            pos_y = y + (slot_h - new_h) // 2

            pagina.paste(img_resized, (pos_x, pos_y))

            nome_sem_ext = os.path.splitext(os.path.basename(nome_arquivo))[0]

            texto_x = x + slot_w // 2
            texto_y = y + slot_h + ESPACO_TEXTO_IMAGEM

            draw.text(
                (texto_x, texto_y),
                nome_sem_ext,
                fill=COR_TEXTO,
                font=fonte_nome,
                anchor="mt"
            )

        paginas.append(pagina)

    return paginas


def gerar_pdf_para_pasta(pasta, template_image):
    nome_pasta = os.path.basename(pasta)
    fotos = []

    for arquivo in sorted(os.listdir(pasta), key=natural_sort_key):
        if arquivo.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                img = Image.open(os.path.join(pasta, arquivo)).convert("RGB")
                fotos.append((img, arquivo))
            except Exception as e:
                print(f"Erro ao abrir {arquivo}: {e}")

    if not fotos:
        return

    paginas = gerar_paginas_com_fotos(fotos, template_image, nome_pasta)

    pdf_path = os.path.join(pasta, f"{nome_pasta}.pdf")
    paginas[0].save(
        pdf_path,
        save_all=True,
        append_images=paginas[1:],
        resolution=300
    )

    for img, _ in fotos:
        img.close()


def main(base_dirs, template_path):
    if not os.path.exists(template_path):
        raise Exception("Template não encontrado")

    template_image = carregar_template_como_imagem(template_path)

    pastas_base = [p.strip() for p in base_dirs.split(";") if p.strip()]

    for base in pastas_base:
        if not os.path.exists(base):
            continue

    tem_imagem_base = any(
        f.lower().endswith((".jpg", ".jpeg", ".png"))
        for f in os.listdir(base)
    )

    if tem_imagem_base:
        gerar_pdf_para_pasta(base, template_image)

    for item in sorted(os.listdir(base)):
        caminho = os.path.join(base, item)
        if os.path.isdir(caminho):
            gerar_pdf_para_pasta(caminho, template_image)