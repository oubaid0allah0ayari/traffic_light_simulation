"""
DQN Agent for Traffic Light Control
Deep Q-Network agent that learns to optimize traffic flow
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque, namedtuple
import os


# Experience tuple for replay memory
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])


class DQNNetwork(nn.Module):
    """
    Deep Q-Network Neural Network
    
    Architecture:
        Input Layer: State vector
        Hidden Layers: 3 fully connected layers with ReLU
        Output Layer: Q-values for each action
    """
    
    def __init__(self, state_size, action_size, hidden_size=128):
        """
        Initialize the DQN network
        
        Args:
            state_size (int): Dimension of state vector
            action_size (int): Number of possible actions
            hidden_size (int): Size of hidden layers
        """
        super(DQNNetwork, self).__init__()
        
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size)
        self.fc4 = nn.Linear(hidden_size, action_size)
        
        self.relu = nn.ReLU()
        
    def forward(self, x):
        """
        Forward pass through the network
        
        Args:
            x (torch.Tensor): Input state
            
        Returns:
            torch.Tensor: Q-values for each action
        """
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class ReplayMemory:
    """
    Experience Replay Memory
    
    Stores experiences and samples random batches for training
    to break correlation between consecutive experiences
    """
    
    def __init__(self, capacity):
        """
        Initialize replay memory
        
        Args:
            capacity (int): Maximum number of experiences to store
        """
        self.memory = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """
        Add experience to memory
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        self.memory.append(Experience(state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """
        Sample random batch of experiences
        
        Args:
            batch_size (int): Number of experiences to sample
            
        Returns:
            list: Batch of Experience tuples
        """
        return random.sample(self.memory, batch_size)
    
    def __len__(self):
        """Return current size of memory"""
        return len(self.memory)


class DQNTrafficAgent:
    """
    DQN Agent for Traffic Light Control
    
    Uses Deep Q-Learning to learn optimal traffic light control policy
    """
    
    def __init__(self, config, rewards):
        """
        Initialize DQN agent
        
        Args:
            config (dict): Configuration parameters
            rewards (dict): Reward structure
        """
        # Configuration
        self.config = config
        self.rewards = rewards
        
        # State and action space
        self.state_size = self._calculate_state_size()
        self.action_size = 5  # 4 signals + hold current (simplified to prevent thrashing)
        
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[DQN] Using device: {self.device}")
        
        # Networks
        self.policy_net = DQNNetwork(
            self.state_size, 
            self.action_size,
            hidden_size=128
        ).to(self.device)
        
        self.target_net = DQNNetwork(
            self.state_size,
            self.action_size,
            hidden_size=128
        ).to(self.device)
        
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(
            self.policy_net.parameters(),
            lr=config['learning_rate']
        )
        
        # Loss function
        self.criterion = nn.MSELoss()
        
        # Replay memory
        self.memory = ReplayMemory(config['memory_size'])
        
        # Training parameters
        self.gamma = config['gamma']
        self.epsilon = config['epsilon_start']
        self.epsilon_end = config['epsilon_end']
        self.epsilon_decay = config['epsilon_decay']
        self.batch_size = config['batch_size']
        self.target_update = config['target_update']
        
        # Training stats
        self.steps_done = 0
        self.episodes_done = 0
        self.total_rewards = []
        self.losses = []
        
    def _calculate_state_size(self):
        """
        Calculate the size of state vector
        
        State includes:
        - Current signal state (4 values for timers)
        - Traffic waiting at each signal (4 values)
        - Traffic level at each direction (4 values)
        - Current green signal (4 one-hot encoded)
        - Yellow phase active (1 value)
        
        Returns:
            int: Total state size
        """
        return 4 + 4 + 4 + 4 + 1  # = 17
    
    def get_state(self, signal_state, traffic_state):
        """
        Convert simulation state to DQN state vector
        
        Args:
            signal_state (dict): Signal manager state
            traffic_state (dict): Traffic manager state
            
        Returns:
            np.array: State vector
        """
        state_vector = []
        
        # Signal timers (normalized to 0-1 with realistic bounds)
        for signal in signal_state['signals']:
            # Use green timer if active, else use red timer
            if signal['is_green']:
                # Cap at 60s max, normalize
                timer = min(signal['green'], 60) / 60.0
            else:
                # Cap at 180s max, normalize
                timer = min(signal['red'], 180) / 180.0
            state_vector.append(timer)
        
        # Waiting vehicles at each direction (capped and normalized)
        directions = ['right', 'down', 'left', 'up']
        for direction in directions:
            waiting = traffic_state[direction]['waiting']
            # Cap at 30 vehicles, normalize
            state_vector.append(min(waiting, 30) / 30.0)
        
        # Traffic level at each direction (already 1-10 scale)
        for direction in directions:
            level = traffic_state[direction]['traffic_level']
            state_vector.append(level / 10.0)  # Normalize to 0-1
        
        # Current green signal (one-hot)
        current_green_onehot = [0, 0, 0, 0]
        current_green_onehot[signal_state['current_green']] = 1
        state_vector.extend(current_green_onehot)
        
        # Yellow phase active
        state_vector.append(float(signal_state['current_yellow']))
        
        return np.array(state_vector, dtype=np.float32)
    
    def select_action(self, state, explore=True):
        """
        Select action using epsilon-greedy policy
        
        Args:
            state (np.array): Current state
            explore (bool): Whether to explore or exploit
            
        Returns:
            int: Selected action
        """
        # Epsilon-greedy exploration
        if explore and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        
        # Exploitation: choose best action
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            return q_values.max(1)[1].item()
    
    def store_experience(self, state, action, reward, next_state, done):
        """
        Store experience in replay memory
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode ended
        """
        self.memory.push(state, action, reward, next_state, done)
    
    def train(self):
        """
        Train the DQN network using experience replay
        
        Returns:
            float: Loss value, or None if not enough experiences
        """
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch
        experiences = self.memory.sample(self.batch_size)
        batch = Experience(*zip(*experiences))
        
        # Convert to tensors
        state_batch = torch.FloatTensor(np.array(batch.state)).to(self.device)
        action_batch = torch.LongTensor(batch.action).to(self.device)
        reward_batch = torch.FloatTensor(batch.reward).to(self.device)
        next_state_batch = torch.FloatTensor(np.array(batch.next_state)).to(self.device)
        done_batch = torch.FloatTensor(batch.done).to(self.device)
        
        # Compute current Q values
        current_q_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))
        
        # Compute target Q values
        with torch.no_grad():
            next_q_values = self.target_net(next_state_batch).max(1)[0]
            target_q_values = reward_batch + (1 - done_batch) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.criterion(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update epsilon
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        
        # Track training
        self.steps_done += 1
        self.losses.append(loss.item())
        
        # Update target network
        if self.steps_done % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
            print(f"[DQN] Target network updated (step {self.steps_done})")
        
        return loss.item()
    
    def calculate_reward(self, traffic_state_before, traffic_state_after, action):
        """
        Calculate reward based on traffic improvement (DELTA-BASED)
        
        Key changes:
        - Rewards IMPROVEMENT (reduction in waiting) not absolute state
        - No constant penalty drain for existing traffic
        - Focus on throughput and queue reduction
        
        Args:
            traffic_state_before (dict): Traffic state before action
            traffic_state_after (dict): Traffic state after action
            action (int): Action taken
            
        Returns:
            float: Calculated reward
        """
        reward = 0.0
        
        # PRIMARY REWARD: Vehicles that crossed (main objective)
        total_crossed_before = sum(
            traffic_state_before[d]['crossed'] 
            for d in ['right', 'down', 'left', 'up']
        )
        total_crossed_after = sum(
            traffic_state_after[d]['crossed'] 
            for d in ['right', 'down', 'left', 'up']
        )
        vehicles_crossed = total_crossed_after - total_crossed_before
        reward += vehicles_crossed * self.rewards.get('vehicle_crossed', 10.0)
        
        # SECONDARY REWARD: Reduction in waiting vehicles (delta-based)
        total_waiting_before = sum(
            traffic_state_before[d]['waiting'] 
            for d in ['right', 'down', 'left', 'up']
        )
        total_waiting_after = sum(
            traffic_state_after[d]['waiting'] 
            for d in ['right', 'down', 'left', 'up']
        )
        waiting_reduction = total_waiting_before - total_waiting_after
        
        # Reward for reducing queue, penalty for increasing it
        if waiting_reduction > 0:
            reward += waiting_reduction * self.rewards.get('waiting_reduction', 2.0)
        elif waiting_reduction < 0:
            reward += waiting_reduction * self.rewards.get('waiting_increase_penalty', -1.0)
        
        # BONUS: Balanced traffic across all directions
        traffic_levels = [
            traffic_state_after[d]['traffic_level']
            for d in ['right', 'down', 'left', 'up']
        ]
        traffic_variance = np.var(traffic_levels)
        if traffic_variance < 2.0:  # Low variance = balanced
            reward += self.rewards.get('traffic_balance_bonus', 2.0)
        
        return reward
    
    def save_model(self, filepath):
        """
        Save the trained model
        
        Args:
            filepath (str): Path to save model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done,
            'episodes_done': self.episodes_done,
            'total_rewards': self.total_rewards,
            'config': self.config
        }, filepath)
        
        print(f"[DQN] Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load a trained model
        
        Args:
            filepath (str): Path to load model from
        """
        if not os.path.exists(filepath):
            print(f"[DQN] Model file not found: {filepath}")
            return False
        
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.steps_done = checkpoint['steps_done']
        self.episodes_done = checkpoint['episodes_done']
        self.total_rewards = checkpoint.get('total_rewards', [])
        
        print(f"[DQN] Model loaded from {filepath}")
        print(f"[DQN] Episodes: {self.episodes_done}, Steps: {self.steps_done}")
        print(f"[DQN] Epsilon: {self.epsilon:.4f}")
        
        return True
    
    def get_stats(self):
        """
        Get training statistics
        
        Returns:
            dict: Statistics dictionary
        """
        return {
            'episodes': self.episodes_done,
            'steps': self.steps_done,
            'epsilon': self.epsilon,
            'avg_reward': np.mean(self.total_rewards[-100:]) if self.total_rewards else 0,
            'avg_loss': np.mean(self.losses[-100:]) if self.losses else 0,
            'memory_size': len(self.memory)
        }
    
    def print_stats(self):
        """Print current training statistics"""
        stats = self.get_stats()
        print(f"\n{'='*60}")
        print(f"DQN Agent Statistics")
        print(f"{'='*60}")
        print(f"Episodes: {stats['episodes']}")
        print(f"Steps: {stats['steps']}")
        print(f"Epsilon: {stats['epsilon']:.4f}")
        print(f"Avg Reward (last 100): {stats['avg_reward']:.2f}")
        print(f"Avg Loss (last 100): {stats['avg_loss']:.4f}")
        print(f"Memory Size: {stats['memory_size']}")
        print(f"{'='*60}\n")


class DQNTrainer:
    """
    Trainer class for DQN agent with simulation
    Handles the training loop and interaction with simulation
    """
    
    def __init__(self, simulation, agent, config):
        """
        Initialize trainer
        
        Args:
            simulation: SimulationManager instance
            agent: DQNTrafficAgent instance
            config: Training configuration
        """
        self.simulation = simulation
        self.agent = agent
        self.config = config
        
        self.episode = 0
        self.step = 0
        
    def get_current_state(self):
        """
        Get current state from simulation
        
        Returns:
            np.array: State vector
        """
        signal_state = self.simulation.signal_manager.get_current_signal_state()
        traffic_state = self.simulation.vehicle_manager.get_traffic_state_for_dqn()
        return self.agent.get_state(signal_state, traffic_state)
    
    def execute_action(self, action):
        """
        Execute action in simulation (SIMPLIFIED ACTION SPACE)
        
        Args:
            action (int): Action to execute
            
        Actions:
            0-3: Activate signal 0-3 (switch to specific signal)
            4: Hold current signal (keep current green active)
        """
        vehicles_dict = self.simulation.vehicle_manager.vehicles
        
        if action < 4:
            # Activate specific signal (switch if different from current)
            self.simulation.signal_manager.activate_green_signal(
                action,
                vehicles_dict=vehicles_dict
            )
        elif action == 4:
            # Hold current signal - extend by 5 seconds to maintain green
            self.simulation.signal_manager.extend_green_duration(5)
    
    def train_step(self):
        """
        Execute one training step
        
        Returns:
            float: Reward received
        """
        # Get current state and traffic
        state = self.get_current_state()
        traffic_before = self.simulation.vehicle_manager.get_traffic_state_for_dqn()
        
        # Select and execute action
        action = self.agent.select_action(state, explore=True)
        self.execute_action(action)
        
        # Get next state and traffic after action
        next_state = self.get_current_state()
        traffic_after = self.simulation.vehicle_manager.get_traffic_state_for_dqn()
        
        # Calculate reward
        reward = self.agent.calculate_reward(traffic_before, traffic_after, action)
        
        # Store experience
        done = False  # Continuous task, never done
        self.agent.store_experience(state, action, reward, next_state, done)
        
        # Train
        loss = self.agent.train()
        
        self.step += 1
        
        return reward
    
    def print_progress(self, episode, total_episodes):
        """
        Print training progress
        
        Args:
            episode (int): Current episode
            total_episodes (int): Total episodes
        """
        stats = self.agent.get_stats()
        progress = (episode / total_episodes) * 100
        
        print(f"\r[DQN Training] Episode {episode}/{total_episodes} ({progress:.1f}%) | "
              f"Epsilon: {stats['epsilon']:.3f} | "
              f"Avg Reward: {stats['avg_reward']:.2f} | "
              f"Avg Loss: {stats['avg_loss']:.4f}", end='')
        
        if episode % 100 == 0:
            print()  # New line every 100 episodes