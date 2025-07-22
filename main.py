import pygame
import os
import sys
from game_config import *
from asset_manager import AssetManager
from roulette import Roulette
from winner_display import WinnerDisplay
from game_state import GameState
from singleplayer_selector import SinglePlayerSelector

# Initialize Pygame
pygame.init()

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Setup display

# Get information about all connected displays
desktop_sizes = pygame.display.get_desktop_sizes()
print(f"Detected displays: {desktop_sizes}")

target_display_index = 0 # Default to primary display

# If there's more than one monitor, try to use the second one (index 1)
if len(desktop_sizes) > 1:
    target_display_index = 1
    print(f"Attempting to use external display (index {target_display_index}).")
else:
    print("Only one display detected. Using the primary display.")

# Get the resolution of the target display
# screen_width, screen_height = desktop_sizes[target_display_index]

modo_pantalla_completa = False

try:
    # Set the display mode to fullscreen on the chosen monitor
    if modo_pantalla_completa:
        pantalla = pygame.display.set_mode((ANCHO, ALTO),pygame.FULLSCREEN, display=target_display_index)
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), display=target_display_index)
    pygame.display.set_caption(f"Pygame on Display {target_display_index}")
    print(f"Successfully set display on monitor {target_display_index}.")
except pygame.error as e:
    print(f"Error setting display mode: {e}")
    print("Falling back to default display.")
    if modo_pantalla_completa:
        pantalla = pygame.display.set_mode((ANCHO, ALTO),pygame.FULLSCREEN, display=0)
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), display=0)

    pygame.display.set_caption("Pygame on Default Display (Fallback)")


pygame.display.set_caption("Ruleta Retro")

# Initialize game components
game_state = GameState(script_dir, opciones_iniciales=OPCIONES,singleplayer_options=SINGLEPLAYER_OPTIONS,multiplayer_options= MULTIPLAYER_OPTIONS)
asset_manager = AssetManager(script_dir, game_state.opciones_disponibles)
centro = (ANCHO // 2, int(ALTO * 0.55))
roulette = Roulette(asset_manager, centro, RADIO_BASE)
singleplayer_selector = SinglePlayerSelector(asset_manager, centro)
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

def cambiar_modo_pantalla():
    global pantalla, modo_pantalla_completa
    modo_pantalla_completa = not modo_pantalla_completa
    if modo_pantalla_completa:
        pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
        print("Cambiado a pantalla completa")
    else:
        pantalla = pygame.display.set_mode((ANCHO, ALTO))
        print("Cambiado a modo ventana")

def reset_current_game():
    """Reset the current game mode"""
    global mostrar_resultado, esperando_reduccion, ganador_actual
    
    if game_state.is_roulette_mode():
        print("Reset de la ruleta")
        game_state.reset_game()
        asset_manager.reload_images(game_state.opciones_disponibles)
        roulette.girando = False
        roulette.angulo = 0
        roulette.velocidad = 0
    elif game_state.is_singleplayer_mode():
        print("Reset del selector single player")
        singleplayer_selector.reset()
    
    # Reset common variables
    mostrar_resultado = False
    esperando_reduccion = False
    ganador_actual = None

def switch_game_mode():
    """Switch between roulette and single player modes"""
    game_state.switch_mode()
    reset_current_game()
    print(f"Cambiado a modo: {game_state.get_current_mode()}")

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
            elif evento.key == pygame.K_m:
                # Switch game mode with 'M' key
                switch_game_mode()
            elif evento.key == pygame.K_r:
                # Reset current game
                reset_current_game()
            elif evento.key == pygame.K_SPACE:
                tiempo_actual = pygame.time.get_ticks()
                if game_state.is_roulette_mode():
                    # Handle roulette mode space key
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
                        
                elif game_state.is_singleplayer_mode():
                    # Handle single player mode space key
                    if not singleplayer_selector.selecting and not singleplayer_selector.is_selection_complete():
                        # Start selection process
                        singleplayer_selector.start_selection()
                    elif singleplayer_selector.is_selection_complete():
                        # Continue after selection or reset
                        if tiempo_actual - ultima_pulsacion_espacio < TIEMPO_DOBLE_PULSACION:
                            # Double press - reset selection
                            singleplayer_selector.reset()
                        else:
                            # Single press - could be used to continue to next phase
                            print(f"Continuing with selected mode: {singleplayer_selector.get_selected_option()}")
                
                ultima_pulsacion_espacio = tiempo_actual
    
    # Update current game mode
    if game_state.is_roulette_mode():
        # Update roulette
        winner = roulette.update()
        if winner:
            ganador_actual = winner
            resultado = f"{ganador_actual.upper()}"
            esperando_reduccion = True
            tiempo_ganador = pygame.time.get_ticks()
            mostrar_resultado = True
            tiempo_resultado = tiempo_ganador
    
    elif game_state.is_singleplayer_mode():
        # Update single player selector
        selected_option = singleplayer_selector.update()
        if selected_option:
            ganador_actual = selected_option
            resultado = f"{ganador_actual.upper()}"
            # No need for esperando_reduccion in single player mode
            tiempo_ganador = pygame.time.get_ticks()
            mostrar_resultado = True
            tiempo_resultado = tiempo_ganador

    # Draw everything
    if game_state.is_roulette_mode():
        # Draw roulette mode
        if asset_manager.video_fondo and roulette.girando:
            background, pos = asset_manager.get_next_background_frame()
            pantalla.blit(background, pos)
        else:
            pantalla.blit(asset_manager.fondo_estatico, (0, 0))
        
        # Draw title and logo
        fuente_titulo = pygame.font.Font(None, 72)
        texto_titulo = fuente_titulo.render("MEGAMIX - ROULETTE", True, NEGRO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, 50))
        pantalla.blit(texto_titulo, rect_titulo)
        
        if asset_manager.logo_megamix:
            pantalla.blit(asset_manager.logo_megamix, (20, 20))
        
        # Draw roulette
        if len(game_state.opciones_disponibles) > 0:
            roulette.draw(pantalla)
            
    elif game_state.is_singleplayer_mode():
        # Draw single player mode
        singleplayer_selector.draw(pantalla)
    
    # Draw winner scene if needed (common for both modes)
    if mostrar_resultado and game_state.is_roulette_mode():
        winner_display.draw_winner_scene(pantalla, ganador_actual, resultado, centro)
    
    # Draw mode switching instructions
    fuente_pequena = pygame.font.Font(None, 36)
    mode_text = fuente_pequena.render(f"Mode: {game_state.get_current_mode().upper()} | Press M to switch | Press R to reset", True, BLANCO)
    pantalla.blit(mode_text, (10, ALTO - 30))

    pygame.display.flip()
    reloj.tick(60)

# Cleanup
game_state.guardar_estado()
pygame.quit()
