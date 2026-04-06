#!/usr/bin/env python
"""
GENERADOR DE IMÁGENES JPG - PRUEBA RÁPIDA
Crea imágenes JPG en lugar de PNG para descartar problemas de formato

Uso LOCAL:
    python generar_imagenes_metas_jpg.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Crear directorio
METAS_DIR = 'static/metas'
os.makedirs(METAS_DIR, exist_ok=True)

# DATOS DE METAS
METAS_DATA = {
    'independencia_financiera': {
        'emoji': '💸',
        'nombre': 'Independencia\nFinanciera',
        'color_bg': '#1a5f3f',
        'color_text': '#ffffff',
    },
    'emprender': {
        'emoji': '🚀',
        'nombre': 'Emprender',
        'color_bg': '#1e40af',
        'color_text': '#ffffff',
    },
    'invertir_mas': {
        'emoji': '📈',
        'nombre': 'Aumentar\nInversiones',
        'color_bg': '#7c2d12',
        'color_text': '#ffffff',
    },
    'comprar_vivienda': {
        'emoji': '🏠',
        'nombre': 'Comprar\nVivienda',
        'color_bg': '#3f3f46',
        'color_text': '#ffffff',
    },
    'viajar': {
        'emoji': '🌍',
        'nombre': 'Viajar y\nDisfrutar',
        'color_bg': '#0369a1',
        'color_text': '#ffffff',
    },
    'educacion': {
        'emoji': '🎓',
        'nombre': 'Educación\ny Formación',
        'color_bg': '#7e22ce',
        'color_text': '#ffffff',
    },
    'calidad_vida': {
        'emoji': '🧘',
        'nombre': 'Calidad\nde Vida',
        'color_bg': '#b91c1c',
        'color_text': '#ffffff',
    },
    'ayudar': {
        'emoji': '❤️',
        'nombre': 'Ayudar\na Otros',
        'color_bg': '#be185d',
        'color_text': '#ffffff',
    },
}

def crear_imagen_jpg(nombre_archivo, emoji, titulo, color_bg, color_text):
    """Crea una imagen JPG simple"""
    
    # Dimensiones
    ancho = 400
    alto = 250
    
    # Crear imagen
    img = Image.new('RGB', (ancho, alto), color=color_bg)
    draw = ImageDraw.Draw(img)
    
    # Intentar usar fuentes
    try:
        titulo_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 48)
    except:
        try:
            titulo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            titulo_font = ImageFont.load_default()
    
    # Dibujar emoji
    try:
        emoji_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
    except:
        emoji_font = titulo_font
    
    emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
    emoji_width = emoji_bbox[2] - emoji_bbox[0]
    emoji_x = (ancho - emoji_width) // 2
    draw.text((emoji_x, 30), emoji, fill=color_text, font=emoji_font)
    
    # Dibujar título
    titulo_bbox = draw.textbbox((0, 0), titulo, font=titulo_font)
    titulo_width = titulo_bbox[2] - titulo_bbox[0]
    titulo_x = (ancho - titulo_width) // 2
    draw.text((titulo_x, 110), titulo, fill=color_text, font=titulo_font)
    
    # Guardar como JPG
    ruta = f'{METAS_DIR}/{nombre_archivo}.jpg'
    img.save(ruta, 'JPEG', quality=95)
    print(f"✅ Creada: {ruta}")

def main():
    print("\n" + "="*60)
    print("🎨 GENERADOR DE IMÁGENES JPG (PRUEBA)")
    print("="*60 + "\n")
    
    for nombre_archivo, datos in METAS_DATA.items():
        crear_imagen_jpg(
            nombre_archivo=nombre_archivo,
            emoji=datos['emoji'],
            titulo=datos['nombre'],
            color_bg=datos['color_bg'],
            color_text=datos['color_text']
        )
    
    print("\n" + "="*60)
    print(f"✅ {len(METAS_DATA)} imágenes JPG creadas")
    print("="*60 + "\n")
    
    # Listar archivos
    print("Archivos creados:")
    for archivo in sorted(os.listdir(METAS_DIR)):
        if archivo.endswith('.jpg'):
            ruta = os.path.join(METAS_DIR, archivo)
            tamaño = os.path.getsize(ruta) / 1024
            print(f"   📄 {archivo} ({tamaño:.1f} KB)")
    
    print("\n✅ Ahora actualiza las rutas en resultado.py:")
    print("   De: /static/metas/XXX.png")
    print("   A:  /static/metas/XXX.jpg")
    print()

if __name__ == '__main__':
    main()