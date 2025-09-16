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
        # Generar posición aleatoria en la pantalla
        screen_width, screen_height = pyautogui.size()
        random_x = random.randint(100, screen_width - 100)
        random_y = random.randint(100, screen_height - 100)
        
        # Mover a posición aleatoria con trayectoria humana variable
        move_human_trajectory(random_x, random_y, random.uniform(1, 2))
        
        # Presionar Ctrl para activar el mouse del juego
        keyboard.press_and_release('ctrl')
        time.sleep(random.uniform(0.5, 0.8))  # Esperar un poco después de presionar Ctrl
        
        # Mover con trayectoria humana usando easeOutQuad
        pyautogui.moveTo(target_x, target_y, duration=random.uniform(0.4, 0.8), tween=pyautogui.easeOutQuad)
        
        return True
        
    except Exception as e:
        print(f"❌ Error moviendo ratón: {e}")
        return False

def move_human_trajectory(target_x, target_y, total_duration):
    """
    Mueve el cursor con una trayectoria más humana usando múltiples puntos intermedios
    con velocidades variables
    """
    try:
        # Obtener tamaño de pantalla y posición actual del cursor
        screen_width, screen_height = pyautogui.size()
        current_x, current_y = pyautogui.position()
        
        # Calcular distancia total
        distance = ((target_x - current_x) ** 2 + (target_y - current_y) ** 2) ** 0.5
        
        # Si la distancia es muy pequeña, mover directamente
        if distance < 50:
            pyautogui.moveTo(target_x, target_y, duration=total_duration, tween=pyautogui.easeOutQuad)
            return
        
        # Generar 2-4 puntos intermedios aleatorios
        num_points = random.randint(2, 4)
        intermediate_points = []
        
        for i in range(num_points):
            # Crear puntos intermedios con desviación aleatoria
            progress = (i + 1) / (num_points + 1)
            
            # Posición base en línea recta
            base_x = current_x + (target_x - current_x) * progress
            base_y = current_y + (target_y - current_y) * progress
            
            # Agregar desviación aleatoria (más pequeña para puntos más cercanos al objetivo)
            deviation_factor = (1 - progress) * 0.3  # Menos desviación cerca del objetivo
            max_deviation = distance * deviation_factor
            
            offset_x = random.uniform(-max_deviation, max_deviation)
            offset_y = random.uniform(-max_deviation, max_deviation)
            
            intermediate_x = int(base_x + offset_x)
            intermediate_y = int(base_y + offset_y)
            
            # Asegurar que esté dentro de la pantalla
            intermediate_x = max(50, min(screen_width - 50, intermediate_x))
            intermediate_y = max(50, min(screen_height - 50, intermediate_y))
            
            intermediate_points.append((intermediate_x, intermediate_y))
        
        # Dividir el tiempo total entre los segmentos con variación
        segment_times = []
        remaining_time = total_duration
        
        for i in range(len(intermediate_points) + 1):
            if i == len(intermediate_points):  # Último segmento
                segment_times.append(remaining_time)
            else:
                # Tiempo variable para cada segmento (más rápido al inicio, más lento al final)
                speed_factor = random.uniform(0.7, 1.3)  # Variación de velocidad
                segment_time = (remaining_time / (len(intermediate_points) + 1)) * speed_factor
                segment_time = max(0.1, min(segment_time, remaining_time * 0.8))  # Limitar tiempo
                segment_times.append(segment_time)
                remaining_time -= segment_time
        
        # Ejecutar los movimientos
        current_pos_x, current_pos_y = current_x, current_y
        
        for i, (next_x, next_y) in enumerate(intermediate_points + [(target_x, target_y)]):
            segment_duration = segment_times[i]
            
            # Elegir tipo de animación aleatorio para cada segmento
            tweens = [pyautogui.easeInQuad, pyautogui.easeOutQuad, pyautogui.easeInOutQuad, pyautogui.easeInCubic, pyautogui.easeOutCubic]
            selected_tween = random.choice(tweens)
            
            pyautogui.moveTo(next_x, next_y, duration=segment_duration, tween=selected_tween)
            current_pos_x, current_pos_y = next_x, next_y
            
            # Pequeña pausa aleatoria entre segmentos (simula micro-pausas humanas)
            if i < len(intermediate_points):
                micro_pause = random.uniform(0.01, 0.05)
                time.sleep(micro_pause)
        
    except Exception as e:
        print(f"❌ Error en trayectoria humana: {e}")
        # Fallback a movimiento simple
        pyautogui.moveTo(target_x, target_y, duration=total_duration, tween=pyautogui.easeOutQuad)

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

def detect_fish_type(sequence_length=0):
    """
    Detecta el tipo de pez buscando primero las imágenes color-zone_ en fish_region,
    luego analiza el color verde solo en esa región específica encontrada.
    Si sequence_length >= 7, salta la evaluación del color verde y recoge directamente.
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
        
        # Analizar píxeles verdes usando rangos específicos de color
        # Colores verdes específicos detectados en el juego:
        # #445c31 (68,92,49), #5c6c4c (92,108,76), #4c5834 (76,88,52)
        # #3a4a25 (58,74,37), #7c8c5e (124,140,94), #515b3d (81,91,61)
        # #646c4b (100,108,75)
        
        # Separar canales RGB
        r_channel = color_zone_img[:, :, 0]  # Canal rojo
        g_channel = color_zone_img[:, :, 1]  # Canal verde
        b_channel = color_zone_img[:, :, 2]  # Canal azul
        
        # Crear máscara para píxeles verdes usando rangos específicos
        green_mask = np.zeros_like(g_channel, dtype=bool)
        
        # Definir rangos de color verde específicos con tolerancia ±15
        green_ranges = [
            # #445c31 (68,92,49) ±15
            ((53, 83), (77, 107), (34, 64)),
            # #5c6c4c (92,108,76) ±15  
            ((77, 107), (93, 123), (61, 91)),
            # #4c5834 (76,88,52) ±15
            ((61, 91), (73, 103), (37, 67)),
            # #3a4a25 (58,74,37) ±15
            ((43, 73), (59, 89), (22, 52)),
            # #7c8c5e (124,140,94) ±15
            ((109, 139), (125, 155), (79, 109)),
            # #515b3d (81,91,61) ±15
            ((66, 96), (76, 106), (46, 76)),
            # #646c4b (100,108,75) ±15
            ((85, 115), (93, 123), (60, 90))
        ]
        
        # Aplicar cada rango de color verde
        for r_range, g_range, b_range in green_ranges:
            range_mask = (
                (r_channel >= r_range[0]) & (r_channel <= r_range[1]) &
                (g_channel >= g_range[0]) & (g_channel <= g_range[1]) &
                (b_channel >= b_range[0]) & (b_channel <= b_range[1])
            )
            green_mask |= range_mask
        
        # Contar píxeles verdes solo en la región color-zone
        green_pixels = np.sum(green_mask)
        total_pixels = zone_width * zone_height
        
        # Calcular porcentaje de píxeles verdes
        green_percentage = (green_pixels / total_pixels) * 100
        
        # Debug: mostrar información detallada
        print(f"🔍 Análisis de color verde:")
        print(f"   - Píxeles verdes detectados: {green_pixels} ({green_percentage:.1f}%)")
        
        
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
        
        # Si la secuencia tiene 7 o más letras, saltar evaluación de color verde y recoger directamente
        if sequence_length >= 7:
            print(f"🎯 Secuencia larga detectada ({sequence_length} letras) - recogiendo directamente")
            keyboard.press_and_release('r')
            time.sleep(random.uniform(0.4, 0.9))
            keyboard.press_and_release('space')
            return False
        
        # Si hay más del 40% de píxeles verdes, consideramos que es un pez verde
        if green_percentage > 40.0:
            print("✅ Pez verde detectado - descartando")
            time.sleep(random.uniform(0.1, 0.3))
            keyboard.press_and_release('space')
            time.sleep(random.uniform(0.3, 0.8))
            keyboard.press_and_release('space')
            return True
        else:
            print("❌ Pez no verde - recogiendo")
            keyboard.press_and_release('r')
            time.sleep(random.uniform(0.4, 0.9))
            keyboard.press_and_release('space')
            return False
            
    except Exception as e:
        print(f"❌ Error detectando tipo de pez: {e}")
        keyboard.press_and_release('r')
        return False

