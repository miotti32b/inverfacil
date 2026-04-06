#!/usr/bin/env python
"""
GENERADOR DE IMÁGENES DE METAS
Crea imágenes PNG automáticamente para cada meta financiera

Uso LOCAL:
    python generar_imagenes_metas.py

Genera:
    static/metas/independencia_financiera.png
    static/metas/emprender.png
    static/metas/invertir_mas.png
    static/metas/comprar_vivienda.png
    static/metas/viajar.png
    static/metas/educacion.png
    static/metas/calidad_vida.png
    static/metas/ayudar.png
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

# Crear directorio si no existe
METAS_DIR = 'static/metas'
os.makedirs(METAS_DIR, exist_ok=True)

# DATOS DE METAS CON COLORES Y DESCRIPCIONES
METAS_DATA = {
    'independencia_financiera': {
        'emoji': '💸',
        'nombre': 'Independencia\nFinanciera',
        'color_bg': '#1a5f3f',  # Verde oscuro
        'color_text': '#ffffff',
        'descripcion': 'Ingresos pasivos sin trabajar'
    },
    'emprender': {
        'emoji': '🚀',
        'nombre': 'Emprender',
        'color_bg': '#1e40af',  # Azul oscuro
        'color_text': '#ffffff',
        'descripcion': 'Tu propio negocio'
    },
    'invertir_mas': {
        'emoji': '📈',
        'nombre': 'Aumentar\nInversiones',
        'color_bg': '#7c2d12',  # Naranja oscuro
        'color_text': '#ffffff',
        'descripcion': 'Hacer crecer patrimonio'
    },
    'comprar_vivienda': {
        'emoji': '🏠',
        'nombre': 'Comprar\nVivienda',
        'color_bg': '#3f3f46',  # Gris oscuro
        'color_text': '#ffffff',
        'descripcion': 'Hogar propio pagado'
    },
    'viajar': {
        'emoji': '🌍',
        'nombre': 'Viajar y\nDisfrutar',
        'color_bg': '#0369a1',  # Azul cielo
        'color_text': '#ffffff',
        'descripcion': 'Explorar el mundo'
    },
    'educacion': {
        'emoji': '🎓',
        'nombre': 'Educación\ny Formación',
        'color_bg': '#7e22ce',  # Púrpura
        'color_text': '#ffffff',
        'descripcion': 'Tu desarrollo continuo'
    },
    'calidad_vida': {
        'emoji': '🧘',
        'nombre': 'Calidad\nde Vida',
        'color_bg': '#b91c1c',  # Rojo
        'color_text': '#ffffff',
        'descripcion': 'Trabajar menos, vivir más'
    },
    'ayudar': {
        'emoji': '❤️',
        'nombre': 'Ayudar\na Otros',
        'color_bg': '#be185d',  # Rosa
        'color_text': '#ffffff',
        'descripcion': 'Impactar en otros'
    },
}

def crear_imagen_meta(nombre_archivo, emoji, titulo, color_bg, color_text, descripcion):
    """Crea una imagen PNG bonita para una meta"""
    
    # Dimensiones
    ancho = 400
    alto = 250
    
    # Crear imagen con gradiente (simulado con colores sólidos)
    img = Image.new('RGB', (ancho, alto), color=color_bg)
    draw = ImageDraw.Draw(img)
    
    # Intentar usar fuentes del sistema
    try:
        # Windows
        titulo_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 48)
        desc_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 16)
    except:
        try:
            # Linux/Mac
            titulo_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            # Fallback: usar fuente por defecto
            titulo_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
    
    # Dibujar emoji grande
    try:
        emoji_font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 80)
    except:
        emoji_font = titulo_font
    
    # Emoji centrado arriba
    emoji_bbox = draw.textbbox((0, 0), emoji, font=emoji_font)
    emoji_width = emoji_bbox[2] - emoji_bbox[0]
    emoji_x = (ancho - emoji_width) // 2
    draw.text((emoji_x, 30), emoji, fill=color_text, font=emoji_font)
    
    # Título en el centro
    titulo_bbox = draw.textbbox((0, 0), titulo, font=titulo_font)
    titulo_width = titulo_bbox[2] - titulo_bbox[0]
    titulo_height = titulo_bbox[3] - titulo_bbox[1]
    titulo_x = (ancho - titulo_width) // 2
    draw.text((titulo_x, 110), titulo, fill=color_text, font=titulo_font)
    
    # Descripción abajo
    draw.text((20, 190), descripcion, fill=color_text, font=desc_font)
    
    # Guardar imagen
    ruta = f'{METAS_DIR}/{nombre_archivo}.png'
    img.save(ruta, 'PNG', quality=95)
    print(f"✅ Creada: {ruta}")

def main():
    print("\n" + "="*60)
    print("🎨 GENERADOR DE IMÁGENES DE METAS")
    print("="*60 + "\n")
    
    for nombre_archivo, datos in METAS_DATA.items():
        crear_imagen_meta(
            nombre_archivo=nombre_archivo,
            emoji=datos['emoji'],
            titulo=datos['nombre'],
            color_bg=datos['color_bg'],
            color_text=datos['color_text'],
            descripcion=datos['descripcion']
        )
    
    print("\n" + "="*60)
    print(f"✅ {len(METAS_DATA)} imágenes creadas en: {METAS_DIR}/")
    print("="*60 + "\n")
    
    print("Archivos creados:")
    for archivo in os.listdir(METAS_DIR):
        if archivo.endswith('.png'):
            ruta = os.path.join(METAS_DIR, archivo)
            tamaño = os.path.getsize(ruta) / 1024  # KB
            print(f"   📄 {archivo} ({tamaño:.1f} KB)")
    
    print("\nLas imágenes están listas para usar en:")
    print("   /static/metas/independencia_financiera.png")
    print("   /static/metas/emprender.png")
    print("   (etc...)\n")

if __name__ == '__main__':
    main()