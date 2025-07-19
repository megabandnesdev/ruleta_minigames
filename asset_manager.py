import pygame
import os
import cv2
import copy
import numpy as np
from PIL import Image
import time


class AnimatedGIF:
    """Class to handle animated GIF loading and playback"""
    
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
        self.static_frame = self.frames[-1] if self.frames else None
    
    def get_next_frame(self):
        if not self.frames:
            return None
            
        current_time = time.time() * 1000
        if current_time - self.last_update > (self.frame_duration * self.velocidad):
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time
        return self.frames[self.current_frame]
    
    def get_static_frame(self):
        return self.static_frame


class AssetManager:
    """Manages all game assets including images, sounds, videos, and GIFs"""
    
    def __init__(self, script_dir, opciones_disponibles, tamano_imagen=180, screen_width=1280, screen_height=720):
        self.script_dir = script_dir
        self.opciones_disponibles = opciones_disponibles
        self.tamano_imagen = tamano_imagen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.last_winner = None

        # Asset containers
        self.imagenes = []
        self.sonidos_victoria = {}
        self.gifs_victoria = {}
        self.sonido_giro = None
        self.sonido_win = None
        self.video_fondo = None
        self.fondo_estatico = None
        self.gif_centro = None
        self.flecha = None
        self.logo_megamix = None
        
        # Load all assets
        self._load_all_assets()
    
    def _load_all_assets(self):
        """Load all game assets"""
        self._load_images()
        self._load_sounds()
        self._load_background_video()
        self._load_center_gif()
        self._load_arrow()
        self._load_logo()
    
    def _load_images(self):
        """Load game option images"""
        self.imagenes = []
        for opcion in self.opciones_disponibles:
            try:
                ruta = os.path.join(self.script_dir, 'imagenes', f'{opcion}.png')
                print(f"Buscando imagen: {ruta}")
                if os.path.exists(ruta):
                    print(f"Imagen encontrada: {ruta}")
                    imagen = pygame.image.load(ruta)
                    ancho_original, alto_original = imagen.get_size()
                    
                    # Apply size adjustments for specific games
                    tamano_ajustado = self.tamano_imagen
                    if opcion in ["Mortal Kombat 2", "Super Tennis"]:
                        tamano_ajustado = int(self.tamano_imagen * 0.8)
                    if opcion == "Battletoads":
                        tamano_ajustado = int(self.tamano_imagen * 1.2)
                    
                    factor_escala = min(tamano_ajustado / ancho_original, tamano_ajustado / alto_original)
                    nuevo_ancho = int(ancho_original * factor_escala)
                    nuevo_alto = int(alto_original * factor_escala)
                    imagen = pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))
                    self.imagenes.append(imagen)
                else:
                    print(f"Imagen NO encontrada: {ruta}")
                    superficie = pygame.Surface((self.tamano_imagen, self.tamano_imagen))
                    superficie.fill((255, 255, 255))
                    self.imagenes.append(superficie)
            except Exception as e:
                print(f"Error cargando imagen para {opcion}: {e}")
                superficie = pygame.Surface((self.tamano_imagen, self.tamano_imagen))
                superficie.fill((255, 255, 255))
                self.imagenes.append(superficie)
    
    def _load_sounds(self):
        """Load all sound assets"""
        try:
            self.sonido_giro = pygame.mixer.Sound(os.path.join(self.script_dir, 'sonidos', 'giro.wav'))
            self.sonido_win = pygame.mixer.Sound(os.path.join(self.script_dir, 'sonidos', 'win.wav'))
        except Exception as e:
            print(f"Error loading main sounds: {e}")
            self.sonido_giro = None
            self.sonido_win = None
        
        self.sonidos_victoria = {}
        for opcion in self.opciones_disponibles:
            try:
                ruta = os.path.join(self.script_dir, 'sonidos', f'{opcion.lower().replace(" ", "_")}_win.wav')
                self.sonidos_victoria[opcion] = pygame.mixer.Sound(ruta)
            except Exception as e:
                print(f"Error loading victory sound for {opcion}: {e}")
    
    def _load_background_video(self):
        """Load background video"""
        ruta_video = os.path.join(self.script_dir, 'imagenes', 'fondo.mp4')
        print(f"Buscando video de fondo: {ruta_video}")
        try:
            if os.path.exists(ruta_video):
                self.video_fondo = cv2.VideoCapture(ruta_video)
                ret, frame = self.video_fondo.read()
                if ret:
                    altura, ancho = frame.shape[:2]
                    escala = max(self.screen_width/ancho, self.screen_height/altura)
                    nuevo_ancho = int(ancho * escala)
                    nueva_altura = int(altura * escala)
                    frame = cv2.resize(frame, (nuevo_ancho, nueva_altura))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.fondo_estatico = pygame.surfarray.make_surface(frame)
                    self.fondo_estatico = pygame.transform.rotate(self.fondo_estatico, -90)
                    self.fondo_estatico = pygame.transform.flip(self.fondo_estatico, True, False)
                else:
                    print("No se pudo leer el primer frame del video, usando fondo gris.")
                    self._create_default_background()
                    self.video_fondo = None
            else:
                print(f"Video fondo.mp4 NO encontrado: {ruta_video}")
                self._create_default_background()
                self.video_fondo = None
        except Exception as e:
            print(f"Error al cargar el video de fondo: {e}")
            self.video_fondo = None
            self._create_default_background()
    
    def _create_default_background(self):
        """Create a default gray background"""
        self.fondo_estatico = pygame.Surface((self.screen_width, self.screen_height))
        self.fondo_estatico.fill((50, 50, 50))
    
    def _load_center_gif(self):
        """Load center animated GIF"""
        ruta_gif_centro = os.path.join(self.script_dir, 'imagenes', 'gifs', 'centro.gif')
        print(f"Buscando GIF del centro: {ruta_gif_centro}")
        try:
            if os.path.exists(ruta_gif_centro):
                self.gif_centro = AnimatedGIF(ruta_gif_centro, tamano_maximo=200)
            else:
                print(f"GIF centro.gif NO encontrado: {ruta_gif_centro}")
                self.gif_centro = None
        except Exception as e:
            print(f"Error al cargar el GIF del centro: {e}")
            self.gif_centro = None
    
    def _load_arrow(self):
        """Load arrow image"""
        try:
            ruta_flecha = os.path.join(self.script_dir, 'imagenes', 'Flecha.png')
            self.flecha = pygame.image.load(ruta_flecha)
            self.flecha = pygame.transform.scale(self.flecha, (120, 96))
        except Exception as e:
            print(f"Error loading arrow: {e}")
            self.flecha = None
    
    def _load_logo(self):
        """Load Megaman logo"""
        try:
            ruta_logo = os.path.join(self.script_dir, 'imagenes', 'Megaband Logo.png')
            self.logo_megamix = pygame.image.load(ruta_logo)
            ancho_original, alto_original = self.logo_megamix.get_size()
            factor_escala = ancho_original / self.screen_width / 2
            nuevo_ancho = int(ancho_original * factor_escala)
            nuevo_alto = int(alto_original * factor_escala)
            self.logo_megamix = pygame.transform.scale(self.logo_megamix, (nuevo_ancho, nuevo_alto))
            print("Logo Megaman cargado correctamente")
        except Exception as e:
            print(f"Error al cargar megaman megamix: {e}")
            self.logo_megamix = None
    
    def reload_images(self, new_opciones_disponibles):
        """Reload images when available options change"""
        self.opciones_disponibles = new_opciones_disponibles
        self._load_images()
    
    def get_victory_gif(self, ganador_actual):
        """Get or load victory GIF for a specific winner"""
        if ganador_actual not in self.gifs_victoria:
            try:
                nombre_archivo = os.path.join(
                    self.script_dir, 'imagenes', 'gifs', 
                    f'{ganador_actual.lower().replace(" ", "_")}_win.gif'
                )
                velocidad = 2.0 if ganador_actual == "Donkey Kong" else 1.0
                self.gifs_victoria[ganador_actual] = AnimatedGIF(nombre_archivo, velocidad)
            except Exception as e:
                print(f"Error al cargar GIF de victoria para {ganador_actual}: {e}")
                return None
        
        return self.gifs_victoria[ganador_actual]
    
    def get_next_background_frame(self):
        """Get next frame from background video"""
        if self.video_fondo:
            ret, frame = self.video_fondo.read()
            if ret:
                altura, ancho = frame.shape[:2]
                escala = max(self.screen_width/ancho, self.screen_height/altura)
                nuevo_ancho = int(ancho * escala)
                nueva_altura = int(altura * escala)
                
                x = (self.screen_width - nuevo_ancho) // 2
                y = (self.screen_height - nueva_altura) // 2
                
                frame = cv2.resize(frame, (nuevo_ancho, nueva_altura))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                fondo_actual = pygame.surfarray.make_surface(frame)
                fondo_actual = pygame.transform.rotate(fondo_actual, -90)
                fondo_actual = pygame.transform.flip(fondo_actual, True, False)
                return fondo_actual, (x, y)
            else:
                self.video_fondo.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return self.fondo_estatico, (0, 0)
        else:
            return self.fondo_estatico, (0, 0)
    
    def play_spin_sound(self):
        """Play spinning sound"""
        if self.sonido_giro:
            self.sonido_giro.play()
    
    def stop_spin_sound(self):
        """Stop spinning sound"""
        if self.sonido_giro:
            self.sonido_giro.stop()
    
    def play_victory_sound(self, ganador_actual):
        """Play victory sound for winner"""
        self.last_winner = copy.copy(ganador_actual)
        if ganador_actual in self.sonidos_victoria:
            self.sonidos_victoria[ganador_actual].play()
            print(f"Reproduciendo sonido de victoria para {ganador_actual}")
        elif self.sonido_win:
            self.sonido_win.play()
            print("Reproduciendo sonido de victoria genérico")

    def stop_victory_sound(self):
        """Play victory sound for winner"""
        if self.last_winner  in self.sonidos_victoria:
            self.sonidos_victoria[self.last_winner ].stop()
            print(f"Deteniendo sonido de victoria para {self.last_winner}")
        elif self.sonido_win:
            self.sonido_win.stop()
            print("Deteniendo sonido de victoria genérico")