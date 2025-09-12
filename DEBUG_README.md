# BDO Fishing - Control de Debug

## Configuración de Debug

El programa incluye un sistema de control de debug que permite habilitar o deshabilitar la generación de imágenes de debug.

### Archivo de Configuración

Edita el archivo `config.py` para cambiar la configuración:

```python
# Control de debug
DEBUG_MODE = False  # Cambiar a True para habilitar guardado de imágenes de debug
```

### Estados del Debug

- **DEBUG_MODE = False** (por defecto): No se generan imágenes de debug
- **DEBUG_MODE = True**: Se generan imágenes de debug en la carpeta `debug_images/`

### Qué se guarda cuando DEBUG_MODE = True

1. **Imágenes de secuencia de teclas** (`utils/key_sequence.py`):
   - `{timestamp}_captured_original.png`: Captura de la región donde aparecen las teclas
   - `{timestamp}_template_result.txt`: Log detallado del proceso de detección

2. **Imágenes de detección de peces** (`utils/loot_window.py`):
   - `{timestamp}_fish_region.png`: Región donde se detecta el color del pez
   - `{timestamp}_green_mask.png`: Máscara de color verde detectada

### Interfaz Gráfica

La ventana principal muestra el estado actual del debug:
- **Verde "HABILITADO"**: Debug activado
- **Rojo "DESHABILITADO"**: Debug desactivado

### Recomendaciones

- Mantén `DEBUG_MODE = False` durante el uso normal para mejor rendimiento
- Activa `DEBUG_MODE = True` solo cuando necesites diagnosticar problemas
- Las imágenes de debug pueden ocupar mucho espacio en disco si se ejecuta por mucho tiempo
