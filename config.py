"""
Configuration module for traffic simulation
Contains all constants and configuration parameters
"""

# Screen settings
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Signal timing defaults
DEFAULT_GREEN = {0: 10, 1: 10, 2: 10, 3: 10}
DEFAULT_RED = 150
DEFAULT_YELLOW = 5

# Random green signal timer settings
RANDOM_GREEN_SIGNAL_TIMER = True
RANDOM_GREEN_SIGNAL_TIMER_RANGE = [10, 20]

# Number of signals
NO_OF_SIGNALS = 4

# Vehicle speeds (pixels per frame)
SPEEDS = {
    'car': 2.25,
    'bus': 1.8,
    'truck': 1.8,
    'bike': 2.5
}

# Vehicle starting coordinates
X_COORDINATES = {
    'right': [0, 0, 0],
    'down': [755, 727, 697],
    'left': [1400, 1400, 1400],
    'up': [602, 627, 657]
}

Y_COORDINATES = {
    'right': [348, 370, 398],
    'down': [0, 0, 0],
    'left': [498, 466, 436],
    'up': [800, 800, 800]
}

# Vehicle types
VEHICLE_TYPES = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}

# Direction mappings
DIRECTION_NUMBERS = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Signal coordinates
SIGNAL_COORDS = [(530, 230), (810, 230), (810, 570), (530, 570)]
SIGNAL_TIMER_COORDS = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Stop line coordinates
STOP_LINES = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
DEFAULT_STOP = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Vehicle gaps
STOPPING_GAP = 25
MOVING_GAP = 25

# Allowed vehicle types
ALLOWED_VEHICLE_TYPES = {
    'car': True,
    'bus': True,
    'truck': True,
    'bike': True
}

# Rotation settings
ROTATION_ANGLE = 3

# Mid-point coordinates for turns
MID_COORDINATES = {
    'right': {'x': 705, 'y': 445},
    'down': {'x': 695, 'y': 450},
    'left': {'x': 695, 'y': 425},
    'up': {'x': 695, 'y': 400}
}

# Vehicle generation distribution (percentages)
DIRECTION_DISTRIBUTION = [25, 50, 75, 100]  # Cumulative percentages
TURN_PROBABILITY = 40  # Percentage chance of turning

# Image paths
IMAGE_PATHS = {
    'background': 'images/intersection.png',
    'red_signal': 'images/signals/red.png',
    'yellow_signal': 'images/signals/yellow.png',
    'green_signal': 'images/signals/green.png'
}