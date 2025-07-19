import json
import os


class GameState:
    """Manages game state persistence"""
    
    def __init__(self, script_dir, opciones_iniciales):
        self.script_dir = script_dir
        self.opciones_iniciales = opciones_iniciales
        self.estado_archivo = os.path.join(script_dir, 'estado_ruleta.json')
        
        # Load saved state
        self.opciones_usadas, self.opciones_disponibles = self.cargar_estado()
    
    def guardar_estado(self):
        """Save current game state"""
        estado = {
            'opciones_usadas': self.opciones_usadas,
            'opciones_disponibles': self.opciones_disponibles
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
                print("Estado cargado correctamente")
                return estado.get('opciones_usadas', []), estado.get('opciones_disponibles', self.opciones_iniciales.copy())
            else:
                print("No se encontró archivo de estado, usando configuración inicial")
                return [], self.opciones_iniciales.copy()
        except Exception as e:
            print(f"Error al cargar estado: {e}")
            return [], self.opciones_iniciales.copy()
    
    def reset_game(self):
        """Reset game to initial state"""
        self.opciones_disponibles = self.opciones_iniciales.copy()
        self.opciones_usadas = []
        self.guardar_estado()
    
    def remove_winner(self, ganador):
        """Remove winner from available options"""
        if ganador in self.opciones_disponibles:
            self.opciones_usadas.append(ganador)
            self.opciones_disponibles.remove(ganador)
            self.guardar_estado()
