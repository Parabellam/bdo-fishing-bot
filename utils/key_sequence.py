import time
import keyboard
import pyautogui
import cv2
import numpy as np
import os
import random
from config import DEBUG_MODE

# Configuración de plantillas de letras
TEMPLATE_DIR = "assets/Binds"
TEMPLATE_FILES = {
    'A': ['A_1.png', 'A_3.png', 'A_4.png'],
    'D': ['D_1.png', 'D_3.png'], 
    'S': ['S_1.png', 'S_3.png', 'S_4.png', 'S_5.png'],
    'W': ['W_1.png', 'W_3.png']
}

# Cargar plantillas de letras
def load_templates():
    """
    Carga todas las plantillas de letras desde el directorio assets/Binds
    """
    templates = {}
    
    for letter, files in TEMPLATE_FILES.items():
        templates[letter] = []
        for file in files:
            template_path = os.path.join(TEMPLATE_DIR, file)
            if os.path.exists(template_path):
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    templates[letter].append(template)
                else:
                    print(f"❌ Error cargando plantilla: {file}")
            else:
                print(f"❌ Plantilla no encontrada: {template_path}")
    
    return templates

# Cargar plantillas al importar el módulo
TEMPLATES = load_templates()

# Región específica donde aparecen las secuencias de teclas
# Calculada con tu script: (766, 330, 1166, 417)
SEQUENCE_REGION = (766, 330, 400, 87)  # x, y, width, height 

# Mapeo de teclas WASD
KEY_MAPPING = {
    'A': 'a',
    'S': 's', 
    'D': 'd',
    'W': 'w'
}

def capture_sequence_region():
    """
    Captura la región específica donde aparecen las secuencias de teclas
    """
    try:
        # Capturar pantalla
        screenshot = pyautogui.screenshot(region=SEQUENCE_REGION)
        
        # Convertir a array de numpy para OpenCV
        img_array = np.array(screenshot)
        
        # Convertir de RGB a BGR (OpenCV usa BGR)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_bgr
        
    except Exception as e:
        print(f"❌ Error capturando región: {e}")
        return None

def find_template_in_image(image, template, threshold=0.8):
    """
    Busca una plantilla en la imagen usando template matching
    Ignora el color y solo compara la forma/estructura
    """
    try:
        # Convertir ambas imágenes a escala de grises para ignorar el color
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Realizar template matching en escala de grises
        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        
        # Encontrar todas las ubicaciones donde la coincidencia supera el threshold
        locations = np.where(result >= threshold)
        
        matches = []
        for pt in zip(*locations[::-1]):  # Cambiar x,y por y,x
            confidence = result[pt[1], pt[0]]
            matches.append((pt[0], pt[1], confidence))
        
        return matches
        
    except Exception as e:
        print(f"❌ Error en template matching: {e}")
        return []

def find_all_letters_in_image(image, threshold=0.8):
    """
    Busca todas las letras WASD en la imagen usando template matching
    Retorna una lista de tuplas (letra, x, y, confianza) ordenadas por posición x
    """
    all_matches = []
    
    for letter, templates in TEMPLATES.items():
        for template in templates:
            matches = find_template_in_image(image, template, threshold)
            for x, y, confidence in matches:
                all_matches.append((letter, x, y, confidence))
    
    # Ordenar por posición x (de izquierda a derecha)
    all_matches.sort(key=lambda match: match[1])
    
    return all_matches

def extract_sequence_with_templates(image, max_letters=10, threshold=0.8):
    """
    Extrae la secuencia de teclas usando detección por plantillas
    Busca de izquierda a derecha, omitiendo región izquierda después de cada detección
    """
    try:
        import datetime
        
        # Guardar información de debug solo si está habilitado
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        if DEBUG_MODE:
            os.makedirs("debug_images", exist_ok=True)
        
        sequence = []
        excluded_regions = []  # Lista de regiones excluidas (x_start, x_end)
        
        if DEBUG_MODE:
            with open(f"debug_images/{timestamp}_template_result.txt", "w", encoding="utf-8") as f:
                f.write(f"Proceso de detección paso a paso:\n")
            
                # Buscar letras iterativamente, excluyendo regiones ya procesadas
                for step in range(max_letters):
                    f.write(f"\n--- Paso {step + 1} ---\n")
                    
                    # Buscar todas las letras en la imagen
                    all_matches = find_all_letters_in_image(image, threshold)
                    
                    if not all_matches:
                        f.write("No se encontraron más letras\n")
                        break
                    
                    # Filtrar coincidencias que no estén en regiones excluidas
                    valid_matches = []
                    for letter, x, y, conf in all_matches:
                        is_excluded = False
                        for x_start, x_end in excluded_regions:
                            if x_start <= x <= x_end:
                                is_excluded = True
                                break
                        
                        if not is_excluded:
                            valid_matches.append((letter, x, y, conf))
                    
                    if not valid_matches:
                        f.write("Todas las coincidencias están en regiones excluidas\n")
                        break
                    
                    # Ordenar por posición x y tomar la primera (más a la izquierda)
                    valid_matches.sort(key=lambda match: match[1])
                    best_match = valid_matches[0]
                    letter, x, y, confidence = best_match
                    
                    f.write(f"Mejor coincidencia: {letter} en ({x}, {y}) con confianza {confidence:.3f}\n")
                    f.write(f"Coincidencias válidas encontradas: {len(valid_matches)}\n")
                    
                    # Agregar a la secuencia
                    sequence.append(letter)
                    
                    # Calcular región a excluir: desde 1 pixel a la derecha hacia toda la izquierda
                    # Asumimos que cada letra tiene aproximadamente 30-40 píxeles de ancho
                    letter_width = 40  # Ajustar según el tamaño real de las letras
                    exclude_start = 0  # Desde el inicio de la imagen
                    exclude_end = x + 10  # Hasta 10 pixel a la derecha de la letra encontrada
                    
                    excluded_regions.append((exclude_start, exclude_end))
                    f.write(f"Región excluida: x={exclude_start} a x={exclude_end}\n")
                    
                    # Mostrar todas las coincidencias encontradas en este paso
                    f.write(f"Todas las coincidencias del paso:\n")
                    for letter, x, y, conf in all_matches:
                        f.write(f"  {letter} en ({x}, {y}) con confianza {conf:.3f}\n")
        
        # Buscar letras iterativamente, excluyendo regiones ya procesadas (sin debug)
        for step in range(max_letters):
            # Buscar todas las letras en la imagen
            all_matches = find_all_letters_in_image(image, threshold)
            
            if not all_matches:
                break
            
            # Filtrar coincidencias que no estén en regiones excluidas
            valid_matches = []
            for letter, x, y, conf in all_matches:
                is_excluded = False
                for x_start, x_end in excluded_regions:
                    if x_start <= x <= x_end:
                        is_excluded = True
                        break
                
                if not is_excluded:
                    valid_matches.append((letter, x, y, conf))
            
            if not valid_matches:
                break
            
            # Ordenar por posición x y tomar la primera (más a la izquierda)
            valid_matches.sort(key=lambda match: match[1])
            best_match = valid_matches[0]
            letter, x, y, confidence = best_match
            
            # Agregar a la secuencia
            sequence.append(letter)
            
            # Calcular región a excluir: desde 1 pixel a la derecha hacia toda la izquierda
            # Asumimos que cada letra tiene aproximadamente 30-40 píxeles de ancho
            letter_width = 40  # Ajustar según el tamaño real de las letras
            exclude_start = 0  # Desde el inicio de la imagen
            exclude_end = x + 10  # Hasta 10 pixel a la derecha de la letra encontrada
            
            excluded_regions.append((exclude_start, exclude_end))
        
        # Guardar secuencia final solo si debug está habilitado
        if DEBUG_MODE:
            with open(f"debug_images/{timestamp}_template_result.txt", "a", encoding="utf-8") as f:
                f.write(f"\nSecuencia final: {sequence}\n")
                f.write(f"Regiones excluidas: {excluded_regions}\n")
        
        return sequence
        
    except Exception as e:
        print(f"❌ Error extrayendo secuencia con plantillas: {e}")
        return []

def detect_key_sequence():
    """
    Detecta la secuencia de teclas usando detección por plantillas en la región específica
    """
    try:
        # Capturar la región
        image = capture_sequence_region()
        if image is None:
            return None
        
        # Guardar la imagen capturada para debug solo si está habilitado
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        if DEBUG_MODE:
            os.makedirs("debug_images", exist_ok=True)
            cv2.imwrite(f"debug_images/{timestamp}_captured_original.png", image)
        
        # Extraer secuencia con plantillas
        sequence = extract_sequence_with_templates(image, max_letters=10, threshold=0.8)
        
        if sequence:
            return sequence
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error detectando secuencia: {e}")
        return None

def press_key_sequence(sequence):
    """
    Presiona la secuencia de teclas detectada
    Cada 3 presiones, espera entre 0.5 y 0.9 segundos
    """
    if not sequence:
        print("❌ No hay secuencia para presionar")
        return False
    
    try:
        for i, key in enumerate(sequence):
            if key in KEY_MAPPING:
                keyboard.press_and_release(KEY_MAPPING[key])
                
                # Cada 3 presiones (índices 2, 5, 8, etc.), esperar más tiempo
                if (i + 1) % 3 == 0:
                    time.sleep(random.uniform(0.5, 0.9))  # Espera larga cada 3 teclas
                else:
                    time.sleep(random.uniform(0.1, 0.3))  # Espera normal entre teclas
            else:
                print(f"  ❌ Tecla no reconocida: {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error presionando secuencia: {e}")
        return False

def detect_any_letter_in_sequence():
    """
    Detecta si existe alguna letra de la secuencia en la región específica
    Hace múltiples intentos hasta encontrar al menos una letra
    Usa OpenCV para detección en escala de grises
    """
    try:
        max_attempts = 50  # Máximo número de intentos
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"🔍 Intento {attempt}/{max_attempts} - Buscando letras en secuencia...")
            
            # Capturar la región específica
            screenshot = pyautogui.screenshot(region=SEQUENCE_REGION)
            image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Buscar cualquier plantilla en escala de grises
            for letter, templates in TEMPLATES.items():
                for template in templates:
                    # Convertir plantilla a escala de grises si no lo está
                    if len(template.shape) == 3:
                        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                    else:
                        template_gray = template
                    
                    # Realizar template matching en escala de grises
                    result = cv2.matchTemplate(gray_image, template_gray, cv2.TM_CCOEFF_NORMED)
                    
                    # Encontrar ubicaciones donde la coincidencia supera el threshold
                    locations = np.where(result >= 0.7)
                    
                    if len(locations[0]) > 0:
                        print(f"✅ Letra detectada: {letter} (intento {attempt})")
                        return True
            
            # Si no encontró nada, esperar un poco antes del siguiente intento
            if attempt < max_attempts:
                print(f"⏳ Esperando 0.1s antes del siguiente intento...")
                time.sleep(0.1)
        
        print(f"❌ No se detectó ninguna letra después de {max_attempts} intentos")
        return False
        
    except Exception as e:
        print(f"❌ Error detectando letras: {e}")
        return False

def detect_and_press_sequence():
    """
    Detecta y presiona la secuencia de teclas automáticamente
    Retorna la longitud de la secuencia detectada o False si no se detectó nada
    """
    # Primero verificar si hay alguna letra presente
    if not detect_any_letter_in_sequence():
        return False
    
    # Detectar la secuencia completa
    sequence = detect_key_sequence()
    
    if sequence:
        # Presionar la secuencia
        if press_key_sequence(sequence):
            return len(sequence)
        else:
            return False
    else:
        return False
