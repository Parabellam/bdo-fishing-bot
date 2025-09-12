import pyautogui
import os
import random
import time
import keyboard
import cv2
import numpy as np
from config import DEBUG_MODE

# Configuración de la ventana de loot
LOOT_WINDOW_PATH = "assets/Loot"
LOOT_WINDOW_REGION = (1462, 615, 205, 71)  # x, y, width, height

def move_mouse_human_like(target_x, target_y):
    """
    Mueve el ratón a la posición especificada con trayectoria humana y tiempo aleatorio
    """
    try:
        time.sleep(2.7)
        
        # Presionar Ctrl para activar el mouse del juego
        keyboard.press_and_release('ctrl')
        time.sleep(1)  # Esperar un poco después de presionar Ctrl
        
        # Generar tiempo aleatorio entre 0.5 y 1.2 segundos
        duration = random.uniform(0.4, 0.8)
        
        # Mover con trayectoria humana usando easeOutQuad
        pyautogui.moveTo(target_x, target_y, duration=duration, tween=pyautogui.easeOutQuad)
        
        return True
        
    except Exception as e:
        print(f"❌ Error moviendo ratón: {e}")
        return False

def detect_loot_window():
    """
    Detecta la ventana de loot en la región específica usando pyautogui
    """
    try:
        # Buscar la imagen de loot en la región específica
        loot_image_path = os.path.join(LOOT_WINDOW_PATH, "loot-window_1.png")
        
        if not os.path.exists(loot_image_path):
            print(f"❌ Imagen de loot no encontrada: {loot_image_path}")
            return False
        
        # Buscar la imagen en la región específica
        location = pyautogui.locateOnScreen(loot_image_path, region=LOOT_WINDOW_REGION, confidence=0.8)
        
        if location:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error detectando ventana de loot: {e}")
        return False

def detect_fish_type():
    """
    Detecta el tipo de pez buscando primero las imágenes color-zone_ en fish_region,
    luego analiza el color verde solo en esa región específica encontrada
    """
    try:
        time.sleep(1.5)
        # Región donde buscar el pez: (988, 382, 656, 326)
        fish_region = (988, 382, 656, 326)
        
        # Capturar la región específica
        screenshot = pyautogui.screenshot(region=fish_region)
        
        # Convertir a array de numpy para OpenCV
        img_array = np.array(screenshot)
        
        # Primero buscar las imágenes exception_ en la región del pez
        exception_found = False
        
        # Buscar dinámicamente todas las imágenes exception_ disponibles
        i = 1
        while True:
            exception_path = os.path.join(LOOT_WINDOW_PATH, f"exception_{i}.png")
            
            if not os.path.exists(exception_path):
                break  # No hay más imágenes exception_
                
            # Buscar la imagen en la región del pez
            location = pyautogui.locateOnScreen(exception_path, region=fish_region, confidence=0.8)
            
            if location:
                print(f"⚠️ Exception_{i}.png encontrada - presionando R")
                keyboard.press_and_release('r')
                time.sleep(1)
                keyboard.press_and_release('space')
                return False
            
            i += 1
        
        # Si no se encontró ninguna excepción, buscar las imágenes color-zone_
        color_zone_found = False
        color_zone_location = None
        
        # Buscar dinámicamente todas las imágenes color-zone_ disponibles
        i = 1
        while True:
            color_zone_path = os.path.join(LOOT_WINDOW_PATH, f"color-zone_{i}.png")
            
            if not os.path.exists(color_zone_path):
                break  # No hay más imágenes color-zone_
                
            # Buscar la imagen en la región del pez
            location = pyautogui.locateOnScreen(color_zone_path, region=fish_region, confidence=0.8)
            
            if location:
                color_zone_found = True
                color_zone_location = location
                break
            
            i += 1
        
        if not color_zone_found:
            print("❌ No se encontró color-zone - presionando R por defecto")
            keyboard.press_and_release('r')
            return False
        
        # Convertir la ubicación encontrada a coordenadas relativas dentro de fish_region
        # pyautogui.locateOnScreen devuelve (left, top, width, height)
        zone_x = color_zone_location.left - fish_region[0]  # Coordenada X relativa
        zone_y = color_zone_location.top - fish_region[1]  # Coordenada Y relativa
        zone_width = color_zone_location.width
        zone_height = color_zone_location.height
        
        
        # Extraer solo la región de color-zone de la imagen
        color_zone_img = img_array[zone_y:zone_y+zone_height, zone_x:zone_x+zone_width]
        
        # Analizar píxeles verdes directamente en RGB sin filtros
        # Definir rangos de color verde en RGB
        # Verde: R < 150, G > 100, B < 150 (píxeles con más verde que rojo y azul)
        
        # Separar canales RGB
        r_channel = color_zone_img[:, :, 0]  # Canal rojo
        g_channel = color_zone_img[:, :, 1]  # Canal verde
        b_channel = color_zone_img[:, :, 2]  # Canal azul
        
        # Crear máscara para píxeles verdes: G > R y G > B y G > umbral_mínimo
        green_mask = (g_channel > r_channel) & (g_channel > b_channel) & (g_channel > 80)
        
        # Contar píxeles verdes solo en la región color-zone
        green_pixels = np.sum(green_mask)
        total_pixels = zone_width * zone_height
        
        # Calcular porcentaje de píxeles verdes
        green_percentage = (green_pixels / total_pixels) * 100
        
        
        # Guardar imagen para debug solo si está habilitado
        if DEBUG_MODE:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            os.makedirs("debug_images", exist_ok=True)
            # Convertir RGB a BGR para guardar correctamente
            color_zone_bgr = cv2.cvtColor(color_zone_img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"debug_images/{timestamp}_evaluating.png", color_zone_bgr)
        
        # Desactivar el mouse del juego
        keyboard.press_and_release('ctrl')
        time.sleep(0.5)
        
        # Si hay más del 30% de píxeles verdes, consideramos que es un pez verde
        if green_percentage > 30.0:
            print("✅ Pez verde detectado - descartando")
            time.sleep(1)
            keyboard.press_and_release('space')
            return True
        else:
            print("❌ Pez no verde - recogiendo")
            keyboard.press_and_release('r')
            time.sleep(1)
            keyboard.press_and_release('space')
            return False
            
    except Exception as e:
        print(f"❌ Error detectando tipo de pez: {e}")
        keyboard.press_and_release('r')
        return False

