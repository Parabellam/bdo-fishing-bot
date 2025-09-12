import time
import pygetwindow as gw


def cambiar_a_black_desert():
    """
    Cambia a la ventana de Black Desert Online si está abierta
    """
    print("Buscando ventana de Black Desert Online...")

    # Buscar ventanas que contengan "Black Desert" en el título
    windows = gw.getWindowsWithTitle("Black Desert")

    if not windows:
        # Intentar con otros nombres posibles
        windows = gw.getWindowsWithTitle("BDO")
        if not windows:
            windows = gw.getWindowsWithTitle("BlackDesert")

    if windows:
        try:
            # Tomar la primera ventana encontrada
            bdo_window = windows[0]
            print(f"Encontrada ventana: {bdo_window.title}")

            # Activar la ventana
            bdo_window.activate()
            print("Ventana de Black Desert Online activada")

            # Esperar un momento para que la ventana se active completamente
            time.sleep(1)
            return True

        except Exception as e:
            print(f"Error al activar la ventana: {e}")
            return False
    else:
        print("No se encontró ninguna ventana de Black Desert Online abierta")
        return False
