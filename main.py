import tkinter as tk
from tkinter import messagebox
import threading
from core.fishing import main_pescar
from config import DEBUG_MODE


def pescar_thread():
    """
    Ejecuta la función pescar en un hilo separado para evitar bloquear la interfaz
    """
    thread = threading.Thread(target=main_pescar)
    thread.daemon = True
    thread.start()


def salir():
    """
    Función para cerrar la aplicación
    """
    root.destroy()


# Crear la ventana principal
root = tk.Tk()
root.title("BDO Fishing")
root.geometry("300x180")
root.resizable(False, False)

# Mostrar estado del debug
debug_status = "HABILITADO" if DEBUG_MODE else "DESHABILITADO"
debug_color = "#4CAF50" if DEBUG_MODE else "#f44336"

# Centrar la ventana en la pantalla
root.eval("tk::PlaceWindow . center")

# Crear etiqueta de estado del debug
lbl_debug = tk.Label(
    root,
    text=f"Debug: {debug_status}",
    fg=debug_color,
    font=("Arial", 10, "bold")
)

# Crear los botones
btn_iniciar = tk.Button(
    root,
    text="Iniciar Pesca",
    command=pescar_thread,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 12, "bold"),
    width=15,
    height=2,
)

btn_salir = tk.Button(
    root,
    text="Salir",
    command=salir,
    bg="#f44336",
    fg="white",
    font=("Arial", 12, "bold"),
    width=15,
    height=2,
)

# Posicionar los elementos
lbl_debug.pack(pady=10)
btn_iniciar.pack(pady=10)
btn_salir.pack(pady=10)

# Configurar el evento de cierre de ventana
root.protocol("WM_DELETE_WINDOW", salir)

# Iniciar el bucle principal
if __name__ == "__main__":
    root.mainloop()
