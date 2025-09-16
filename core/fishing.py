import time
import random
from time import sleep
from tkinter import messagebox
import pyautogui
pyautogui.useImageNotFoundException(False)
pyautogui.FAILSAFE = False
from utils.open_game import cambiar_a_black_desert
from utils.key_sequence import detect_and_press_sequence
from utils.loot_window import detect_loot_window, move_mouse_human_like, detect_fish_type
from utils.spacebar_detection import detect_spacebar
import keyboard



def main_pescar():
    """
    Función que simula el proceso de pesca - se repite indefinidamente
    """
    print("🎣 ¡Iniciando pesca automática infinita!")
    print("⚠️ Presiona Ctrl+C para detener el programa")
    
    # Cambiar a la ventana de Black Desert Online (solo una vez al inicio)
    if cambiar_a_black_desert():
        print("✅ Ventana de Black Desert activada")
        time.sleep(2)
    else:
        print("❌ No se pudo encontrar la ventana de Black Desert Online")
        return
    
    ciclo = 1
    
    while True:
        try:
            print(f"\n🔄 === CICLO DE PESCA #{ciclo} ===")
            
            # Detectar SpaceBar en la región específica cada 3 segundos hasta encontrarlo
            spacebar_detectado = False
            while not spacebar_detectado:
                if detect_spacebar():
                    time.sleep(2)
                    keyboard.press_and_release('space')
                    
                    time.sleep(1.6)
                    keyboard.press_and_release('space')
                    
                    # Detectar y presionar secuencia de teclas
                    time.sleep(2)
                    sequence_length = detect_and_press_sequence()
                    if sequence_length:
                        print(f"✅ Secuencia de teclas completada ({sequence_length} letras)")
                    else:
                        print("❌ Error en secuencia de teclas")
                        sequence_length = 0
                    
                    # Presionar ESC con intervalos aleatorios hasta encontrar menu_1.png en la región específica
                    menu_encontrado = False
                    while not menu_encontrado:
                        keyboard.press_and_release('esc')
                        # Intervalo aleatorio entre 0.3 y 0.7 segundos
                        intervalo = random.uniform(0.3, 0.7)
                        time.sleep(intervalo)
                        
                        # Buscar menu_1.png en la región específica (476, 115, 616, 175)
                        try:
                            menu_location = pyautogui.locateOnScreen("assets/Menu/menu_1.png", 
                                                                   region=(476, 115, 616, 175))
                            if menu_location:
                                print("✅ Menu encontrado en la región específica")
                                menu_encontrado = True
                                # Esperar 0.2 segundos y pulsar ESC de nuevo
                                time.sleep(0.2)
                                keyboard.press_and_release('esc')
                        except pyautogui.ImageNotFoundException:
                            continue
                    
                    if detect_loot_window():
                        print("✅ Ventana de loot encontrada")
                        
                        # Mover ratón a la posición especificada con trayectoria humana
                        move_mouse_human_like(1433, 535)
                        
                        # Detectar tipo de pez y actuar según corresponda
                        detect_fish_type(sequence_length)
                    else:
                        print("❌ No se encontró ventana de loot")
                    
                    spacebar_detectado = True
                else:
                    time.sleep(3)
            
            print(f"✅ Ciclo #{ciclo} completado")
            ciclo += 1
            
            # Pequeña pausa entre ciclos
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n🛑 ¡Pesca detenida por el usuario!")
            print(f"📊 Total de ciclos completados: {ciclo - 1}")
            break
        except Exception as e:
            print(f"❌ Error en ciclo #{ciclo}: {e}")
            time.sleep(5)
            continue
    
    print("🏁 Programa de pesca terminado")
