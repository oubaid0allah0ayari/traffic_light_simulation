"""
Package de simulation de trafic
Simulation d'un carrefour avec feux intelligents
Version 2.1.0 avec statistiques complètes incluant tracking des feux rouges
"""

__version__ = "2.1.0"
__author__ = "[Votre Nom]"
__all__ = [
    'SimulationManager',
    'SignalManager',
    'VehicleManager',
    'TrafficSignal',
    'Vehicle',
    'StatisticsCollector'
]

# Imports pour faciliter l'utilisation
from .models import TrafficSignal, Vehicle
from .managers import SignalManager, VehicleManager, SimulationManager
from .statistics import StatisticsCollector
from . import config

# Constantes du package
SIMULATION_TITLE = "Simulation de Carrefour Intelligent"
SIMULATION_VERSION = __version__