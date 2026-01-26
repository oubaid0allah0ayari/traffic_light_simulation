"""
Manager classes for traffic simulation
Contains SignalManager, VehicleManager, and SimulationManager
Version with refactored signal control for DQN integration
"""
import random
import time
import threading
import pygame
from models import TrafficSignal, Vehicle
from statistics import StatisticsCollector
from config import *


class SignalManager:
    """Manages all traffic signals in the simulation"""
    
    def __init__(self, stats_collector=None):
        self.signals = []
        self.current_green = 0
        self.next_green = 1
        self.current_yellow = 0
        self.stats_collector = stats_collector
        
        # Control mode: 'auto' for automatic cycling, 'manual' for DQN control
        self.control_mode = 'auto'
        
        self._initialize_signals()
    
    def _initialize_signals(self):
        """Initialize all traffic signals with default or random values"""
        min_time = RANDOM_GREEN_SIGNAL_TIMER_RANGE[0]
        max_time = RANDOM_GREEN_SIGNAL_TIMER_RANGE[1]
        
        if RANDOM_GREEN_SIGNAL_TIMER:
            ts1 = TrafficSignal(0, DEFAULT_YELLOW, random.randint(min_time, max_time), 0)
            self.signals.append(ts1)
            
            ts2 = TrafficSignal(
                ts1.red + ts1.yellow + ts1.green,
                DEFAULT_YELLOW,
                random.randint(min_time, max_time),
                1
            )
            self.signals.append(ts2)
            
            ts3 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, 
                              random.randint(min_time, max_time), 2)
            self.signals.append(ts3)
            
            ts4 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, 
                              random.randint(min_time, max_time), 3)
            self.signals.append(ts4)
        else:
            ts1 = TrafficSignal(0, DEFAULT_YELLOW, DEFAULT_GREEN[0], 0)
            self.signals.append(ts1)
            
            ts2 = TrafficSignal(
                ts1.yellow + ts1.green,
                DEFAULT_YELLOW,
                DEFAULT_GREEN[1],
                1
            )
            self.signals.append(ts2)
            
            ts3 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN[2], 2)
            self.signals.append(ts3)
            
            ts4 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN[3], 3)
            self.signals.append(ts4)
    
    def update(self):
        """Update all signal timers"""
        for i in range(NO_OF_SIGNALS):
            is_current = (i == self.current_green)
            self.signals[i].update_timers(is_current, self.current_yellow)
    
    # ========================================
    # COMMAND FUNCTIONS FOR DQN AGENT
    # ========================================
    
    def set_control_mode(self, mode):
        """
        Set the control mode
        
        Args:
            mode (str): 'auto' for automatic cycling, 'manual' for DQN control
        """
        if mode in ['auto', 'manual']:
            self.control_mode = mode
            print(f"[SignalManager] Control mode set to: {mode}")
        else:
            raise ValueError("Mode must be 'auto' or 'manual'")
    
    def activate_green_signal(self, signal_index, duration=None, vehicles_dict=None):
        """
        Activate green light for a specific signal
        This is the main function that DQN agent will call
        
        Args:
            signal_index (int): Index of signal to activate (0-3)
            duration (int, optional): Duration of green light in seconds
                                     If None, uses default/random duration
            vehicles_dict (dict, optional): Vehicle dictionary for resetting stops
        
        Returns:
            bool: True if activation successful, False otherwise
        """
        if signal_index < 0 or signal_index >= NO_OF_SIGNALS:
            print(f"[Error] Invalid signal index: {signal_index}")
            return False
        
        # If same signal is already green, just return
        if self.current_green == signal_index and self.current_yellow == 0:
            print(f"[Info] Signal {signal_index} is already green")
            return True
        
        # Start yellow phase for current signal first
        if self.current_yellow == 0:
            self._start_yellow_phase()
            return False  # Signal not yet green, in transition
        
        # Complete the transition to new green signal
        self._complete_signal_transition(signal_index, duration, vehicles_dict)
        return True
    
    def _start_yellow_phase(self):
        """Start the yellow (orange) phase for current signal"""
        self.current_yellow = 1
        print(f"[Signal] Signal {self.current_green} entering YELLOW phase")
    
    def _complete_signal_transition(self, new_signal_index, duration=None, vehicles_dict=None):
        """
        Complete transition to a new green signal
        
        Args:
            new_signal_index (int): Index of new signal to activate
            duration (int, optional): Duration for green phase
            vehicles_dict (dict, optional): Vehicle dictionary
        """
        # Record cycle completion
        if self.stats_collector:
            green_duration = self.signals[self.current_green].initial_green
            self.stats_collector.record_signal_cycle(
                self.current_green, 
                green_duration
            )
        
        # Reset stop coordinates for current green direction
        if vehicles_dict:
            for i in range(3):
                direction = DIRECTION_NUMBERS[self.current_green]
                for vehicle in vehicles_dict[direction][i]:
                    vehicle.stop = DEFAULT_STOP[direction]
        
        # Reset current signal timers
        self._reset_current_signal_timers()
        
        # Activate new signal
        self.current_green = new_signal_index
        self.next_green = (self.current_green + 1) % NO_OF_SIGNALS
        self.current_yellow = 0
        
        # Set green duration if provided
        if duration is not None:
            self.signals[self.current_green].green = duration
            self.signals[self.current_green].initial_green = duration
        
        # Set red time for next signal
        self.signals[self.next_green].red = (
            self.signals[self.current_green].yellow + 
            self.signals[self.current_green].green
        )
        
        print(f"[Signal] Signal {self.current_green} activated GREEN for {self.signals[self.current_green].green}s")
    
    def _reset_current_signal_timers(self):
        """Reset timers for the current signal"""
        if RANDOM_GREEN_SIGNAL_TIMER:
            self.signals[self.current_green].reset_green(
                random.randint(RANDOM_GREEN_SIGNAL_TIMER_RANGE[0],
                             RANDOM_GREEN_SIGNAL_TIMER_RANGE[1])
            )
        else:
            self.signals[self.current_green].reset_green(
                DEFAULT_GREEN[self.current_green]
            )
        
        self.signals[self.current_green].reset_timers(
            yellow=DEFAULT_YELLOW,
            red=DEFAULT_RED
        )
    
    def force_switch_to_next(self, vehicles_dict=None):
        """
        Force immediate switch to next signal
        Useful for DQN agent to override current timing
        
        Args:
            vehicles_dict (dict, optional): Vehicle dictionary
        """
        # Force green timer to 0 to trigger switch
        self.signals[self.current_green].green = 0
        print(f"[Signal] Forcing switch from signal {self.current_green}")
    
    def extend_green_duration(self, additional_seconds):
        """
        Extend the current green light duration
        Useful for DQN agent to adapt to traffic conditions
        
        Args:
            additional_seconds (int): Number of seconds to add
        
        Returns:
            int: New total green duration
        """
        if self.current_yellow == 0:  # Only if currently green
            self.signals[self.current_green].green += additional_seconds
            new_duration = self.signals[self.current_green].green
            print(f"[Signal] Extended signal {self.current_green} by {additional_seconds}s (new: {new_duration}s)")
            return new_duration
        return 0
    
    def reduce_green_duration(self, reduce_seconds):
        """
        Reduce the current green light duration
        
        Args:
            reduce_seconds (int): Number of seconds to remove
        
        Returns:
            int: New total green duration
        """
        if self.current_yellow == 0:  # Only if currently green
            new_duration = max(3, self.signals[self.current_green].green - reduce_seconds)
            self.signals[self.current_green].green = new_duration
            print(f"[Signal] Reduced signal {self.current_green} by {reduce_seconds}s (new: {new_duration}s)")
            return new_duration
        return 0
    
    def get_current_signal_state(self):
        """
        Get the current state of all signals
        Useful for DQN agent to observe the environment
        
        Returns:
            dict: State information for all signals
        """
        return {
            'current_green': self.current_green,
            'current_yellow': self.current_yellow,
            'next_green': self.next_green,
            'control_mode': self.control_mode,
            'signals': [
                {
                    'index': i,
                    'red': self.signals[i].red,
                    'yellow': self.signals[i].yellow,
                    'green': self.signals[i].green,
                    'is_green': (i == self.current_green and self.current_yellow == 0),
                    'is_yellow': (i == self.current_green and self.current_yellow == 1),
                    'is_red': (i != self.current_green)
                }
                for i in range(NO_OF_SIGNALS)
            ]
        }
    
    # ========================================
    # ORIGINAL AUTOMATIC SWITCHING LOGIC
    # (Used when control_mode = 'auto')
    # ========================================
    
    def switch_signal(self, vehicles_dict):
        """
        Handle automatic signal switching logic
        This is called by the automatic thread
        
        Args:
            vehicles_dict: Dictionary of all vehicles
        """
        # Only proceed with automatic switching if in auto mode
        if self.control_mode != 'auto':
            return
        
        # Record cycle completion in statistics
        if self.stats_collector:
            green_duration = self.signals[self.current_green].initial_green
            self.stats_collector.record_signal_cycle(
                self.current_green, 
                green_duration
            )
        
        # Reset stop coordinates for current green direction
        for i in range(3):
            direction = DIRECTION_NUMBERS[self.current_green]
            for vehicle in vehicles_dict[direction][i]:
                vehicle.stop = DEFAULT_STOP[direction]
        
        # Reset current signal timers
        if RANDOM_GREEN_SIGNAL_TIMER:
            self.signals[self.current_green].reset_green(
                random.randint(RANDOM_GREEN_SIGNAL_TIMER_RANGE[0],
                             RANDOM_GREEN_SIGNAL_TIMER_RANGE[1])
            )
        else:
            self.signals[self.current_green].reset_green(
                DEFAULT_GREEN[self.current_green]
            )
        
        self.signals[self.current_green].reset_timers(
            yellow=DEFAULT_YELLOW,
            red=DEFAULT_RED
        )
        
        # Switch to next signal
        self.current_green = self.next_green
        self.next_green = (self.current_green + 1) % NO_OF_SIGNALS
        
        # Set red time for next signal
        self.signals[self.next_green].red = (
            self.signals[self.current_green].yellow + 
            self.signals[self.current_green].green
        )


class VehicleManager:
    """Manages all vehicles in the simulation"""
    
    def __init__(self, stats_collector=None):
        self.vehicles = {
            'right': {0: [], 1: [], 2: [], 'crossed': 0},
            'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0},
            'up': {0: [], 1: [], 2: [], 'crossed': 0}
        }
        
        self.vehicles_turned = {
            'right': {1: [], 2: []},
            'down': {1: [], 2: []},
            'left': {1: [], 2: []},
            'up': {1: [], 2: []}
        }
        
        self.vehicles_not_turned = {
            'right': {1: [], 2: []},
            'down': {1: [], 2: []},
            'left': {1: [], 2: []},
            'up': {1: [], 2: []}
        }
        
        self.x_coords = {k: v.copy() for k, v in X_COORDINATES.items()}
        self.y_coords = {k: v.copy() for k, v in Y_COORDINATES.items()}
        
        self.allowed_vehicle_types_list = []
        self._setup_allowed_vehicles()
        
        self.simulation_group = pygame.sprite.Group()
        self.stats_collector = stats_collector
    
    def _setup_allowed_vehicles(self):
        """Setup list of allowed vehicle types"""
        for i, vehicle_type in enumerate(ALLOWED_VEHICLE_TYPES):
            if ALLOWED_VEHICLE_TYPES[vehicle_type]:
                self.allowed_vehicle_types_list.append(i)
    
    def generate_vehicle(self):
        """Generate a single random vehicle"""
        vehicle_type = random.choice(self.allowed_vehicle_types_list)
        lane_number = random.randint(1, 2)
        
        # Determine if vehicle will turn
        will_turn = 0
        if lane_number in [1, 2]:
            if random.randint(0, 99) < TURN_PROBABILITY:
                will_turn = 1
        
        # Determine direction
        temp = random.randint(0, 99)
        direction_number = 0
        
        for i, dist in enumerate(DIRECTION_DISTRIBUTION):
            if temp < dist:
                direction_number = i
                break
        
        # Create vehicle
        vehicle = Vehicle(
            lane_number,
            VEHICLE_TYPES[vehicle_type],
            direction_number,
            DIRECTION_NUMBERS[direction_number],
            will_turn,
            self.vehicles,
            self.x_coords,
            self.y_coords,
            self.stats_collector
        )
        
        self.simulation_group.add(vehicle)
        return vehicle
    
    def update_vehicles(self, current_green, current_yellow):
        """Update all vehicles in the simulation"""
        for vehicle in self.simulation_group:
            vehicle.move(
                current_green,
                current_yellow,
                self.vehicles,
                self.vehicles_turned,
                self.vehicles_not_turned
            )
    
    def calculate_traffic_level(self, direction):
        """
        Calculate traffic level for a direction (1-10)
        
        Args:
            direction (str): Direction to analyze
            
        Returns:
            int: Traffic level from 1 to 10
        """
        waiting_vehicles = 0
        for lane in range(3):
            for vehicle in self.vehicles[direction][lane]:
                if vehicle.crossed == 0:
                    waiting_vehicles += 1
        
        # Normalize to 1-10 scale
        traffic_level = min(10, max(1, waiting_vehicles // 2))
        
        # Record in statistics
        if self.stats_collector:
            self.stats_collector.record_traffic_level(direction, traffic_level)
        
        return traffic_level
    
    def count_vehicles_at_redlight(self, signal_index):
        """
        Count vehicles currently waiting at red light
        
        Args:
            signal_index (int): Index of the signal (0-3)
            
        Returns:
            int: Number of vehicles waiting
        """
        direction = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}[signal_index]
        
        count = 0
        for lane in range(3):
            for vehicle in self.vehicles[direction][lane]:
                if vehicle.crossed == 0 and vehicle.is_waiting_at_redlight:
                    count += 1
        
        # Update in statistics
        if self.stats_collector:
            self.stats_collector.update_current_waiting_count(signal_index, count)
        
        return count
    
    def get_traffic_state_for_dqn(self):
        """
        Get traffic state information formatted for DQN agent
        
        Returns:
            dict: Traffic state for all directions
        """
        state = {}
        for direction in ['right', 'down', 'left', 'up']:
            waiting = 0
            total = 0
            for lane in range(3):
                for vehicle in self.vehicles[direction][lane]:
                    total += 1
                    if vehicle.crossed == 0:
                        waiting += 1
            
            state[direction] = {
                'waiting': waiting,
                'total': total,
                'crossed': self.vehicles[direction]['crossed'],
                'traffic_level': self.calculate_traffic_level(direction)
            }
        
        return state


class SimulationManager:
    """Main manager that coordinates the entire simulation"""
    
    def __init__(self, control_mode='auto'):
        """
        Initialize simulation manager
        
        Args:
            control_mode (str): 'auto' for automatic control, 'manual' for DQN
        """
        pygame.init()
        
        # Create statistics collector
        self.stats_collector = StatisticsCollector()
        
        # Create managers with stats
        self.signal_manager = SignalManager(self.stats_collector)
        self.signal_manager.set_control_mode(control_mode)
        
        self.vehicle_manager = VehicleManager(self.stats_collector)
        
        # Setup display
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("TRAFFIC SIMULATION")
        
        # Load images
        self.background = pygame.image.load(IMAGE_PATHS['background'])
        self.red_signal = pygame.image.load(IMAGE_PATHS['red_signal'])
        self.yellow_signal = pygame.image.load(IMAGE_PATHS['yellow_signal'])
        self.green_signal = pygame.image.load(IMAGE_PATHS['green_signal'])
        
        # Setup fonts
        self.font = pygame.font.Font(None, 30)
        self.stats_font = pygame.font.Font(None, 24)
        
        # Control flags
        self.running = True
        self.clock = pygame.time.Clock()
        self.show_stats = True
        
        # Stats update timer
        self.last_stats_update = time.time()
        self.stats_update_interval = 5
        
        # Start threads
        self._start_threads()
    
    def _start_threads(self):
        """Start background threads for signal timing and vehicle generation"""
        signal_thread = threading.Thread(
            name="signal_control",
            target=self._signal_control_loop,
            daemon=True
        )
        signal_thread.start()
        
        vehicle_thread = threading.Thread(
            name="vehicle_generation",
            target=self._vehicle_generation_loop,
            daemon=True
        )
        vehicle_thread.start()
    
    def _signal_control_loop(self):
        """Background thread for controlling signal timing"""
        while self.running:
            # Only run automatic control if in auto mode
            if self.signal_manager.control_mode != 'auto':
                time.sleep(0.1)  # Small sleep to prevent busy waiting
                continue
            
            # Green signal phase
            while self.signal_manager.signals[
                self.signal_manager.current_green].green > 0:
                self.signal_manager.update()
                time.sleep(1)
            
            # Yellow signal phase
            self.signal_manager.current_yellow = 1
            while self.signal_manager.signals[
                self.signal_manager.current_green].yellow > 0:
                self.signal_manager.update()
                time.sleep(1)
            
            # Switch to next signal
            self.signal_manager.current_yellow = 0
            self.signal_manager.switch_signal(self.vehicle_manager.vehicles)
    
    def _vehicle_generation_loop(self):
        """Background thread for generating vehicles"""
        while self.running:
            self.vehicle_manager.generate_vehicle()
            time.sleep(1)
    
    def render(self):
        """Render all simulation elements"""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw signals
        for i in range(NO_OF_SIGNALS):
            signal = self.signal_manager.signals[i]
            
            if i == self.signal_manager.current_green:
                if self.signal_manager.current_yellow == 1:
                    signal.signal_text = signal.yellow
                    self.screen.blit(self.yellow_signal, SIGNAL_COORDS[i])
                else:
                    signal.signal_text = signal.green
                    self.screen.blit(self.green_signal, SIGNAL_COORDS[i])
            else:
                if signal.red <= 10:
                    signal.signal_text = signal.red
                else:
                    signal.signal_text = "---"
                self.screen.blit(self.red_signal, SIGNAL_COORDS[i])
        
        # Draw signal timers
        for i in range(NO_OF_SIGNALS):
            signal = self.signal_manager.signals[i]
            signal_text = self.font.render(
                str(signal.signal_text), True, WHITE, BLACK
            )
            self.screen.blit(signal_text, SIGNAL_TIMER_COORDS[i])
        
        # Draw vehicles
        for vehicle in self.vehicle_manager.simulation_group:
            self.screen.blit(vehicle.image, [vehicle.x, vehicle.y])
        
        # Draw statistics overlay
        if self.show_stats:
            self._render_stats_overlay()
    
    def _render_stats_overlay(self):
        """Render statistics overlay on screen"""
        overlay = pygame.Surface((400, 450))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (10, 10))
        
        report = self.stats_collector.generate_report()
        y_offset = 20
        
        # Title with control mode
        mode_color = (0, 255, 0) if self.signal_manager.control_mode == 'auto' else (255, 165, 0)
        title = self.stats_font.render(
            f"STATS [{self.signal_manager.control_mode.upper()}]", 
            True, mode_color
        )
        self.screen.blit(title, (20, y_offset))
        y_offset += 30
        
        cycles_text = self.stats_font.render(
            f"Cycles: {report['global_stats']['total_cycles']}", 
            True, WHITE
        )
        self.screen.blit(cycles_text, (20, y_offset))
        y_offset += 25
        
        gen_text = self.stats_font.render(
            f"Generes: {report['global_stats']['vehicles_generated']}", 
            True, WHITE
        )
        self.screen.blit(gen_text, (20, y_offset))
        y_offset += 25
        
        cross_text = self.stats_font.render(
            f"Passes: {report['global_stats']['vehicles_crossed']}", 
            True, WHITE
        )
        self.screen.blit(cross_text, (20, y_offset))
        y_offset += 25
        
        duration_text = self.stats_font.render(
            f"Duree: {report['simulation_info']['duration_formatted']}", 
            True, WHITE
        )
        self.screen.blit(duration_text, (20, y_offset))
        y_offset += 30
        
        # Red light statistics
        redlight_title = self.stats_font.render("Feux Rouges:", True, (255, 100, 100))
        self.screen.blit(redlight_title, (20, y_offset))
        y_offset += 25
        
        total_stopped = report['global_redlight_stats']['total_vehicles_stopped']
        avg_wait = report['global_redlight_stats']['average_wait_time']
        
        stopped_text = self.stats_font.render(
            f"Total arretes: {total_stopped}",
            True, WHITE
        )
        self.screen.blit(stopped_text, (30, y_offset))
        y_offset += 20
        
        avg_text = self.stats_font.render(
            f"Attente moy: {avg_wait:.1f}s",
            True, WHITE
        )
        self.screen.blit(avg_text, (30, y_offset))
        y_offset += 30
        
        dir_title = self.stats_font.render("Par direction:", True, (255, 255, 0))
        self.screen.blit(dir_title, (20, y_offset))
        y_offset += 25
        
        for i, (direction, stats) in enumerate(report['direction_stats'].items()):
            dir_text = self.stats_font.render(
                f"{direction[:1].upper()}: {stats['crossed']} ({stats['efficiency']:.0f}%)",
                True, WHITE
            )
            self.screen.blit(dir_text, (30, y_offset))
            y_offset += 20
            
            current_waiting = report['redlight_stats'][f'signal_{i}']['currently_waiting']
            if current_waiting > 0:
                waiting_text = self.stats_font.render(
                    f"  {current_waiting} en attente",
                    True, (255, 100, 100)
                )
                self.screen.blit(waiting_text, (35, y_offset))
                y_offset += 20
    
    def update(self):
        """Update simulation state"""
        self.vehicle_manager.update_vehicles(
            self.signal_manager.current_green,
            self.signal_manager.current_yellow
        )
        
        # Update traffic levels periodically
        current_time = time.time()
        if current_time - self.last_stats_update >= self.stats_update_interval:
            for direction in DIRECTION_NUMBERS.values():
                self.vehicle_manager.calculate_traffic_level(direction)
            
            # Update red light vehicle count
            for i in range(NO_OF_SIGNALS):
                self.vehicle_manager.count_vehicles_at_redlight(i)
            
            self.last_stats_update = current_time
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.show_stats = not self.show_stats
                elif event.key == pygame.K_p:
                    self.stats_collector.print_summary()
                elif event.key == pygame.K_e:
                    self.stats_collector.export_to_file()
                elif event.key == pygame.K_m:
                    # Toggle control mode
                    new_mode = 'manual' if self.signal_manager.control_mode == 'auto' else 'auto'
                    self.signal_manager.set_control_mode(new_mode)
        return True
    
    def run(self):
        """Main simulation loop"""
        print("\nControls:")
        print("  S - Toggle statistics display")
        print("  P - Print statistics to console")
        print("  E - Export statistics to file")
        print("  M - Toggle Manual/Auto control mode")
        print("  Close window to exit\n")
        
        while self.running:
            if not self.handle_events():
                break
            
            self.update()
            self.render()
            
            pygame.display.update()
            self.clock.tick(FPS)
        
        # Print final stats before exit
        print("\n" + "="*60)
        print("SIMULATION TERMINEE - STATISTIQUES FINALES")
        print("="*60)
        self.stats_collector.print_summary()
        self.stats_collector.export_to_file("simulation_finale.txt")
        
        pygame.quit()