"""
Model classes for traffic simulation - FIXED VERSION
Contains TrafficSignal and Vehicle classes with accurate statistics tracking
"""
import pygame
import time
from config import *


class TrafficSignal:
    """Represents a traffic signal with red, yellow, and green timers"""
    
    def __init__(self, red, yellow, green, signal_index):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signal_text = ""
        self.signal_index = signal_index
        self.cycle_start_time = None
        self.initial_green = green
    
    def update_timers(self, is_current_green, is_yellow_active):
        """Update signal timers based on current state"""
        if is_current_green:
            if is_yellow_active:
                self.yellow -= 1
            else:
                self.green -= 1
        else:
            self.red -= 1
    
    def reset_green(self, green_time):
        """Reset green timer to specified value"""
        self.green = green_time
        self.initial_green = green_time
    
    def reset_timers(self, red=None, yellow=None, green=None):
        """Reset all timers to specified values"""
        if red is not None:
            self.red = red
        if yellow is not None:
            self.yellow = yellow
        if green is not None:
            self.green = green
            self.initial_green = green


class Vehicle(pygame.sprite.Sprite):
    """Represents a vehicle in the simulation"""
    
    def __init__(self, lane, vehicle_class, direction_number, direction, 
                 will_turn, vehicles_dict, x_coords, y_coords, stats_collector=None):
        pygame.sprite.Sprite.__init__(self)
        
        # Basic properties
        self.lane = lane
        self.vehic_class = vehicle_class
        self.vehicle_class = vehicle_class
        self.speed = SPEEDS[vehicle_class]
        self.direction_number = direction_number
        self.direction = direction
        self.will_turn = will_turn
        
        # Position properties
        self.x = x_coords[direction][lane]
        self.y = y_coords[direction][lane]
        
        # State properties
        self.crossed = 0
        self.turned = 0
        self.rotate_angle = 0
        
        # Statistics tracking
        self.stats_collector = stats_collector
        self.spawn_time = time.time()
        self.wait_start_time = None
        self.total_wait_time = 0
        self.is_waiting = False
        
        # Red light specific tracking - FIXED
        self.redlight_wait_start = None
        self.is_waiting_at_redlight = False
        self.has_stopped_at_redlight = False
        
        # Add to vehicles dictionary
        vehicles_dict[direction][lane].append(self)
        self.index = len(vehicles_dict[direction][lane]) - 1
        self.crossed_index = 0
        
        # Load images
        path = f"images/{direction}/{vehicle_class}.png"
        self.original_image = pygame.image.load(path)
        self.image = pygame.image.load(path)
        
        # Calculate stop position
        self._calculate_stop_position(vehicles_dict)
        
        # Update spawn coordinates
        self._update_spawn_coordinates(x_coords, y_coords)
        
        # Record generation
        if self.stats_collector:
            self.stats_collector.record_vehicle_generation(direction, vehicle_class)
    
    def _calculate_stop_position(self, vehicles_dict):
        """Calculate where this vehicle should stop"""
        if len(vehicles_dict[self.direction][self.lane]) > 1:
            prev_vehicle = vehicles_dict[self.direction][self.lane][self.index - 1]
            
            if prev_vehicle.crossed == 0:
                if self.direction == 'right':
                    self.stop = (prev_vehicle.stop - 
                               prev_vehicle.image.get_rect().width - 
                               STOPPING_GAP)
                elif self.direction == 'left':
                    self.stop = (prev_vehicle.stop + 
                               prev_vehicle.image.get_rect().width + 
                               STOPPING_GAP)
                elif self.direction == 'down':
                    self.stop = (prev_vehicle.stop - 
                               prev_vehicle.image.get_rect().height - 
                               STOPPING_GAP)
                elif self.direction == 'up':
                    self.stop = (prev_vehicle.stop + 
                               prev_vehicle.image.get_rect().height + 
                               STOPPING_GAP)
            else:
                self.stop = DEFAULT_STOP[self.direction]
        else:
            self.stop = DEFAULT_STOP[self.direction]
    
    def _update_spawn_coordinates(self, x_coords, y_coords):
        """Update spawn coordinates for next vehicle"""
        if self.direction == 'right':
            temp = self.image.get_rect().width + STOPPING_GAP
            x_coords[self.direction][self.lane] -= temp
        elif self.direction == 'left':
            temp = self.image.get_rect().width + STOPPING_GAP
            x_coords[self.direction][self.lane] += temp
        elif self.direction == 'down':
            temp = self.image.get_rect().height + STOPPING_GAP
            y_coords[self.direction][self.lane] -= temp
        elif self.direction == 'up':
            temp = self.image.get_rect().height + STOPPING_GAP
            y_coords[self.direction][self.lane] += temp
    
    def render(self, screen):
        """Render vehicle on screen"""
        screen.blit(self.image, (self.x, self.y))
    
    def _start_waiting(self):
        """Start tracking waiting time"""
        if not self.is_waiting:
            self.is_waiting = True
            self.wait_start_time = time.time()
    
    def _stop_waiting(self):
        """Stop tracking waiting time and record it"""
        if self.is_waiting:
            self.is_waiting = False
            wait_duration = time.time() - self.wait_start_time
            self.total_wait_time += wait_duration
    
    def _start_redlight_wait(self):
        """Start tracking red light wait time - FIXED LOGIC"""
        if not self.is_waiting_at_redlight and self.crossed == 0:
            self.is_waiting_at_redlight = True
            self.redlight_wait_start = time.time()
            
            if not self.has_stopped_at_redlight and self.stats_collector:
                self.has_stopped_at_redlight = True
                self.stats_collector.start_redlight_wait(self.direction_number)
    
    def _stop_redlight_wait(self):
        """Stop tracking red light wait and record it - FIXED LOGIC"""
        if self.is_waiting_at_redlight and self.redlight_wait_start is not None:
            self.is_waiting_at_redlight = False
            redlight_wait_duration = time.time() - self.redlight_wait_start
            
            if self.stats_collector:
                self.stats_collector.end_redlight_wait(
                    self.direction_number, 
                    redlight_wait_duration
                )
            
            self.redlight_wait_start = None
    
    def move(self, current_green, current_yellow, vehicles_dict, 
             vehicles_turned, vehicles_not_turned):
        """Move vehicle based on traffic rules and direction"""
        if self.direction == 'right':
            self._move_right(current_green, current_yellow, vehicles_dict,
                           vehicles_turned, vehicles_not_turned)
        elif self.direction == 'down':
            self._move_down(current_green, current_yellow, vehicles_dict,
                          vehicles_turned, vehicles_not_turned)
        elif self.direction == 'left':
            self._move_left(current_green, current_yellow, vehicles_dict,
                          vehicles_turned, vehicles_not_turned)
        elif self.direction == 'up':
            self._move_up(current_green, current_yellow, vehicles_dict,
                        vehicles_turned, vehicles_not_turned)
    
    def _check_crossing(self, vehicles_dict, vehicles_not_turned):
        """Check and handle vehicle crossing the stop line"""
        if self.crossed == 0:
            should_cross = False
            
            if self.direction == 'right':
                should_cross = (self.x + self.image.get_rect().width > 
                              STOP_LINES[self.direction])
            elif self.direction == 'down':
                should_cross = (self.y + self.image.get_rect().height > 
                              STOP_LINES[self.direction])
            elif self.direction == 'left':
                should_cross = self.x < STOP_LINES[self.direction]
            elif self.direction == 'up':
                should_cross = self.y < STOP_LINES[self.direction]
            
            if should_cross:
                self.crossed = 1
                vehicles_dict[self.direction]['crossed'] += 1
                
                if self.stats_collector:
                    self.stats_collector.record_vehicle_crossing(
                        self.direction, 
                        self.vehicle_class
                    )
                    self.stats_collector.record_completed_wait_time(self.total_wait_time)
                
                self._stop_waiting()
                if self.is_waiting_at_redlight:
                    self._stop_redlight_wait()
                
                if self.will_turn == 0:
                    vehicles_not_turned[self.direction][self.lane].append(self)
                    self.crossed_index = len(
                        vehicles_not_turned[self.direction][self.lane]) - 1
    
    def _is_at_stop_position(self):
        """Check if vehicle is at its stop position"""
        if self.direction == 'right':
            return self.x + self.image.get_rect().width >= self.stop
        elif self.direction == 'down':
            return self.y + self.image.get_rect().height >= self.stop
        elif self.direction == 'left':
            return self.x <= self.stop
        elif self.direction == 'up':
            return self.y <= self.stop
        return False
    
    def _can_move_forward(self, current_green, current_yellow, vehicles_dict):
        """Check if vehicle can move forward - FIXED RED LIGHT LOGIC"""
        is_green = (current_green == self.direction_number and 
                   current_yellow == 0)
        
        at_or_before_stop = False
        if self.direction == 'right':
            at_or_before_stop = (self.x + self.image.get_rect().width <= 
                                self.stop)
        elif self.direction == 'down':
            at_or_before_stop = (self.y + self.image.get_rect().height <= 
                                self.stop)
        elif self.direction == 'left':
            at_or_before_stop = self.x >= self.stop
        elif self.direction == 'up':
            at_or_before_stop = self.y >= self.stop
        
        no_vehicle_ahead = True
        if self.index > 0:
            prev_vehicle = vehicles_dict[self.direction][self.lane][self.index - 1]
            
            if self.direction == 'right':
                no_vehicle_ahead = (self.x + self.image.get_rect().width < 
                                   prev_vehicle.x - MOVING_GAP)
            elif self.direction == 'down':
                no_vehicle_ahead = (self.y + self.image.get_rect().height < 
                                   prev_vehicle.y - MOVING_GAP)
            elif self.direction == 'left':
                no_vehicle_ahead = (self.x > prev_vehicle.x + 
                                   prev_vehicle.image.get_rect().width + 
                                   MOVING_GAP)
            elif self.direction == 'up':
                no_vehicle_ahead = (self.y > prev_vehicle.y + 
                                   prev_vehicle.image.get_rect().height + 
                                   MOVING_GAP)
            
            if prev_vehicle.turned == 1:
                no_vehicle_ahead = True
        
        can_move = (at_or_before_stop or is_green or 
                   self.crossed == 1) and no_vehicle_ahead
        
        if self.crossed == 0:
            is_stopped_at_light = self._is_at_stop_position() and not can_move
            is_red_light = not is_green
            
            if is_stopped_at_light and is_red_light:
                self._start_redlight_wait()
                self._start_waiting()
            elif self.is_waiting_at_redlight and (is_green or can_move):
                self._stop_redlight_wait()
            
            if not can_move:
                self._start_waiting()
            elif can_move and self.is_waiting:
                self._stop_waiting()
        
        return can_move
    
    def _move_right(self, current_green, current_yellow, vehicles_dict,
                   vehicles_turned, vehicles_not_turned):
        """Handle movement for vehicles going right"""
        self._check_crossing(vehicles_dict, vehicles_not_turned)
        
        if self.will_turn == 1:
            if self.lane == 1:
                if (self.crossed == 0 or 
                    self.x + self.image.get_rect().width < 
                    STOP_LINES[self.direction] + 40):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.x += self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, self.rotate_angle)
                        self.x += 2.4
                        self.y -= 2.8
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            self.y > (vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].y + 
                                    vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].image.get_rect().height + 
                                    MOVING_GAP)):
                            self.y -= self.speed
            elif self.lane == 2:
                if (self.crossed == 0 or 
                    self.x + self.image.get_rect().width < 
                    MID_COORDINATES[self.direction]['x']):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.x += self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle)
                        self.x += 2
                        self.y += 1.8
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            (self.y + self.image.get_rect().height) < 
                            (vehicles_turned[self.direction][self.lane]
                             [self.crossed_index - 1].y - MOVING_GAP)):
                            self.y += self.speed
        else:
            if self.crossed == 0:
                if self._can_move_forward(current_green, current_yellow, 
                                        vehicles_dict):
                    self.x += self.speed
            else:
                if (self.crossed_index == 0 or 
                    self.x + self.image.get_rect().width < 
                    (vehicles_not_turned[self.direction][self.lane]
                     [self.crossed_index - 1].x - MOVING_GAP)):
                    self.x += self.speed
    
    def _move_down(self, current_green, current_yellow, vehicles_dict,
                  vehicles_turned, vehicles_not_turned):
        """Handle movement for vehicles going down"""
        self._check_crossing(vehicles_dict, vehicles_not_turned)
        
        if self.will_turn == 1:
            if self.lane == 1:
                if (self.crossed == 0 or 
                    self.y + self.image.get_rect().height < 
                    STOP_LINES[self.direction] + 50):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.y += self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, self.rotate_angle)
                        self.x += 1.2
                        self.y += 1.8
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            (self.x + self.image.get_rect().width) < 
                            (vehicles_turned[self.direction][self.lane]
                             [self.crossed_index - 1].x - MOVING_GAP)):
                            self.x += self.speed
            elif self.lane == 2:
                if (self.crossed == 0 or 
                    self.y + self.image.get_rect().height < 
                    MID_COORDINATES[self.direction]['y']):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.y += self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle)
                        self.x -= 2.5
                        self.y += 2
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            self.x > (vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].x + 
                                    vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].image.get_rect().width + 
                                    MOVING_GAP)):
                            self.x -= self.speed
        else:
            if self.crossed == 0:
                if self._can_move_forward(current_green, current_yellow, 
                                        vehicles_dict):
                    self.y += self.speed
            else:
                if (self.crossed_index == 0 or 
                    self.y + self.image.get_rect().height < 
                    (vehicles_not_turned[self.direction][self.lane]
                     [self.crossed_index - 1].y - MOVING_GAP)):
                    self.y += self.speed
    
    def _move_left(self, current_green, current_yellow, vehicles_dict,
                  vehicles_turned, vehicles_not_turned):
        """Handle movement for vehicles going left"""
        self._check_crossing(vehicles_dict, vehicles_not_turned)
        
        if self.will_turn == 1:
            if self.lane == 1:
                if (self.crossed == 0 or 
                    self.x > STOP_LINES[self.direction] - 70):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.x -= self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, self.rotate_angle)
                        self.x -= 1
                        self.y += 1.2
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            (self.y + self.image.get_rect().height) < 
                            (vehicles_turned[self.direction][self.lane]
                             [self.crossed_index - 1].y - MOVING_GAP)):
                            self.y += self.speed
            elif self.lane == 2:
                if (self.crossed == 0 or 
                    self.x > MID_COORDINATES[self.direction]['x']):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.x -= self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            self.y > (vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].y + 
                                    vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].image.get_rect().height + 
                                    MOVING_GAP)):
                            self.y -= self.speed
        else:
            if self.crossed == 0:
                if self._can_move_forward(current_green, current_yellow, 
                                        vehicles_dict):
                    self.x -= self.speed
            else:
                if (self.crossed_index == 0 or 
                    self.x > (vehicles_not_turned[self.direction][self.lane]
                            [self.crossed_index - 1].x + 
                            vehicles_not_turned[self.direction][self.lane]
                            [self.crossed_index - 1].image.get_rect().width + 
                            MOVING_GAP)):
                    self.x -= self.speed
    
    def _move_up(self, current_green, current_yellow, vehicles_dict,
                vehicles_turned, vehicles_not_turned):
        """Handle movement for vehicles going up"""
        self._check_crossing(vehicles_dict, vehicles_not_turned)
        
        if self.will_turn == 1:
            if self.lane == 1:
                if (self.crossed == 0 or 
                    self.y > STOP_LINES[self.direction] - 60):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.y -= self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, self.rotate_angle)
                        self.x -= 2
                        self.y -= 1.2
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            self.x > (vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].x + 
                                    vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].image.get_rect().width + 
                                    MOVING_GAP)):
                            self.x -= self.speed
            elif self.lane == 2:
                if (self.crossed == 0 or 
                    self.y > MID_COORDINATES[self.direction]['y']):
                    if self._can_move_forward(current_green, current_yellow, 
                                            vehicles_dict):
                        self.y -= self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += ROTATION_ANGLE
                        self.image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle)
                        self.x += 1
                        self.y -= 1
                        if self.rotate_angle == 90:
                            self.turned = 1
                            vehicles_turned[self.direction][self.lane].append(self)
                            self.crossed_index = len(
                                vehicles_turned[self.direction][self.lane]) - 1
                    else:
                        if (self.crossed_index == 0 or 
                            self.x < (vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].x - 
                                    vehicles_turned[self.direction][self.lane]
                                    [self.crossed_index - 1].image.get_rect().width - 
                                    MOVING_GAP)):
                            self.x += self.speed
        else:
            if self.crossed == 0:
                if self._can_move_forward(current_green, current_yellow, 
                                        vehicles_dict):
                    self.y -= self.speed
            else:
                if (self.crossed_index == 0 or 
                    self.y > (vehicles_not_turned[self.direction][self.lane]
                            [self.crossed_index - 1].y + 
                            vehicles_not_turned[self.direction][self.lane]
                            [self.crossed_index - 1].image.get_rect().height + 
                            MOVING_GAP)):
                    self.y -= self.speed