"""
Module de statistiques pour la simulation de trafic
Collecte et analyse les données de performance
Version finale avec tracking précis des feux rouges - FIXED
"""
import time
from datetime import datetime


class StatisticsCollector:
    """
    Collecte et gère toutes les statistiques de la simulation
    """
    
    def __init__(self):
        """Initialise le collecteur de statistiques"""
        # Temps de démarrage
        self.start_time = time.time()
        self.simulation_start = datetime.now()
        
        # Compteurs globaux
        self.total_vehicles_generated = 0
        self.total_vehicles_crossed = 0
        self.total_cycles_completed = 0
        
        # Statistiques par direction
        self.vehicles_by_direction = {
            'right': {'generated': 0, 'crossed': 0},
            'down': {'generated': 0, 'crossed': 0},
            'left': {'generated': 0, 'crossed': 0},
            'up': {'generated': 0, 'crossed': 0}
        }
        
        # Statistiques par type de véhicule
        self.vehicles_by_type = {
            'car': {'generated': 0, 'crossed': 0},
            'bus': {'generated': 0, 'crossed': 0},
            'truck': {'generated': 0, 'crossed': 0},
            'bike': {'generated': 0, 'crossed': 0}
        }
        
        # Statistiques des feux
        self.signal_stats = {
            0: {'green_times': [], 'total_green_time': 0},
            1: {'green_times': [], 'total_green_time': 0},
            2: {'green_times': [], 'total_green_time': 0},
            3: {'green_times': [], 'total_green_time': 0}
        }
        
        # Historique des niveaux de trafic
        self.traffic_history = {
            'right': [],
            'down': [],
            'left': [],
            'up': []
        }
        
        # Temps d'attente total par véhicule (seulement ceux qui ont traversé)
        self.completed_wait_times = []
        
        # Statistiques par feu rouge - FIXED: Better tracking
        self.redlight_stats = {
            0: {
                'vehicles_stopped': 0,
                'wait_times': [],
                'current_waiting': 0,
                'total_wait_time': 0.0
            },
            1: {
                'vehicles_stopped': 0,
                'wait_times': [],
                'current_waiting': 0,
                'total_wait_time': 0.0
            },
            2: {
                'vehicles_stopped': 0,
                'wait_times': [],
                'current_waiting': 0,
                'total_wait_time': 0.0
            },
            3: {
                'vehicles_stopped': 0,
                'wait_times': [],
                'current_waiting': 0,
                'total_wait_time': 0.0
            }
        }
        
        # Temps d'attente au feu rouge par véhicule
        self.redlight_wait_times_all = []
        
    def record_vehicle_generation(self, direction, vehicle_type):
        """
        Enregistre la génération d'un nouveau véhicule
        
        Args:
            direction (str): Direction du véhicule
            vehicle_type (str): Type du véhicule
        """
        self.total_vehicles_generated += 1
        self.vehicles_by_direction[direction]['generated'] += 1
        self.vehicles_by_type[vehicle_type]['generated'] += 1
    
    def record_vehicle_crossing(self, direction, vehicle_type):
        """
        Enregistre le franchissement d'un véhicule
        
        Args:
            direction (str): Direction du véhicule
            vehicle_type (str): Type du véhicule
        """
        self.total_vehicles_crossed += 1
        self.vehicles_by_direction[direction]['crossed'] += 1
        self.vehicles_by_type[vehicle_type]['crossed'] += 1
    
    def record_signal_cycle(self, signal_index, green_duration):
        """
        Enregistre un cycle de feu vert
        
        Args:
            signal_index (int): Index du signal (0-3)
            green_duration (int): Durée du feu vert en secondes
        """
        self.signal_stats[signal_index]['green_times'].append(green_duration)
        self.signal_stats[signal_index]['total_green_time'] += green_duration
        
        if signal_index == 0:
            self.total_cycles_completed += 1
    
    def record_traffic_level(self, direction, level):
        """
        Enregistre le niveau de trafic pour une direction
        
        Args:
            direction (str): Direction
            level (int): Niveau de trafic (1-10)
        """
        self.traffic_history[direction].append({
            'timestamp': time.time() - self.start_time,
            'level': level
        })
    
    def record_completed_wait_time(self, total_wait_time):
        """
        Enregistre le temps d'attente TOTAL d'un véhicule qui vient de traverser
        
        Args:
            total_wait_time (float): Temps d'attente total en secondes
        """
        self.completed_wait_times.append(total_wait_time)
    
    def start_redlight_wait(self, signal_index):
        """
        FIXED: Enregistre qu'un véhicule commence à attendre au feu rouge
        Cette méthode est appelée UNE SEULE FOIS par véhicule
        
        Args:
            signal_index (int): Index du signal (0-3)
        """
        self.redlight_stats[signal_index]['vehicles_stopped'] += 1
    
    def end_redlight_wait(self, signal_index, wait_time):
        """
        FIXED: Enregistre la fin d'attente d'un véhicule au feu rouge
        
        Args:
            signal_index (int): Index du signal (0-3)
            wait_time (float): Temps passé au feu rouge en secondes
        """
        self.redlight_stats[signal_index]['wait_times'].append(wait_time)
        self.redlight_stats[signal_index]['total_wait_time'] += wait_time
        self.redlight_wait_times_all.append(wait_time)
    
    def update_current_waiting_count(self, signal_index, count):
        """
        Met à jour le nombre de véhicules actuellement en attente
        
        Args:
            signal_index (int): Index du signal (0-3)
            count (int): Nombre de véhicules en attente
        """
        self.redlight_stats[signal_index]['current_waiting'] = count
    
    def get_average_redlight_wait(self, signal_index):
        """
        Calcule le temps d'attente moyen au feu rouge pour un signal
        
        Args:
            signal_index (int): Index du signal (0-3)
            
        Returns:
            float: Temps moyen en secondes
        """
        wait_times = self.redlight_stats[signal_index]['wait_times']
        if wait_times:
            return sum(wait_times) / len(wait_times)
        return 0.0
    
    def get_global_average_redlight_wait(self):
        """
        Calcule le temps d'attente moyen global au feu rouge
        
        Returns:
            float: Temps moyen en secondes
        """
        if self.redlight_wait_times_all:
            return sum(self.redlight_wait_times_all) / len(self.redlight_wait_times_all)
        return 0.0
    
    def get_total_vehicles_stopped_at_redlight(self):
        """
        Retourne le nombre total de véhicules arrêtés aux feux rouges
        
        Returns:
            int: Nombre total de véhicules
        """
        total = 0
        for signal_stats in self.redlight_stats.values():
            total += signal_stats['vehicles_stopped']
        return total
    
    def get_current_vehicles_at_redlight(self, signal_index):
        """
        Retourne le nombre de véhicules actuellement bloqués
        
        Args:
            signal_index (int): Index du signal (0-3)
            
        Returns:
            int: Nombre de véhicules en attente
        """
        return self.redlight_stats[signal_index]['current_waiting']
    
    def get_average_green_time(self, signal_index):
        """
        Calcule le temps moyen au vert pour un signal
        
        Args:
            signal_index (int): Index du signal
            
        Returns:
            float: Temps moyen en secondes
        """
        green_times = self.signal_stats[signal_index]['green_times']
        if green_times:
            return sum(green_times) / len(green_times)
        return 0.0
    
    def get_average_waiting_time(self):
        """
        Calcule le temps d'attente moyen par véhicule
        
        Returns:
            float: Temps moyen en secondes
        """
        if self.completed_wait_times:
            return sum(self.completed_wait_times) / len(self.completed_wait_times)
        return 0.0
    
    def get_crossing_efficiency(self, direction):
        """
        Calcule l'efficacité de franchissement pour une direction
        
        Args:
            direction (str): Direction
            
        Returns:
            float: Pourcentage de véhicules ayant franchi
        """
        generated = self.vehicles_by_direction[direction]['generated']
        crossed = self.vehicles_by_direction[direction]['crossed']
        
        if generated > 0:
            return (crossed / generated) * 100
        return 0.0
    
    def get_simulation_duration(self):
        """
        Retourne la durée de la simulation
        
        Returns:
            float: Durée en secondes
        """
        return time.time() - self.start_time
    
    def get_average_traffic_level(self, direction):
        """
        Calcule le niveau de trafic moyen pour une direction
        
        Args:
            direction (str): Direction
            
        Returns:
            float: Niveau moyen (1-10)
        """
        history = self.traffic_history[direction]
        if history:
            levels = [entry['level'] for entry in history]
            return sum(levels) / len(levels)
        return 0.0
    
    def generate_report(self):
        """
        Génère un rapport complet des statistiques
        
        Returns:
            dict: Rapport structuré
        """
        duration = self.get_simulation_duration()
        
        return {
            'simulation_info': {
                'start_time': self.simulation_start.strftime('%Y-%m-%d %H:%M:%S'),
                'duration_seconds': round(duration, 2),
                'duration_formatted': self._format_duration(duration)
            },
            'global_stats': {
                'total_cycles': self.total_cycles_completed,
                'vehicles_generated': self.total_vehicles_generated,
                'vehicles_crossed': self.total_vehicles_crossed,
                'generation_rate': round(self.total_vehicles_generated / duration, 2) if duration > 0 else 0
            },
            'direction_stats': {
                direction: {
                    'generated': stats['generated'],
                    'crossed': stats['crossed'],
                    'efficiency': round(self.get_crossing_efficiency(direction), 2),
                    'avg_traffic_level': round(self.get_average_traffic_level(direction), 2)
                }
                for direction, stats in self.vehicles_by_direction.items()
            },
            'vehicle_type_stats': {
                vtype: {
                    'generated': stats['generated'],
                    'crossed': stats['crossed'],
                    'percentage': round((stats['generated'] / self.total_vehicles_generated * 100), 2) 
                                 if self.total_vehicles_generated > 0 else 0
                }
                for vtype, stats in self.vehicles_by_type.items()
            },
            'signal_stats': {
                f'signal_{i}': {
                    'avg_green_time': round(self.get_average_green_time(i), 2),
                    'total_green_time': stats['total_green_time'],
                    'cycles_count': len(stats['green_times'])
                }
                for i, stats in self.signal_stats.items()
            },
            'waiting_stats': {
                'average_waiting_time': round(self.get_average_waiting_time(), 2),
                'average_waiting_time': round(self.get_average_waiting_time(), 2),
                'total_samples': len(self.completed_wait_times)
            },
            'redlight_stats': {
                f'signal_{i}': {
                    'vehicles_stopped': rl_stats['vehicles_stopped'],
                    'currently_waiting': rl_stats['current_waiting'],
                    'avg_wait_time': round(self.get_average_redlight_wait(i), 2),
                    'total_wait_samples': len(rl_stats['wait_times']),
                    'total_wait_time': round(rl_stats['total_wait_time'], 2)
                }
                for i, rl_stats in self.redlight_stats.items()
            },
            'global_redlight_stats': {
                'total_vehicles_stopped': self.get_total_vehicles_stopped_at_redlight(),
                'average_wait_time': round(self.get_global_average_redlight_wait(), 2),
                'total_wait_samples': len(self.redlight_wait_times_all)
            }
        }
    
    def _format_duration(self, seconds):
        """
        Formate la durée en format lisible
        
        Args:
            seconds (float): Durée en secondes
            
        Returns:
            str: Durée formatée (ex: "1h 23m 45s")
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def print_summary(self):
        """Affiche un résumé des statistiques dans la console"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("RAPPORT DE STATISTIQUES DE SIMULATION")
        print("="*60)
        
        print(f"\nDemarrage: {report['simulation_info']['start_time']}")
        print(f"Duree: {report['simulation_info']['duration_formatted']}")
        
        print(f"\n--- STATISTIQUES GLOBALES ---")
        print(f"Cycles completes: {report['global_stats']['total_cycles']}")
        print(f"Vehicules generes: {report['global_stats']['vehicles_generated']}")
        print(f"Vehicules passes: {report['global_stats']['vehicles_crossed']}")
        print(f"Taux de generation: {report['global_stats']['generation_rate']} vehicules/seconde")
        
        print(f"\n--- PAR DIRECTION ---")
        for direction, stats in report['direction_stats'].items():
            print(f"{direction.upper()}:")
            print(f"  Generes: {stats['generated']}, Passes: {stats['crossed']}")
            print(f"  Efficacite: {stats['efficiency']}%")
            print(f"  Niveau de trafic moyen: {stats['avg_traffic_level']}/10")
        
        print(f"\n--- PAR TYPE DE VEHICULE ---")
        for vtype, stats in report['vehicle_type_stats'].items():
            print(f"{vtype.upper()}: {stats['generated']} ({stats['percentage']}%)")
        
        print(f"\n--- SIGNAUX ---")
        for signal, stats in report['signal_stats'].items():
            print(f"{signal}: Temps vert moyen = {stats['avg_green_time']}s, "
                  f"Cycles = {stats['cycles_count']}")
        
        print(f"\n--- TEMPS D'ATTENTE GENERAL ---")
        print(f"Temps d'attente moyen: {report['waiting_stats']['average_waiting_time']}s")
        
        print(f"\n--- STATISTIQUES FEUX ROUGES (DETAILLE) ---")
        print(f"Total vehicules arretes au rouge: {report['global_redlight_stats']['total_vehicles_stopped']}")
        print(f"Temps d'attente moyen au feu rouge: {report['global_redlight_stats']['average_wait_time']}s")
        print(f"Nombre total d'arrets au rouge enregistres: {report['global_redlight_stats']['total_wait_samples']}")
        
        print(f"\nPar signal:")
        directions = {0: 'RIGHT', 1: 'DOWN', 2: 'LEFT', 3: 'UP'}
        for i in range(4):
            signal = f'signal_{i}'
            stats = report['redlight_stats'][signal]
            print(f"  Signal {i} ({directions[i]}):")
            print(f"    Vehicules arretes: {stats['vehicles_stopped']}")
            print(f"    Actuellement en attente: {stats['currently_waiting']}")
            print(f"    Temps d'attente moyen: {stats['avg_wait_time']}s")
            print(f"    Temps total d'attente: {stats['total_wait_time']}s")
            print(f"    Nombre d'arrets complets: {stats['total_wait_samples']}")
        
        print("="*60 + "\n")
    
    def export_to_file(self, filename="simulation_stats.txt"):
        """
        Exporte les statistiques dans un fichier texte
        
        Args:
            filename (str): Nom du fichier de sortie
        """
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("RAPPORT DE STATISTIQUES DE SIMULATION\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Demarrage: {report['simulation_info']['start_time']}\n")
            f.write(f"Duree: {report['simulation_info']['duration_formatted']}\n\n")
            
            f.write("--- STATISTIQUES GLOBALES ---\n")
            for key, value in report['global_stats'].items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n--- PAR DIRECTION ---\n")
            for direction, stats in report['direction_stats'].items():
                f.write(f"\n{direction.upper()}:\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
            
            f.write("\n--- PAR TYPE DE VEHICULE ---\n")
            for vtype, stats in report['vehicle_type_stats'].items():
                f.write(f"\n{vtype.upper()}:\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
            
            f.write("\n--- SIGNAUX ---\n")
            for signal, stats in report['signal_stats'].items():
                f.write(f"\n{signal}:\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
            
            f.write("\n--- TEMPS D'ATTENTE GENERAL ---\n")
            for key, value in report['waiting_stats'].items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n--- STATISTIQUES FEUX ROUGES ---\n")
            f.write(f"\nGlobal:\n")
            for key, value in report['global_redlight_stats'].items():
                f.write(f"  {key}: {value}\n")
            
            f.write(f"\nPar signal:\n")
            directions = {0: 'RIGHT', 1: 'DOWN', 2: 'LEFT', 3: 'UP'}
            for i in range(4):
                signal = f'signal_{i}'
                stats = report['redlight_stats'][signal]
                f.write(f"\nSignal {i} ({directions[i]}):\n")
                for key, value in stats.items():
                    f.write(f"  {key}: {value}\n")
        
        print(f"[OK] Statistiques exportees vers {filename}")