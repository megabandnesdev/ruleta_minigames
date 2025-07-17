import pygame
import math
import os
import time
import json
from PIL import Image
import cv2
import numpy as np

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO = 1280
ALTO = 720
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Ruleta Retro")

# Variable para controlar el modo de pantalla
modo_pantalla_completa = True

# Función para cambiar el modo de pantalla
def cambiar_modo_pantalla():
    global pantalla, modo_pantalla_completa
    modo_pantalla_completa = not modo_pantalla_completa
    if modo_pantalla_completa:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
        print("Cambiado a pantalla completa")
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        print("Cambiado a modo ventana")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# Lista de opciones
opciones = [
    "Mortal Kombat 2",
    "Mario Bros",
    "Street Fighter 2",
    "Battletoads",
    "Super Tennis",
    "Megaman",
    "Pokemon",
    "The Simpsons"
]

# Variables para el resultado
resultado = ""
mostrar_resultado = False
tiempo_resultado = 0
TIEMPO_MOSTRAR_RESULTADO = 6000
TIEMPO_ESPERA = 5000
esperando_reduccion = False
tiempo_ganador = 0
ganador_actual = None

# Cargar imágenes
TAMANO_IMAGEN = 180
imagenes = []
opciones_disponibles = opciones.copy()
opciones_usadas = []

# --- NUEVA FUNCIÓN PARA RECARGAR IMÁGENES ---
def recargar_imagenes():
    global imagenes
    imagenes = []
    for opcion in opciones_disponibles:
        try:
            ruta = os.path.join('imagenes', f'{opcion}.png')
            ruta_absoluta = os.path.abspath(ruta)
            print(f"Buscando imagen: {ruta_absoluta}")
            if os.path.exists(ruta_absoluta):
                print(f"Imagen encontrada: {ruta_absoluta}")
                imagen = pygame.image.load(ruta_absoluta)
                ancho_original, alto_original = imagen.get_size()
                tamano_ajustado = TAMANO_IMAGEN
                if opcion in ["Mortal Kombat 2", "Super Tennis"]:
                    tamano_ajustado = int(TAMANO_IMAGEN * 0.8)
                if opcion == "Battletoads":
                    tamano_ajustado = int(TAMANO_IMAGEN * 1.2)  # 20% más grande
                factor_escala = min(tamano_ajustado / ancho_original, tamano_ajustado / alto_original)
                nuevo_ancho = int(ancho_original * factor_escala)
                nuevo_alto = int(alto_original * factor_escala)
                imagen = pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))
                imagenes.append(imagen)
            else:
                print(f"Imagen NO encontrada: {ruta_absoluta}")
                superficie = pygame.Surface((TAMANO_IMAGEN, TAMANO_IMAGEN))
                superficie.fill(BLANCO)
                imagenes.append(superficie)
        except Exception as e:
            print(f"Error cargando imagen para {opcion}: {e}")
            superficie = pygame.Surface((TAMANO_IMAGEN, TAMANO_IMAGEN))
            superficie.fill(BLANCO)
            imagenes.append(superficie)

# --- USAR LA FUNCIÓN AL INICIO ---
recargar_imagenes()

# Cargar fondo
ruta_video = os.path.join('imagenes', 'fondo.mp4')
ruta_video_abs = os.path.abspath(ruta_video)
print(f"Buscando video de fondo: {ruta_video_abs}")
try:
    if os.path.exists(ruta_video_abs):
        video_fondo = cv2.VideoCapture(ruta_video_abs)
        ret, frame = video_fondo.read()
        if ret:
            altura, ancho = frame.shape[:2]
            escala = max(ANCHO/ancho, ALTO/altura)
            nuevo_ancho = int(ancho * escala)
            nueva_altura = int(altura * escala)
            x = (ANCHO - nuevo_ancho) // 2
            y = (ALTO - nueva_altura) // 2
            frame = cv2.resize(frame, (nuevo_ancho, nueva_altura))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            fondo_estatico = pygame.surfarray.make_surface(frame)
            fondo_estatico = pygame.transform.rotate(fondo_estatico, -90)
            fondo_estatico = pygame.transform.flip(fondo_estatico, True, False)
        else:
            print("No se pudo leer el primer frame del video, usando fondo gris.")
            fondo_estatico = pygame.Surface((ANCHO, ALTO))
            fondo_estatico.fill((50, 50, 50))
            video_fondo = None
    else:
        print(f"Video fondo.mp4 NO encontrado: {ruta_video_abs}")
        fondo_estatico = pygame.Surface((ANCHO, ALTO))
        fondo_estatico.fill((50, 50, 50))
        video_fondo = None
except Exception as e:
    print(f"Error al cargar el video de fondo: {e}")
    video_fondo = None
    fondo_estatico = pygame.Surface((ANCHO, ALTO))
    fondo_estatico.fill((50, 50, 50))

# Clase para manejar GIFs animados
class AnimatedGIF:
    def __init__(self, ruta, velocidad=1.0, tamano_maximo=None):
        self.pilimage = Image.open(ruta)
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.velocidad = velocidad
        self.tamano_maximo = tamano_maximo
        
        try:
            while True:
                frame = self.pilimage.convert('RGBA')
                pygame_surface = pygame.image.fromstring(
                    frame.tobytes(), frame.size, frame.mode
                ).convert_alpha()
                
                # Escalar manteniendo proporciones si se especifica tamaño máximo
                if self.tamano_maximo:
                    ancho_original, alto_original = pygame_surface.get_size()
                    factor_escala = min(self.tamano_maximo / ancho_original, self.tamano_maximo / alto_original)
                    nuevo_ancho = int(ancho_original * factor_escala)
                    nuevo_alto = int(alto_original * factor_escala)
                    pygame_surface = pygame.transform.scale(pygame_surface, (nuevo_ancho, nuevo_alto))
                
                self.frames.append(pygame_surface)
                self.pilimage.seek(self.pilimage.tell() + 1)
        except EOFError:
            pass
        self.frame_duration = self.pilimage.info.get('duration', 100)
        self.static_frame = self.frames[-1]
    def get_next_frame(self):
        current_time = time.time() * 1000
        if current_time - self.last_update > (self.frame_duration * self.velocidad):
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time
        return self.frames[self.current_frame]
    def get_static_frame(self):
        return self.static_frame

# Cargar GIF del centro
ruta_gif_centro = os.path.join('imagenes', 'gifs', 'centro.gif')
ruta_gif_centro_abs = os.path.abspath(ruta_gif_centro)
print(f"Buscando GIF del centro: {ruta_gif_centro_abs}")
try:
    if os.path.exists(ruta_gif_centro_abs):
        gif_centro = AnimatedGIF(ruta_gif_centro_abs, tamano_maximo=200)  # Tamaño máximo de 200px
    else:
        print(f"GIF centro.gif NO encontrado: {ruta_gif_centro_abs}")
        gif_centro = None
except Exception as e:
    print(f"Error al cargar el GIF del centro: {e}")
    gif_centro = None

# Cargar sonidos
try:
    sonido_giro = pygame.mixer.Sound('sonidos/giro.wav')
    sonido_win = pygame.mixer.Sound('sonidos/win.wav')
except:
    sonido_giro = None
    sonido_win = None

# Cargar sonidos específicos para cada juego
sonidos_victoria = {}
for opcion in opciones_disponibles:
    try:
        ruta = f'sonidos/{opcion.lower().replace(" ", "_")}_win.wav'
        sonidos_victoria[opcion] = pygame.mixer.Sound(ruta)
    except:
        pass

# Variables de la ruleta
centro = (ANCHO // 2, int(ALTO * 0.55))
radio = ANCHO // 4 # Aumentado de 400 a 480 (20% más)
angulo = 0
velocidad = 2
girando = False
normalized_width = ANCHO // 10
normalized_height = ANCHO // 10

# Cargar flecha
try:
    flecha = pygame.image.load('imagenes/Flecha.png')
    flecha = pygame.transform.scale(flecha, (120, 96))  # Aumentado proporcionalmente
except:
    flecha = None

# Cargar logo de Megaman Megamix
try:
    logo_megamix = pygame.image.load('imagenes/Megaband Logo.png')
    # Obtener las dimensiones originales
    ancho_original, alto_original = logo_megamix.get_size()
    # Calcular el factor de escala para mantener proporciones (máximo 600px de ancho) y agrandarlo 10%
    factor_escala = ancho_original / ANCHO /2 # 10% más grande
    nuevo_ancho = int(ancho_original * factor_escala)
    nuevo_alto = int(alto_original * factor_escala)
    # Redimensionar manteniendo proporciones
    logo_megamix = pygame.transform.scale(logo_megamix, (nuevo_ancho, nuevo_alto))
    print("Logo Megaman guardado correctamente")
except Exception as e:
    print(f"Error al cargar megaman megamix: {e}")

# Fuente para el texto
fuente = pygame.font.Font(None, 96)

# Reloj para controlar FPS
reloj = pygame.time.Clock()

# Crear un diccionario para almacenar los GIFs de victoria
gifs_victoria = {}

# Agregar variable para controlar doble espacio
ultima_pulsacion_espacio = 0
TIEMPO_DOBLE_PULSACION = 500  # milisegundos

# Variable para controlar si se debe esperar espacio para salir de la escena de victoria
esperando_espacio_para_salir = False

# Funciones para guardar y cargar el estado
def guardar_estado(opciones_usadas, opciones_disponibles):
    estado = {
        'opciones_usadas': opciones_usadas,
        'opciones_disponibles': opciones_disponibles
    }
    try:
        with open('estado_ruleta.json', 'w') as f:
            json.dump(estado, f)
        print("Estado guardado correctamente")
    except Exception as e:
        print(f"Error al guardar estado: {e}")

def cargar_estado():
    try:
        if os.path.exists('estado_ruleta.json'):
            with open('estado_ruleta.json', 'r') as f:
                estado = json.load(f)
            print("Estado cargado correctamente")
            return estado.get('opciones_usadas', []), estado.get('opciones_disponibles', opciones.copy())
        else:
            print("No se encontró archivo de estado, usando configuración inicial")
            return [], opciones.copy()
    except Exception as e:
        print(f"Error al cargar estado: {e}")
        return [], opciones.copy()

# Cargar estado guardado
opciones_usadas, opciones_disponibles = cargar_estado()

# Loop principal
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                cambiar_modo_pantalla()  # Cambiar entre pantalla completa y ventana
            elif evento.key == pygame.K_r:
                # Función de reset
                print("Reset de la ruleta")
                opciones_disponibles = opciones.copy()
                opciones_usadas = []
                girando = False
                mostrar_resultado = False
                esperando_reduccion = False
                ganador_actual = None
                angulo = 0
                velocidad = 0
                # Guardar estado después del reset
                guardar_estado(opciones_usadas, opciones_disponibles)
                recargar_imagenes()
            elif evento.key == pygame.K_SPACE:
                tiempo_actual = pygame.time.get_ticks()
                if girando and tiempo_actual - ultima_pulsacion_espacio < TIEMPO_DOBLE_PULSACION:
                    # Doble pulsación detectada durante el giro, terminar giro inmediatamente
                    velocidad = 0.0009  # Forzar fin del giro
                elif mostrar_resultado and tiempo_actual - ultima_pulsacion_espacio < TIEMPO_DOBLE_PULSACION:
                    # Doble pulsación detectada durante el resultado, saltar a espera
                    mostrar_resultado = False
                    esperando_espacio_para_salir = False
                    if esperando_reduccion:
                        opciones_usadas.append(ganador_actual)
                        opciones_disponibles.remove(ganador_actual)
                        esperando_reduccion = False
                        ganador_actual = None
                        # Guardar estado después de eliminar un juego con doble espacio
                        guardar_estado(opciones_usadas, opciones_disponibles)
                        recargar_imagenes()
                elif mostrar_resultado:
                    # Pulsación simple durante el resultado, salir de la escena de victoria
                    mostrar_resultado = False
                    esperando_espacio_para_salir = False
                    if esperando_reduccion:
                        opciones_usadas.append(ganador_actual)
                        opciones_disponibles.remove(ganador_actual)
                        esperando_reduccion = False
                        ganador_actual = None
                        # Guardar estado después de eliminar un juego
                        guardar_estado(opciones_usadas, opciones_disponibles)
                        recargar_imagenes()
                elif not girando and not esperando_reduccion and len(opciones_disponibles) > 0:
                    velocidad = 0.2
                    girando = True
                    if sonido_giro:
                        sonido_giro.play()
                ultima_pulsacion_espacio = tiempo_actual

    # Actualizar
    if girando:
        angulo += velocidad
        velocidad *= 0.98
        if velocidad < 0.002:
            if not esperando_reduccion and len(opciones_disponibles) > 0:
                # Normalizar el ángulo
                angulo_normalizado = (angulo % (2 * math.pi))
                # Calcular el índice del ganador
                angulo_por_segmento = 2 * math.pi / len(opciones_disponibles)
                indice = int(((angulo_normalizado + math.pi/2) % (2 * math.pi)) / angulo_por_segmento)
                indice = (len(opciones_disponibles) - indice - 1) % len(opciones_disponibles)
                
                ganador_actual = opciones_disponibles[indice]
                resultado = f"{ganador_actual.upper()}"
                
                if sonido_giro:
                    sonido_giro.stop()
                    print("Sonido de giro detenido")
                    if ganador_actual in sonidos_victoria:
                        sonidos_victoria[ganador_actual].play()
                        print(f"Reproduciendo sonido de victoria para {ganador_actual}")
                    elif sonido_win:
                        sonido_win.play()
                        print("Reproduciendo sonido de victoria genérico")
                
                esperando_reduccion = True
                tiempo_ganador = pygame.time.get_ticks()
                mostrar_resultado = True
                tiempo_resultado = tiempo_ganador
                girando = False

    # Dibujar
    if video_fondo:
        if girando:
            ret, frame = video_fondo.read()
            if ret:
                # Ajustar el frame a pantalla completa manteniendo proporción
                altura, ancho = frame.shape[:2]
                escala = max(ANCHO/ancho, ALTO/altura)
                nuevo_ancho = int(ancho * escala)
                nueva_altura = int(altura * escala)
                
                # Centrar el frame
                x = (ANCHO - nuevo_ancho) // 2
                y = (ALTO - nueva_altura) // 2
                
                frame = cv2.resize(frame, (nuevo_ancho, nueva_altura))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                fondo_actual = pygame.surfarray.make_surface(frame)
                fondo_actual = pygame.transform.rotate(fondo_actual, -90)
                fondo_actual = pygame.transform.flip(fondo_actual, True, False)
                pantalla.blit(fondo_actual, (x, y))
            else:
                video_fondo.set(cv2.CAP_PROP_POS_FRAMES, 0)
                pantalla.blit(fondo_estatico, (0, 0))
        else:
            pantalla.blit(fondo_estatico, (0, 0))
    else:
        pantalla.fill(BLANCO)
    
    # Dibujar título "Megamix" arriba
    fuente_titulo = pygame.font.Font(None, 72)
    texto_titulo = fuente_titulo.render("MEGAMIX", True, NEGRO)
    rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, 50))
    pantalla.blit(texto_titulo, rect_titulo)
    
    # Dibujar logo de Megaman Megamix en la esquina superior izquierda
    if logo_megamix:
        pantalla.blit(logo_megamix, (20, 20))
    
    if len(opciones_disponibles) > 0:
        # Dibujar círculo base
        pygame.draw.circle(pantalla, NEGRO, centro, radio + 2)
        pygame.draw.circle(pantalla, BLANCO, centro, radio)
        
        # Dibujar secciones
        angulo_por_segmento = 2 * math.pi / len(opciones_disponibles)
        for i, (opcion, imagen) in enumerate(zip(opciones_disponibles, imagenes)):
            # Dibujar líneas divisorias
            angulo_linea = angulo + i * angulo_por_segmento
            fin_x = centro[0] + math.cos(angulo_linea) * radio
            fin_y = centro[1] + math.sin(angulo_linea) * radio
            pygame.draw.line(pantalla, NEGRO, centro, (fin_x, fin_y), 2)
            
            # Dibujar imágenes
            angulo_imagen = angulo + (i + 0.5) * angulo_por_segmento
            
            # Ajustar distancia para Megaman
            factor_distancia = 0.7  # Distancia normal
            if opcion in ["Megaman", "Super Tennis"]:
                factor_distancia = factor_distancia * 1  # 15% más hacia afuera (0.66 + 0.10)
            
            pos_x = centro[0] + math.cos(angulo_imagen) * (radio * factor_distancia)
            pos_y = centro[1] + math.sin(angulo_imagen) * (radio * factor_distancia)
            
            # Rotar y dibujar imagen
            smooth_scaled_image = pygame.transform.smoothscale(imagen, (normalized_width, normalized_height))
            imagen_rotada = pygame.transform.rotate(smooth_scaled_image, -math.degrees(angulo_imagen + math.pi/2))
            rect = imagen_rotada.get_rect(center=(pos_x, pos_y))
            pantalla.blit(imagen_rotada, rect)
        
        # Dibujar GIF en el centro
        if gif_centro:
            if girando:
                frame_actual = gif_centro.get_next_frame()
            else:
                frame_actual = gif_centro.get_static_frame()
            rect_gif = frame_actual.get_rect(center=centro)
            pantalla.blit(frame_actual, rect_gif)
        
        # Dibujar flecha
        if flecha:
            flecha_rotada = pygame.transform.rotate(flecha, 90)
            rect_flecha = flecha_rotada.get_rect(center=(centro[0], centro[1] - radio - 60))
            pantalla.blit(flecha_rotada, rect_flecha)
    
    if mostrar_resultado:
        # Mostrar resultado hasta que se presione espacio
        # Fondo negro sólido
        overlay = pygame.Surface((ANCHO, 200))
        overlay.fill(NEGRO)
        pantalla.blit(overlay, (0, centro[1] - 100))
        
        # Texto del resultado
        texto_resultado = fuente.render(resultado, True, BLANCO)
        rect_texto = texto_resultado.get_rect(center=((ANCHO // 3) - (ANCHO // 6), centro[1]))
        pantalla.blit(texto_resultado, rect_texto)
        
        # Imagen del ganador
        indice_imagen = opciones_disponibles.index(ganador_actual)
        imagen_ganador = pygame.transform.scale(imagenes[indice_imagen], (160, 160))
        rect_imagen = imagen_ganador.get_rect(center=(ANCHO // 2 + (ANCHO // 6), centro[1]))
        pantalla.blit(imagen_ganador, rect_imagen)
        
        # GIF de victoria justo al lado de la imagen
        try:
            nombre_archivo = f'imagenes/gifs/{ganador_actual.lower().replace(" ", "_")}_win.gif'
            if ganador_actual not in gifs_victoria:
                velocidad = 2.0 if ganador_actual == "Donkey Kong" else 1.0  # Mitad de velocidad
                gifs_victoria[ganador_actual] = AnimatedGIF(nombre_archivo, velocidad)
            frame_victoria = gifs_victoria[ganador_actual].get_next_frame()
            
            # Ajustar posición específicamente para ciertos juegos
            posicion_x = ANCHO // 2 + ANCHO // 4
            if ganador_actual == "Mortal Kombat 2":
                posicion_x = ANCHO // 2 + 502  # 10% más a la izquierda que antes
                # Obtener el tamaño original y agrandarlo 2.25 veces
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 2.25)  # 2.25 veces más grande
                nuevo_alto = int(alto_original * 2.25)    # 2.25 veces más grande
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "Pokemon":
                posicion_x = ANCHO // 2 + 434  # 40% más a la derecha
                # Obtener el tamaño original (tamaño normal)
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 1.0)  # Tamaño original
                nuevo_alto = int(alto_original * 1.0)    # Tamaño original
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "Battletoads":
                posicion_x = ANCHO // 2 + 463  # 15% más a la derecha
                # Obtener el tamaño original y agrandarlo 50%
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 1.5)  # 50% más grande
                nuevo_alto = int(alto_original * 1.5)    # 50% más grande
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "Street Fighter 2":
                posicion_x = ANCHO // 2 + 434  # 40% más a la derecha
                # Obtener el tamaño original y agrandarlo 4 veces
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 4.0)  # 4 veces más grande
                nuevo_alto = int(alto_original * 4.0)    # 4 veces más grande
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "The Simpsons":
                posicion_x = ANCHO // 2 + 434  # 10% más a la derecha
                # Obtener el tamaño original y duplicarlo
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 2.0)  # Duplicar el tamaño
                nuevo_alto = int(alto_original * 2.0)    # Duplicar el tamaño
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "Mario Bros":
                posicion_x = ANCHO // 2 + 403  # 30% más a la derecha
                # Obtener el tamaño original y aumentarlo 30%
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 1.3)  # 30% más grande
                nuevo_alto = int(alto_original * 1.3)    # 30% más grande
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "Super Tennis":
                posicion_x = ANCHO // 2 + 447  # 10% más a la derecha
                # Obtener el tamaño original y agrandarlo 2 veces
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 2.0)  # 2 veces más grande
                nuevo_alto = int(alto_original * 2.0)    # 2 veces más grande
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            elif ganador_actual == "Megaman":
                posicion_x = ANCHO // 2 + 523  # 30% más a la derecha
                # Obtener el tamaño original y agrandarlo 300%
                ancho_original, alto_original = frame_victoria.get_size()
                nuevo_ancho = int(ancho_original * 3.0)  # 300% más grande
                nuevo_alto = int(alto_original * 3.0)    # 300% más grande
                frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
            
            rect_gif = frame_victoria.get_rect(center=(posicion_x, centro[1]))
            pantalla.blit(frame_victoria, rect_gif)
        except Exception as e:
            print(f"Error al cargar GIF de victoria para {ganador_actual}: {e}")
            pass

    pygame.display.flip()
    reloj.tick(60)

# Guardar estado al cerrar el programa
guardar_estado(opciones_usadas, opciones_disponibles)
pygame.quit()
