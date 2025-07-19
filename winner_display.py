import pygame
import math
from game_config import ANCHO, ALTO, BLANCO, NEGRO


class WinnerDisplay:
    """Handles the display of winning results"""
    
    def __init__(self, asset_manager, fuente):
        self.asset_manager = asset_manager
        self.fuente = fuente
        self.centro_mitad_derecha = ANCHO // 2 + ANCHO // 4  # x = 960
    
    def draw_winner_scene(self, pantalla, ganador_actual, resultado, centro):
        """Draw the complete winner scene"""
        # Black overlay
        overlay = pygame.Surface((ANCHO, 200))
        overlay.fill(NEGRO)
        pantalla.blit(overlay, (0, centro[1] - 100))
        
        # Result text
        self._draw_result_text(pantalla, resultado, centro)
        
        # Winner image in right half
        self._draw_winner_image(pantalla, ganador_actual, centro)
        
        # Victory GIF
        self._draw_victory_gif(pantalla, ganador_actual, centro)
    
    def _draw_result_text(self, pantalla, resultado, centro):
        """Draw the result text on the left side"""
        texto_resultado = self.fuente.render(resultado, True, BLANCO)
        rect_texto = texto_resultado.get_rect(center=((ANCHO // 3) - (ANCHO // 6), centro[1]))
        pantalla.blit(texto_resultado, rect_texto)
    
    def _draw_winner_image(self, pantalla, ganador_actual, centro):
        """Draw winner image in the center of right half"""
        indice_imagen = self.asset_manager.opciones_disponibles.index(ganador_actual)
        imagen_ganador = pygame.transform.scale(self.asset_manager.imagenes[indice_imagen], (200, 200))
        rect_imagen = imagen_ganador.get_rect(center=(self.centro_mitad_derecha, centro[1]))
        pantalla.blit(imagen_ganador, rect_imagen)
    
    def _draw_victory_gif(self, pantalla, ganador_actual, centro):
        """Draw victory GIF positioned in right half"""
        gif_victoria = self.asset_manager.get_victory_gif(ganador_actual)
        if not gif_victoria:
            return
            
        frame_victoria = gif_victoria.get_next_frame()
        if not frame_victoria:
            return
        
        # Base position in right half
        posicion_base_x = self.centro_mitad_derecha + 120
        
        # Game-specific positioning and scaling
        posicion_x, frame_victoria = self._apply_game_specific_settings(
            ganador_actual, frame_victoria, posicion_base_x
        )
        
        # Ensure GIF doesn't go beyond screen
        if posicion_x > ANCHO - 100:
            posicion_x = ANCHO - 100
        
        rect_gif = frame_victoria.get_rect(center=(posicion_x, centro[1]))
        pantalla.blit(frame_victoria, rect_gif)
    
    def _apply_game_specific_settings(self, ganador_actual, frame_victoria, posicion_base_x):
        """Apply game-specific positioning and scaling"""
        game_settings = {
            "Mortal Kombat 2": {"offset": -50, "scale": 2.25},
            "Pokemon": {"offset": 20, "scale": 1.0},
            "Battletoads": {"offset": 10, "scale": 1.5},
            "Street Fighter 2": {"offset": 20, "scale": 4.0},
            "The Simpsons": {"offset": 20, "scale": 2.0},
            "Mario Bros": {"offset": 0, "scale": 1.3},
            "Super Tennis": {"offset": 30, "scale": 2.0},
            "Megaman": {"offset": 60, "scale": 3.0},
        }
        
        if ganador_actual in game_settings:
            settings = game_settings[ganador_actual]
            posicion_x = posicion_base_x + settings["offset"]
            
            ancho_original, alto_original = frame_victoria.get_size()
            nuevo_ancho = int(ancho_original * settings["scale"])
            nuevo_alto = int(alto_original * settings["scale"])
            frame_victoria = pygame.transform.scale(frame_victoria, (nuevo_ancho, nuevo_alto))
        else:
            posicion_x = posicion_base_x
        
        return posicion_x, frame_victoria
