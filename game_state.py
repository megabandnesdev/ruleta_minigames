import json
import os


class GameState:
    """Manages game state persistence"""
    
    def __init__(self, *args, **kwargs):
        if 'script_dir' in kwargs:
            self.script_dir = kwargs['script_dir']
        elif args:
            self.script_dir = args[0]
        if 'opciones_iniciales' in kwargs:
            self.opciones_iniciales = kwargs['opciones_iniciales']
        else:
            self.opciones_iniciales = []

        if 'singleplayer_options' in kwargs:
            self.singleplayer_options = kwargs['singleplayer_options']
        else:
            self.singleplayer_options = []

        if 'multiplayer_options' in kwargs:
            self.multiplayer_options = kwargs['multiplayer_options']
        else:
            self.multiplayer_options = []    
        self.estado_archivo = os.path.join(self.script_dir, 'estado_ruleta.json')

        # Game modes
        self.ROULETTE_MODE = "roulette"
        self.SINGLEPLAYER_MODE = "singleplayer"
        self.current_mode = self.ROULETTE_MODE
        # Load saved state
        self.opciones_usadas, self.opciones_disponibles,self.available_singleplayer_options,self.available_multiplayer_options = self.cargar_estado()
    
    def get_current_mode(self):
        """Get the current game mode"""
        return self.current_mode
    
    def set_mode(self, mode):
        """Set the current game mode"""
        if mode in [self.ROULETTE_MODE, self.SINGLEPLAYER_MODE]:
            self.current_mode = mode
            print(f"Game mode changed to: {mode}")
        else:
            print(f"Invalid game mode: {mode}")
    
    def switch_mode(self):
        """Switch between roulette and single player modes"""
        if self.current_mode == self.ROULETTE_MODE:
            self.current_mode = self.SINGLEPLAYER_MODE
        else:
            self.current_mode = self.ROULETTE_MODE
        print(f"Switched to {self.current_mode} mode")
        return self.current_mode
    
    def is_roulette_mode(self):
        """Check if current mode is roulette"""
        return self.current_mode == self.ROULETTE_MODE
    
    def is_singleplayer_mode(self):
        """Check if current mode is single player"""
        return self.current_mode == self.SINGLEPLAYER_MODE
   
    def guardar_estado(self):
        """Save current game state"""
        estado = {
            'opciones_usadas': self.opciones_usadas,
            'opciones_disponibles': self.opciones_disponibles,
            'available_singleplayer_options': self.available_singleplayer_options,
            'available_multiplayer_options': self.available_multiplayer_options,
            'current_mode': self.current_mode
        }
        try:
            with open(self.estado_archivo, 'w') as f:
                json.dump(estado, f)
            print("Estado guardado correctamente")
        except Exception as e:
            print(f"Error al guardar estado: {e}")
    
    def cargar_estado(self):
        """Load saved game state"""
        try:
            if os.path.exists(self.estado_archivo):
                with open(self.estado_archivo, 'r') as f:
                    estado = json.load(f)
                # Load game mode if saved
                self.current_mode = estado.get('current_mode', self.ROULETTE_MODE)
                print("Estado cargado correctamente")
                return estado.get('opciones_usadas', []), estado.get('opciones_disponibles', self.opciones_iniciales.copy()), estado.get('available_singleplayer_options', self.singleplayer_options.copy()),estado.get('available_multiplayer_options', self.multiplayer_options.copy())
            else:
                print("No se encontró archivo de estado, usando configuración inicial")
                return [], self.opciones_iniciales.copy(),self.singleplayer_options.copy(),self.multiplayer_options.copy()
        except Exception as e:
            print(f"Error al cargar estado: {e}")
            return [], self.opciones_iniciales.copy(),self.singleplayer_options.copy(),self.multiplayer_options.copy()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.opciones_disponibles = self.opciones_iniciales.copy()
        self.available_singleplayer_options = self.singleplayer_options.copy()
        self.available_multiplayer_options = self.multiplayer_options.copy()

        self.opciones_usadas = []
        self.guardar_estado()
    
    def remove_winner(self, ganador):
        """Remove winner from available options"""
        if ganador in self.opciones_disponibles:
            self.opciones_usadas.append(ganador)
            self.opciones_disponibles.remove(ganador)
            self.guardar_estado()
