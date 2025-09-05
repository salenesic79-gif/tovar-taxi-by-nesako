from PIL import Image, ImageEnhance, ImageFilter
import os

def convert_ttaxi_icon():
    """Konvertuje TTaxi.png u ultra-jasne formate za shortcuts"""
    
    # Putanja do originalne slike
    input_path = "static/images/TTaxi.png"
    output_dir = "static/images/"
    
    if not os.path.exists(input_path):
        print(f"❌ Fajl {input_path} ne postoji!")
        return
    
    try:
        # Učitaj originalnu sliku
        img = Image.open(input_path)
        print(f"✅ Učitana slika: {img.size} pixels, mode: {img.mode}")
        
        # Konvertuj u RGBA ako nije
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # ULTRA SHARP verzija sa maksimalnim kontrastom
        ultra_sharp = img.copy()
        
        # 1. Povećaj kontrast na maksimum
        enhancer = ImageEnhance.Contrast(ultra_sharp)
        ultra_sharp = enhancer.enhance(2.0)
        
        # 2. Povećaj oštrinu na maksimum
        enhancer = ImageEnhance.Sharpness(ultra_sharp)
        ultra_sharp = enhancer.enhance(3.0)
        
        # 3. Povećaj zasićenost boja
        enhancer = ImageEnhance.Color(ultra_sharp)
        ultra_sharp = enhancer.enhance(1.8)
        
        # 4. Unsharp mask filter za dodatnu oštrinu
        ultra_sharp = ultra_sharp.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        # Sačuvaj ultra sharp PNG
        ultra_path = os.path.join(output_dir, "TTaxi_ULTRA_SHARP.png")
        ultra_sharp.save(ultra_path, format='PNG', optimize=True)
        print(f"✅ Kreiran: {ultra_path}")
        
        # ICO format sa ultra sharp verzijom
        ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
        ico_images = []
        
        for size in ico_sizes:
            resized = ultra_sharp.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(resized)
        
        ico_path = os.path.join(output_dir, "TTaxi_ULTRA_SHARP.ico")
        ico_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print(f"✅ Kreiran: {ico_path}")
        
        # Verzija sa crnim outline-om za bolju vidljivost
        outlined = ultra_sharp.copy()
        # Dodaj crni outline
        outlined = outlined.filter(ImageFilter.FIND_EDGES)
        outlined = ImageEnhance.Contrast(outlined).enhance(3.0)
        
        outline_path = os.path.join(output_dir, "TTaxi_OUTLINED.png")
        outlined.save(outline_path, format='PNG', optimize=True)
        print(f"✅ Kreiran: {outline_path}")
        
        # 32x32 verzija (standardna za Windows shortcuts)
        small_sharp = ultra_sharp.resize((32, 32), Image.Resampling.LANCZOS)
        small_path = os.path.join(output_dir, "TTaxi_32x32_SHARP.png")
        small_sharp.save(small_path, format='PNG', optimize=True)
        print(f"✅ Kreiran: {small_path}")
        
        # BMP sa ultra sharp verzijom
        bmp_path = os.path.join(output_dir, "TTaxi_ULTRA_SHARP.bmp")
        ultra_sharp.convert('RGB').save(bmp_path, format='BMP')
        print(f"✅ Kreiran: {bmp_path}")
        
        print("\n🎯 ULTRA SHARP KONVERZIJA ZAVRŠENA!")
        print("Testiraj ove ULTRA JASNE formate:")
        print("1. TTaxi_ULTRA_SHARP.ico - Maksimalni kontrast ICO")
        print("2. TTaxi_ULTRA_SHARP.png - Maksimalni kontrast PNG")
        print("3. TTaxi_OUTLINED.png - Sa crnim outline-om")
        print("4. TTaxi_32x32_SHARP.png - Mala ultra sharp verzija")
        print("5. TTaxi_ULTRA_SHARP.bmp - Ultra sharp BMP")
        
    except Exception as e:
        print(f"❌ Greška: {e}")

if __name__ == "__main__":
    convert_ttaxi_icon()
