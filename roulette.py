import pygame
import math
from game_config import *


class Roulette:
    """Handles roulette spinning logic and rendering"""
    
    def __init__(self, asset_manager, centro, radio):
        self.asset_manager = asset_manager
        self.centro = centro
        self.radio = radio
        self.angulo = 0
        self.velocidad = 0
        self.girando = False
        self.normalized_width = ANCHO // 10
        self.normalized_height = ANCHO // 10
    
    def start_spin(self):
        """Start spinning the roulette"""
        if not self.girando and len(self.asset_manager.opciones_disponibles) > 0:
            self.velocidad = VELOCIDAD_INICIAL
            self.girando = True
            self.asset_manager.play_spin_sound()
    
    def update(self):
        """Update roulette physics"""
        if self.girando:
            self.angulo += self.velocidad
            self.velocidad *= FACTOR_FRICCION
            
            if self.velocidad < VELOCIDAD_MINIMA:
                return self._finish_spin()
        return None
    
    def force_stop(self):
        """Force the roulette to stop spinning"""
        if self.girando:
            self.velocidad = VELOCIDAD_FORZADA
    
    def _finish_spin(self):
        """Calculate winner when spin finishes"""
        if len(self.asset_manager.opciones_disponibles) > 0:
            angulo_normalizado = (self.angulo % (2 * math.pi))
            angulo_por_segmento = 2 * math.pi / len(self.asset_manager.opciones_disponibles)
            indice = int(((angulo_normalizado + math.pi/2) % (2 * math.pi)) / angulo_por_segmento)
            indice = (len(self.asset_manager.opciones_disponibles) - indice - 1) % len(self.asset_manager.opciones_disponibles)
            
            ganador = self.asset_manager.opciones_disponibles[indice]
            self.girando = False
            self.asset_manager.stop_spin_sound()
            self.asset_manager.play_victory_sound(ganador)
            
            return ganador
        return None
    
    def draw(self, pantalla):
        """Draw the roulette wheel"""
        if len(self.asset_manager.opciones_disponibles) == 0:
            return
        
        # Draw base circle
        pygame.draw.circle(pantalla, NEGRO, self.centro, self.radio + 2)
        pygame.draw.circle(pantalla, BLANCO, self.centro, self.radio)
        
        # Draw sections
        angulo_por_segmento = 2 * math.pi / len(self.asset_manager.opciones_disponibles)
        for i, (opcion, imagen) in enumerate(zip(self.asset_manager.opciones_disponibles, self.asset_manager.imagenes)):
            # Draw dividing lines
            angulo_linea = self.angulo + i * angulo_por_segmento
            fin_x = self.centro[0] + math.cos(angulo_linea) * self.radio
            fin_y = self.centro[1] + math.sin(angulo_linea) * self.radio
            pygame.draw.line(pantalla, NEGRO, self.centro, (fin_x, fin_y), 2)
            
            # Draw images
            self._draw_option_image(pantalla, opcion, imagen, i, angulo_por_segmento)
        
        # Draw center GIF
        self._draw_center_gif(pantalla)
        
        # Draw arrow
        self._draw_arrow(pantalla)
    
    def _draw_option_image(self, pantalla, opcion, imagen, index, angulo_por_segmento):
        """Draw individual option image on the roulette"""
        angulo_imagen = self.angulo + (index + 0.5) * angulo_por_segmento
        
        # Adjust distance for specific games
        factor_distancia = 0.7
        if opcion in ["Megaman", "Super Tennis"]:
            factor_distancia = factor_distancia * 1
        
        pos_x = self.centro[0] + math.cos(angulo_imagen) * (self.radio * factor_distancia)
        pos_y = self.centro[1] + math.sin(angulo_imagen) * (self.radio * factor_distancia)
        
        # Scale and rotate image
        smooth_scaled_image = pygame.transform.smoothscale(imagen, (self.normalized_width, self.normalized_height))
        imagen_rotada = pygame.transform.rotate(smooth_scaled_image, -math.degrees(angulo_imagen + math.pi/2))
        rect = imagen_rotada.get_rect(center=(pos_x, pos_y))
        pantalla.blit(imagen_rotada, rect)
    
    def _draw_center_gif(self, pantalla):
        """Draw animated GIF in center"""
        if self.asset_manager.gif_centro:
            if self.girando:
                frame_actual = self.asset_manager.gif_centro.get_next_frame()
            else:
                frame_actual = self.asset_manager.gif_centro.get_static_frame()
            
            if frame_actual:
                rect_gif = frame_actual.get_rect(center=self.centro)
                pantalla.blit(frame_actual, rect_gif)
    
    def _draw_arrow(self, pantalla):
        """Draw arrow pointing to winner"""
        if self.asset_manager.flecha:
            flecha_rotada = pygame.transform.rotate(self.asset_manager.flecha, 90)
            rect_flecha = flecha_rotada.get_rect(center=(self.centro[0], self.centro[1] - self.radio - 60))
            pantalla.blit(flecha_rotada, rect_flecha)
