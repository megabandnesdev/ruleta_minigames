# Game Configuration Constants
ANCHO = 1280
ALTO = 720

# Colors
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Game options
OPCIONES = [
    "Mortal Kombat 2",
    "Mario Bros",
    "Street Fighter 2",
    "Battletoads",
    "Super Tennis",
    "The Simpsons"
]
SINGLEPLAYER_OPTIONS = [
    "MM1 Bomb Man",
    "MM2 Metal Man",
    "MM3 Top Man",
    "MM4 Toad Man",
    "MM5 Star Man",
    "MM6 Flame Man",
]
MULTIPLAYER_OPTIONS = [
    "Mortal Kombat 2",
    "Mario Bros",
    "Street Fighter 2",
    "Battletoads",
    "Super Tennis",
    "The Simpsons",
    "Megaman VS"
]
# Timing constants
TIEMPO_MOSTRAR_RESULTADO = 6000
TIEMPO_ESPERA = 5000
TIEMPO_DOBLE_PULSACION = 500

# Image settings
TAMANO_IMAGEN = 180

# Single player selection timing
TIEMPO_SELECCION_SINGLEPLAYER = 5000  # 5 seconds for random selection
TIEMPO_MOSTRAR_OPCION = 200  # Time to show each option during cycling


# Roulette settings
RADIO_BASE = ANCHO // 4
VELOCIDAD_INICIAL = 0.2
FACTOR_FRICCION = 0.98
VELOCIDAD_MINIMA = 0.002
VELOCIDAD_FORZADA = 0.0009
