import pygame
import os
import sys
from game_config import *
from asset_manager import AssetManager
from roulette import Roulette
from winner_display import WinnerDisplay
from game_state import GameState

# Initialize Pygame
pygame.init()

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Setup display
pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Ruleta Retro")

# Initialize game components
game_state = GameState(script_dir, OPCIONES)
asset_manager = AssetManager(script_dir, game_state.opciones_disponibles)
centro = (ANCHO // 2, int(ALTO * 0.55))
roulette = Roulette(asset_manager, centro, RADIO_BASE)
fuente = pygame.font.Font(None, 96)
winner_display = WinnerDisplay(asset_manager, fuente)

# Game state variables
resultado = ""
mostrar_resultado = False
tiempo_resultado = 0
esperando_reduccion = False
tiempo_ganador = 0
ganador_actual = None
ultima_pulsacion_espacio = 0
esperando_espacio_para_salir = False
modo_pantalla_completa = True

def cambiar_modo_pantalla():
    global pantalla, modo_pantalla_completa
    modo_pantalla_completa = not modo_pantalla_completa
    if modo_pantalla_completa:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
        print("Cambiado a pantalla completa")
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        print("Cambiado a modo ventana")

# Main game loop
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    # Handle events
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                cambiar_modo_pantalla()
            elif evento.key == pygame.K_r:
                # Reset game
                print("Reset de la ruleta")
                game_state.reset_game()
                asset_manager.reload_images(game_state.opciones_disponibles)
                roulette.girando = False
                mostrar_resultado = False
                esperando_reduccion = False
                ganador_actual = None
                roulette.angulo = 0
                roulette.velocidad = 0
            elif evento.key == pygame.K_SPACE:
                tiempo_actual = pygame.time.get_ticks()
                if roulette.girando and tiempo_actual - ultima_pulsacion_espacio < TIEMPO_DOBLE_PULSACION:
                    # Double press detected during spin, force stop
                    roulette.force_stop()
                elif mostrar_resultado and tiempo_actual - ultima_pulsacion_espacio < TIEMPO_DOBLE_PULSACION:
                    # Double press detected during result, skip to wait
                    mostrar_resultado = False
                    esperando_espacio_para_salir = False
                    if esperando_reduccion:
                        roulette.asset_manager.stop_victory_sound()
                        game_state.remove_winner(ganador_actual)
                        asset_manager.reload_images(game_state.opciones_disponibles)
                        esperando_reduccion = False
                        ganador_actual = None
                elif mostrar_resultado:
                    # Single press during result, exit victory scene
                    mostrar_resultado = False
                    esperando_espacio_para_salir = False
                    if esperando_reduccion:
                        roulette.asset_manager.stop_victory_sound()
                        game_state.remove_winner(ganador_actual)
                        asset_manager.reload_images(game_state.opciones_disponibles)
                        esperando_reduccion = False
                        ganador_actual = None
                elif not roulette.girando and not esperando_reduccion and len(game_state.opciones_disponibles) > 0:
                    roulette.start_spin()
                ultima_pulsacion_espacio = tiempo_actual
    
    # Update roulette
    winner = roulette.update()
    if winner:
        ganador_actual = winner
        resultado = f"{ganador_actual.upper()}"
        esperando_reduccion = True
        tiempo_ganador = pygame.time.get_ticks()
        mostrar_resultado = True
        tiempo_resultado = tiempo_ganador
    
    # Draw everything
    if asset_manager.video_fondo and roulette.girando:
        background, pos = asset_manager.get_next_background_frame()
        pantalla.blit(background, pos)
    else:
        pantalla.blit(asset_manager.fondo_estatico, (0, 0))
    
    # Draw title and logo
    fuente_titulo = pygame.font.Font(None, 72)
    texto_titulo = fuente_titulo.render("MEGAMIX", True, NEGRO)
    rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, 50))
    pantalla.blit(texto_titulo, rect_titulo)
    
    if asset_manager.logo_megamix:
        pantalla.blit(asset_manager.logo_megamix, (20, 20))
    
    # Draw roulette
    if len(game_state.opciones_disponibles) > 0:
        roulette.draw(pantalla)
    
    # Draw winner scene if needed
    if mostrar_resultado:
        winner_display.draw_winner_scene(pantalla, ganador_actual, resultado, centro)
    
    pygame.display.flip()
    reloj.tick(60)

# Cleanup
game_state.guardar_estado()
pygame.quit()
