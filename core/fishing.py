import time
from time import sleep
from tkinter import messagebox
import pyautogui
pyautogui.useImageNotFoundException(False)
pyautogui.FAILSAFE = False
from utils.load_images import load_images_from_path
from utils.open_game import cambiar_a_black_desert
from utils.key_sequence import detect_and_press_sequence
from utils.loot_window import detect_loot_window, move_mouse_human_like, detect_fish_type
import keyboard

SPACEBAR_PATH = "assets/SpaceBar"

spacebar_imgs = load_images_from_path(SPACEBAR_PATH, "SpaceBar_")

CONFIDENCE = 0.95
MAX_ATTEMPTS = 10
region = (886, 324, 148, 46)

def detect_spacebar():
    """
    Detecta SpaceBar en la región específica calculada
    """
    count = 0
    while count < MAX_ATTEMPTS:
        for img_name, image_path in spacebar_imgs.items():
            try:
                # Intentar sin confidence primero
                location = pyautogui.locateOnScreen(image_path, region=region)
                count += 1
                if location:
                    print(f"SpaceBar encontrado: {img_name}")
                    return True
            except Exception as e:
                print(f"Error detectando {img_name}: {e}")
                count += 1
                continue
    print("SpaceBar no encontrado")
    return False


def main_pescar():
    """
    Función que simula el proceso de pesca - se repite indefinidamente
    """
    print("🎣 ¡Iniciando pesca automática infinita!")
    print("⚠️ Presiona Ctrl+C para detener el programa")
    
    # Cambiar a la ventana de Black Desert Online (solo una vez al inicio)
    print("🖥️ Cambiando a la ventana de Black Desert Online...")
    if cambiar_a_black_desert():
        print("✅ Ventana de Black Desert activada")
        print("Esperando 2 segundos para que la ventana se active completamente...")
        time.sleep(2)
    else:
        print("❌ No se pudo encontrar la ventana de Black Desert Online")
        print("Asegúrate de que el juego esté abierto y visible")
        return
    
    ciclo = 1
    
    while True:
        try:
            print(f"\n🔄 === CICLO DE PESCA #{ciclo} ===")
            
            # Detectar SpaceBar en la región específica cada 3 segundos hasta encontrarlo
            spacebar_detectado = False
            while not spacebar_detectado:
                if detect_spacebar():
                    print("SpaceBar detectado, esperando 2 segundos...")
                    time.sleep(2)  # Esperar 2 segundos como especificaste
                    keyboard.press_and_release('space')  # Presionar espacio
                    
                    print("Esperando 1.6 segundos...")
                    time.sleep(1.6)  # Esperar 1.6 segundos
                    keyboard.press_and_release('space')  # Presionar espacio nuevamente
                    
                    # Detectar y presionar secuencia de teclas
                    print("Detectando secuencia de teclas...")
                    time.sleep(3)
                    if detect_and_press_sequence():
                        print("✅ Secuencia de teclas completada exitosamente")
                    else:
                        print("❌ No se pudo completar la secuencia de teclas")
                    
                    # Esperar un poco y luego detectar ventana de loot
                    print("Esperando 2 segundos para que aparezca la ventana de loot...")
                    time.sleep(2)
                    
                    if detect_loot_window():
                        print("✅ Ventana de loot encontrada")
                        
                        # Mover ratón a la posición especificada con trayectoria humana
                        move_mouse_human_like(1433, 535)
                        
                        # Detectar tipo de pez y actuar según corresponda
                        detect_fish_type()
                    else:
                        print("❌ No se pudo encontrar la ventana de loot")
                    
                    spacebar_detectado = True
                else:
                    print("❌ SpaceBar no detectado, esperando 3 segundos antes del siguiente intento...")
                    time.sleep(3)  # Esperar 3 segundos antes de reintentar
            
            print(f"✅ Ciclo #{ciclo} completado")
            ciclo += 1
            
            # Pequeña pausa entre ciclos
            print("⏳ Esperando 10 segundos antes del siguiente ciclo...")
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n🛑 ¡Pesca detenida por el usuario!")
            print(f"📊 Total de ciclos completados: {ciclo - 1}")
            break
        except Exception as e:
            print(f"❌ Error en ciclo #{ciclo}: {e}")
            print("⏳ Esperando 5 segundos antes de reintentar...")
            time.sleep(5)
            continue
    
    print("🏁 Programa de pesca terminado")
