# 🚦 Traffic Light Optimization with Deep Q-Network (DQN)

> An intelligent traffic control system using Deep Reinforcement Learning to optimize traffic light timing at a 4-way intersection.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](#license)

---

## 📋 Overview

This project demonstrates **Deep Reinforcement Learning** applied to real-world traffic optimization. A DQN agent learns to control traffic signals by observing traffic conditions and making decisions to minimize vehicle wait times and maximize throughput.

### Key Features

✅ **Deep Q-Network (DQN) Agent** - Neural network-based traffic controller  
✅ **Real-time Traffic Simulation** - 4-way intersection with pygame visualization  
✅ **Advanced Statistics Tracking** - Comprehensive metrics on vehicle flow, wait times, and efficiency  
✅ **Google Colab Training** - Train on GPU without local hardware requirements  
✅ **Pre-trained Models** - Ready-to-use trained models included  
✅ **Easy to Extend** - Modular architecture for custom modifications  

---

## 🎯 How It Works

### Traditional Traffic Control
```
Fixed Timer → Same timing regardless of traffic conditions ❌
```

### DQN-Based Traffic Control
```
Observation (traffic state) → DQN Agent → Action (switch signal) → Reward → Learning ✅
```

The agent learns optimal policies by:
1. **Observing** real-time traffic state (vehicles waiting, signal timers, traffic levels)
2. **Deciding** which signal to activate based on learned policy
3. **Receiving** rewards for good decisions (vehicles crossing) and penalties for bad ones
4. **Learning** to improve its decision-making over thousands of episodes

---

## 📁 Project Structure

```
traffic/
│
├── Core Simulation Engine
│   ├── models.py              # Traffic signal & vehicle models
│   ├── managers.py            # Signal, vehicle, and simulation managers
│   ├── statistics.py          # Comprehensive performance tracking
│   ├── config.py              # Simulation constants & visual settings
│   └── __init__.py            # Package initialization
│
├── DQN Agent & Training
│   ├── dqn_agent.py           # DQN network, replay memory, training logic
│   ├── simulation_config.py   # Training hyperparameters & reward config
│   └── Train_DQN_Colab.ipynb  # Google Colab notebook for training
│
├── Inference & Deployment
│   ├── run_trained_agent.py   # Run pre-trained model
│   └── main.py                # Simulation demo (auto/manual modes)
│
├── Pre-trained Models
│   └── models/
│       ├── dqn_traffic_agent_fixed.pth
│       ├── dqn_traffic_agent_fixed_best.pth
│       └── dqn_traffic_colab.pth
│
└── Assets
    └── images/
        ├── signals/           # Traffic signal images
        ├── right/             # Vehicle sprites (right direction)
        ├── down/              # Vehicle sprites (down direction)
        ├── left/              # Vehicle sprites (left direction)
        └── up/                # Vehicle sprites (up direction)
```

---

## 🚀 Quick Start

### Option 1: Train on Google Colab (Recommended - Free GPU) 

**No local setup required!**

1. Open [Train_DQN_Colab.ipynb](Train_DQN_Colab.ipynb) in Google Colab
2. Run all cells in order
3. Download the trained model
4. (Optional) Use locally with `run_trained_agent.py`

**Training Time:** ~30-60 minutes for 100 episodes on Colab GPU

### Option 2: Run Pre-trained Model

**Requirements:**
- Python 3.8+
- PyTorch
- Pygame

**Setup:**

```bash
# Clone repository
git clone https://github.com/yourusername/traffic-light-dqn.git
cd traffic-light-dqn

# Install dependencies
pip install torch pygame numpy

# Run trained agent
python run_trained_agent.py
```

**Watch the trained agent control traffic in real-time!**

### Option 3: Train Locally

**For advanced users with GPU:**

```bash
# 1. Update simulation_config.py
# Set: DQN_TRAINING_MODE = True

# 2. Run training
python main.py

# Training typically takes 3-8 hours depending on hardware
```

---

## 📊 Performance Metrics

The system tracks detailed statistics:

| Metric | Description |
|--------|-------------|
| **Avg Wait Time** | Average seconds vehicles wait |
| **Vehicle Throughput** | Vehicles crossing per minute |
| **Efficiency** | % of vehicles that crossed vs. generated |
| **Red Light Waits** | Time spent stopped at red lights |
| **Traffic Balance** | Load distribution across directions |

Example output from a trained agent:
```
Vehicle Generation: 47 vehicles/hour
Average Wait Time: 12.3 seconds
Efficiency: 94.6%
Red Light Wait Time: 8.2 seconds
```

---

## 🧠 DQN Agent Architecture

### Neural Network
```
Input Layer (17 features)
    ↓
Dense Layer (128 neurons) + ReLU
    ↓
Dense Layer (128 neurons) + ReLU
    ↓
Dense Layer (128 neurons) + ReLU
    ↓
Output Layer (5 actions)
```

### State Features (17-dimensional vector)
- Signal timers for all 4 signals (4 features)
- Waiting vehicles at each direction (4 features)
- Traffic levels at each direction (4 features)
- Current green signal (4 features, one-hot encoded)
- Yellow phase active (1 feature)

### Actions (5 possible)
- Action 0-3: Activate green light for signal 0-3
- Action 4: Hold current signal (no switch)

### Training Hyperparameters
```python
Learning Rate: 0.0001
Gamma (discount factor): 0.99
Epsilon Start/End: 1.0 → 0.01
Epsilon Decay: 0.9997
Batch Size: 32
Replay Memory: 10,000 experiences
Target Update: Every 100 steps
```

### Reward Structure
```python
Vehicle Crosses:        +10.0
Queue Reduction:        +2.0
Queue Increase:         -1.0
Traffic Balance Bonus:  +2.0
```

---

## 📈 Training Results

Typical training progression over 50 episodes:

```
Episode  1: Reward = 15.2, Loss = 2.4532, Epsilon = 0.9997
Episode 10: Reward = 42.7, Loss = 0.8234, Epsilon = 0.9703
Episode 25: Reward = 89.3, Loss = 0.2156, Epsilon = 0.8821
Episode 50: Reward = 156.8, Loss = 0.0432, Epsilon = 0.6234
```

**Key Observations:**
- Rewards increase as agent learns better policies
- Loss decreases as network improves
- Agent successfully learns to manage traffic flow

---

## 🔧 Configuration & Customization

### Training Parameters

Edit `simulation_config.py`:

```python
# Number of training episodes
DQN_TRAINING_EPISODES = 50  # Increase for better results (100-500 recommended)

# Decision making interval
DQN_DECISION_INTERVAL = 8  # Seconds between decisions

# Learning parameters
DQN_PARAMS = {
    'learning_rate': 0.0001,
    'gamma': 0.99,
    'epsilon_decay': 0.9997,
    'batch_size': 32,
    'memory_size': 10000,
}

# Reward structure
DQN_REWARDS = {
    'vehicle_crossed': 10.0,
    'waiting_reduction': 2.0,
    'waiting_increase_penalty': -1.0,
    'traffic_balance_bonus': 2.0,
}
```

### Simulation Parameters

Edit `config.py`:

```python
# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800

# Vehicle generation rates
VEHICLE_SPAWN_RATE = 0.15  # Probability per frame

# Signal timing
DEFAULT_GREEN = {0: 10, 1: 10, 2: 10, 3: 10}
DEFAULT_RED = 150
DEFAULT_YELLOW = 5
```

---

## 📚 File Descriptions

### Core Simulation

**models.py** - Vehicle and Signal models
- `TrafficSignal`: Manages signal state (red, yellow, green timers)
- `Vehicle`: Individual vehicle with movement, collision detection, wait time tracking

**managers.py** - Simulation management
- `SignalManager`: Controls signal switching logic
- `VehicleManager`: Manages all vehicles and generates new ones
- `SimulationManager`: Coordinates entire simulation

**statistics.py** - Performance tracking
- `StatisticsCollector`: Tracks all metrics (wait times, throughput, efficiency)
- Calculates average waiting time from completed vehicles
- Generates comprehensive reports

**config.py** - Constants
- Screen dimensions, colors, vehicle speeds
- Signal timing defaults
- Spawn coordinates

### DQN Components

**dqn_agent.py** - Deep Q-Learning implementation
- `DQNNetwork`: Neural network architecture
- `ReplayMemory`: Experience replay buffer
- `DQNTrafficAgent`: Main agent with training logic

**simulation_config.py** - Training configuration
- Hyperparameters for DQN training
- Reward structure definition
- Training mode flags

### Entry Points

**main.py** - Simulation runner
- Supports both NORMAL (fixed timing) and DQN modes
- Manual/automatic control modes
- Real-time visualization

**run_trained_agent.py** - Inference script
- Loads pre-trained model
- Runs simulation with trained agent
- No training, just inference

**Train_DQN_Colab.ipynb** - Google Colab notebook
- Complete training pipeline for Colab
- Includes setup, training, visualization
- Downloads trained model

---

## 🔍 Understanding the Statistics

The system calculates average waiting time as follows:

```python
# For each vehicle that crosses the intersection:
wait_time = spawn_time_to_crossing_time

# Average across all completed vehicles:
avg_wait_time = sum(wait_times) / num_vehicles_crossed
```

**What affects wait time:**
- ✅ Good decisions by DQN → Lower wait times
- ✅ Balanced traffic distribution → Lower wait times
- ❌ Too long green signals → Higher wait times
- ❌ Unbalanced traffic → Higher wait times

**Key metrics tracked:**
- `completed_wait_times` - Total wait per vehicle
- `redlight_wait_times` - Time stopped at red lights
- `traffic_level` - Congestion at each direction
- `throughput` - Vehicles crossing per unit time

---

## 📝 Examples

### Run Pre-trained Model

```python
python run_trained_agent.py
# Controls appear on screen
# S = Show/hide stats
# P = Print stats to console
# E = Export stats to file
```

### Train New Model

```python
# Edit simulation_config.py:
# DQN_TRAINING_MODE = True
# DQN_TRAINING_EPISODES = 100

python main.py
# Watch training progress with visualization
```

### Use in Google Colab

```
1. Open Train_DQN_Colab.ipynb
2. Mount Google Drive or clone repo
3. Run all cells
4. Download trained model
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **No module named 'pygame'** | `pip install pygame` |
| **GPU not detected** | Install PyTorch with CUDA: `pip install torch torchvision torchaudio` |
| **Model file not found** | Ensure `dqn_traffic_agent_fixed.pth` exists in `models/` directory |
| **Low FPS on Windows** | Reduce `FPS` in `config.py` or use headless training |
| **Out of memory** | Reduce `batch_size` and `memory_size` in `simulation_config.py` |

---

## 🎓 Learning Resources

- **DQN Paper:** [Human-level control through deep reinforcement learning (Nature, 2015)](https://www.nature.com/articles/nature14236)
- **PyTorch Docs:** https://pytorch.org/docs/stable/index.html
- **RL Basics:** https://en.wikipedia.org/wiki/Q-learning

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👥 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Multi-agent DQN for multiple intersections
- [ ] Policy gradient methods (PPO, A3C)
- [ ] Real traffic data integration
- [ ] More sophisticated reward functions
- [ ] Visualization improvements
- [ ] Genetic algorithms for hyperparameter tuning

---

## 📞 Support

For issues, questions, or suggestions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review existing GitHub issues
3. Create a new issue with detailed description

---

## 🎯 Future Work

- [ ] Multi-intersection network control
- [ ] Real-world traffic data integration
- [ ] Mobile app for visualization
- [ ] Benchmark against traditional methods
- [ ] Distributed training across multiple GPUs
- [ ] Integration with SUMO traffic simulator

---

**Last Updated:** January 2026  
**Status:** Active Development ✅

```bash
python train_dqn_fast.py
```

This will train for 50 episodes and save the best model automatically.

### 2. **Run the Trained Agent**

```bash
python run_trained_agent.py
```

Watch the trained agent control traffic lights in the simulation.

### 3. **Demo Manual Control**

```bash
python main.py
```

Interactive simulation where you can toggle between manual and automatic control.

---

## 🧠 Deep Q-Network (DQN) Explanation

### What is DQN?

**Deep Q-Network** is a reinforcement learning algorithm that combines:
- **Q-Learning**: Learning the value of state-action pairs
- **Deep Neural Networks**: Approximating complex Q-functions
- **Experience Replay**: Breaking correlation in training data
- **Target Networks**: Stabilizing learning

### How It Works

1. **Agent observes state** (traffic conditions, signal timers)
2. **Selects action** (switch signal, hold current, extend duration)
3. **Receives reward** (based on vehicles crossed, queue reduction)
4. **Stores experience** in replay memory
5. **Learns** by sampling random experiences and updating network
6. **Repeats** until converged to optimal policy

### Key Innovations Used

- **Delta-Based Rewards**: Rewards improvement, not absolute state
- **Simplified Action Space**: 5 clear actions to prevent thrashing
- **State Normalization**: Properly scaled inputs for neural network
- **Epsilon-Greedy Exploration**: Balances exploration vs exploitation
- **Target Network**: Separate network for stable TD targets

---

## 📚 Detailed File Documentation

### **Core Simulation Files**

#### `models.py` - Traffic Entities
Defines the fundamental objects in the simulation.

**Classes:**
- `TrafficSignal`: Represents a single traffic light
  - Manages red, yellow, green timers
  - Tracks signal state and transitions
  - Methods: `update_timers()`, `reset_green()`, `reset_timers()`

- `Vehicle`: Represents a single vehicle
  - Handles movement, lane changes, turning
  - Collision detection with other vehicles
  - Methods: `render()`, `move()`, `check_collision()`

**Techniques:**
- Sprite-based rendering (pygame)
- Physics-based movement (velocity, acceleration)
- Lane management and turning logic

---

#### `managers.py` - Simulation Control
Coordinates all simulation components.

**Classes:**

**1. SignalManager**
Manages all 4 traffic signals at the intersection.

**Key Methods:**
- `activate_green_signal(signal_index)` - DQN agent uses this to switch signals
- `extend_green_duration(seconds)` - DQN agent uses this to extend green time
- `get_current_signal_state()` - Returns state for DQN observation
- `_start_yellow_phase()` - Handles yellow transition
- `_complete_signal_transition()` - Completes signal switch

**Control Modes:**
- `auto`: Traditional cyclic timing
- `manual`: DQN agent control (used during training)

**2. VehicleManager**
Manages vehicle generation and movement.

**Key Methods:**
- `generate_vehicle()` - Creates random vehicles
- `update_vehicles()` - Updates all vehicle positions
- `get_traffic_state_for_dqn()` - Returns traffic metrics for DQN
- `calculate_traffic_level()` - Computes congestion level (1-10)

**Techniques:**
- Multi-threaded vehicle generation
- Sprite group management (pygame)
- Traffic flow calculation

**3. SimulationManager** (only in GUI mode)
Coordinates the entire simulation with rendering.

**Key Responsibilities:**
- Initialize pygame display
- Run main game loop
- Render traffic signals and vehicles
- Display statistics overlay
- Handle user inputs

---

#### `statistics.py` - Performance Tracking
Collects and analyzes simulation metrics.

**Class: StatisticsCollector**

**Key Metrics:**
- Vehicles generated/crossed per direction
- Signal cycle counts and durations
- Red light wait times
- Traffic efficiency percentages

**Methods:**
- `record_vehicle_generation()` - Track new vehicles
- `record_vehicle_crossed()` - Track successful crossings
- `record_signal_cycle()` - Track signal timings
- `generate_report()` - Create comprehensive statistics
- `export_to_file()` - Save stats to text file

---

### **DQN Implementation Files**

#### `dqn_agent.py` - Deep Q-Network Agent
The brain of the intelligent traffic controller.

**Classes:**

**1. DQNNetwork (PyTorch nn.Module)**
Neural network architecture for Q-function approximation.

**Architecture:**
```
Input Layer (17 features)
    ↓
Hidden Layer 1 (128 neurons + ReLU)
    ↓
Hidden Layer 2 (128 neurons + ReLU)
    ↓
Hidden Layer 3 (128 neurons + ReLU)
    ↓
Output Layer (5 Q-values, one per action)
```

**Techniques:**
- Fully connected (dense) layers
- ReLU activation for non-linearity
- Xavier/He initialization (automatic in PyTorch)

**2. ReplayMemory**
Experience replay buffer for breaking temporal correlation.

**Structure:**
- Deque with max capacity (10,000 experiences)
- Stores tuples: (state, action, reward, next_state, done)
- Random sampling for training batches

**Why it matters:**
- Breaks correlation between consecutive experiences
- Enables off-policy learning
- Improves sample efficiency

**3. DQNTrafficAgent**
Main agent that learns to control traffic.

**State Representation (17 features):**
1. Signal timers (4) - normalized green/red times
2. Waiting vehicles (4) - vehicles per direction
3. Traffic levels (4) - congestion score 1-10
4. Current green signal (4) - one-hot encoded
5. Yellow phase active (1) - boolean

**Action Space (5 actions):**
- 0-3: Switch to specific signal
- 4: Hold current signal (extend by 5s)

**Reward Function (Delta-Based):**
```python
reward = 0

# PRIMARY: Vehicles crossed
reward += vehicles_crossed * 10.0

# SECONDARY: Queue reduction
if (waiting_before - waiting_after) > 0:
    reward += (waiting_before - waiting_after) * 2.0
else:
    reward += (waiting_before - waiting_after) * -1.0

# BONUS: Balanced traffic
if traffic_variance < 2.0:
    reward += 2.0
```

**Key Methods:**

- `get_state()` - Convert simulation state to neural network input
- `select_action()` - ε-greedy action selection
- `train()` - Update network using experience replay
- `calculate_reward()` - Compute reward from state transition

**Training Algorithm:**
1. Sample batch from replay memory
2. Compute current Q-values: Q(s, a)
3. Compute target Q-values: r + γ * max Q(s', a')
4. Calculate loss: MSE(Q_current, Q_target)
5. Backpropagate and update policy network
6. Periodically update target network

**Hyperparameters:**
- Learning rate: 0.0001
- Batch size: 32
- Gamma (discount): 0.99
- Epsilon decay: 0.9997
- Target network update: every 100 steps

---

#### `simulation_config.py` - Training Configuration
Central configuration for DQN training.

**Key Parameters:**

**Training:**
- `DQN_TRAINING_EPISODES`: Number of episodes (50 recommended)
- `DQN_DECISION_INTERVAL`: Time between decisions (8s for GUI, 5s for headless)
- `DQN_MODEL_PATH`: Where to save trained model

**DQN Hyperparameters:**
- `learning_rate`: 0.0001 (Adam optimizer)
- `gamma`: 0.99 (future reward discount)
- `epsilon_start`: 1.0 (initial exploration)
- `epsilon_end`: 0.01 (minimum exploration)
- `epsilon_decay`: 0.9997 (exploration decay rate)
- `batch_size`: 32 (training batch)
- `memory_size`: 10,000 (replay buffer)
- `target_update`: 100 (target network sync frequency)

**Reward Structure (Delta-Based):**
- `vehicle_crossed`: +10.0
- `waiting_reduction`: +2.0
- `waiting_increase_penalty`: -1.0
- `traffic_balance_bonus`: +2.0

---

### **Training Scripts**

#### `train_dqn_fast.py` - Fast Headless Training ⚡
**RECOMMENDED** for actual training.

**Features:**
- Uses real simulation (SignalManager, VehicleManager)
- Disables pygame rendering (`SDL_VIDEODRIVER=dummy`)
- 38% faster than GUI training
- Same accuracy as GUI version

**Speed:**
- Decision interval: 5s (optimized)
- Action wait: 3s
- Total: ~8s per step
- 50 episodes: ~11 hours

**Usage:**
```bash
python train_dqn_fast.py
```

**How It Works:**
1. Creates headless simulation manager
2. Starts background threads (signals, vehicles)
3. DQN agent interacts with simulation
4. No pygame rendering = faster
5. Saves best model automatically

---

#### `train_dqn.py` - GUI Training
Training with visual feedback (slower).

**Features:**
- Full pygame visualization
- Watch agent learn in real-time
- Statistics overlay
- Interactive controls

**Speed:**
- ~13s per step (slower due to rendering)
- 50 episodes: ~18 hours

**Usage:**
```bash
python train_dqn.py
```

**Controls:**
- S: Toggle stats
- P: Print to console
- M: Toggle control mode
- Close window to exit

---

#### `run_trained_agent.py` - Deploy Trained Model
Run a trained DQN agent to see it in action.

**Features:**
- Loads saved model from `models/`
- Agent controls traffic without exploration (ε=0)
- Visual demonstration of learned policy

**Usage:**
```bash
python run_trained_agent.py
```

---

### **Configuration Files**

#### `config.py` - Visual & Simulation Constants
Constants for the pygame simulation.

**Categories:**
- Screen dimensions and coordinates
- Signal positions and timer locations
- Vehicle images and dimensions
- Default timing values
- Color definitions

**Key Constants:**
- `SCREEN_WIDTH/HEIGHT`: 1400x800
- `NO_OF_SIGNALS`: 4
- `DEFAULT_GREEN`: Base signal durations
- `SIGNAL_COORDS`: Signal light positions
- `DEFAULT_STOP`: Stop line positions

---

## 🧪 DQN Techniques Explained

### 1. **Experience Replay**
**Problem**: Sequential experiences are correlated  
**Solution**: Store experiences in buffer, sample randomly  
**Benefit**: Breaks correlation, improves stability

**Implementation:**
```python
class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.memory.append(Experience(...))
    
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
```

---

### 2. **Target Network**
**Problem**: Q-value targets change as we learn  
**Solution**: Use separate frozen network for targets  
**Benefit**: Stabilizes training

**Implementation:**
```python
# Policy network (updated every step)
self.policy_net = DQNNetwork(...)

# Target network (updated every 100 steps)
self.target_net = DQNNetwork(...)
self.target_net.load_state_dict(self.policy_net.state_dict())

# Use target network for computing TD targets
with torch.no_grad():
    next_q = self.target_net(next_state).max(1)[0]
    target = reward + gamma * next_q
```

---

### 3. **Epsilon-Greedy Exploration**
**Problem**: Need to balance exploration vs exploitation  
**Solution**: Act randomly with probability ε, greedily otherwise  
**Benefit**: Discovers new strategies while using learned knowledge

**Implementation:**
```python
if random.random() < self.epsilon:
    return random.randrange(self.action_size)  # Explore
else:
    return policy_net(state).max(1)[1].item()  # Exploit
```

Epsilon starts at 1.0 (100% random) and decays to 0.01 (1% random).

---

### 4. **Delta-Based Rewards**
**Problem**: Penalizing absolute state creates reward drain  
**Solution**: Reward improvement (delta), not state  
**Benefit**: Agent can always earn positive rewards

**Before (BROKEN):**
```python
reward = -0.05 * total_waiting  # Always negative!
```

**After (FIXED):**
```python
waiting_reduction = waiting_before - waiting_after
if waiting_reduction > 0:
    reward += waiting_reduction * 2.0  # Positive for improvement
```

---

### 5. **Temporal Difference (TD) Learning**
**Problem**: Can't wait until end of episode for reward  
**Solution**: Bootstrap from estimated future values  
**Benefit**: Learn continuously from every transition

**TD Target:**
```python
target = r + γ * max Q(s', a')
       = immediate reward + discounted future value
```

**Loss:**
```python
loss = MSE(Q(s,a), target)
```

---

### 6. **Soft Updates (Deprecated in this implementation)**
Alternative to hard target network updates.

**Hard Update (used here):**
```python
if step % 100 == 0:
    target_net.load_state_dict(policy_net.state_dict())
```

**Soft Update (alternative):**
```python
for target_param, policy_param in zip(target_net.parameters(), policy_net.parameters()):
    target_param.data.copy_(τ * policy_param.data + (1-τ) * target_param.data)
```

---

## 📊 Training Progress

### Expected Reward Progression

| Phase | Episodes | Avg Reward | Description |
|-------|----------|------------|-------------|
| Exploration | 1-10 | 0 to +10 | Random exploration, discovering actions |
| Learning | 10-30 | +10 to +30 | Learning basic patterns |
| Optimization | 30-50 | +30 to +50 | Fine-tuning optimal policy |

### Monitoring Training

**Console Output:**
```
[Training] Ep 25/50 (50.0%) | ε: 0.882 | Reward: 25.34 | Loss: 15.2
```

**Log Files:**
```
training_logs/fast_training_YYYYMMDD_HHMMSS.txt
```

**Saved Models:**
```
models/dqn_traffic_agent_fixed_best.pth    # Best model
models/dqn_traffic_agent_fixed.pth          # Final model
```

---

## 🎓 Learning Resources

### DQN Papers
- **Playing Atari with Deep Reinforcement Learning** (2013) - Original DQN paper
- **Human-level control through deep reinforcement learning** (2015) - Nature paper

### Concepts
- **Q-Learning**: Value-based RL algorithm
- **Function Approximation**: Using neural networks for Q-values
- **Off-Policy Learning**: Learning from any experiences
- **Bellman Equation**: Recursive relationship for values

### Tools Used
- **PyTorch**: Deep learning framework
- **Pygame**: 2D game engine for visualization
- **NumPy**: Numerical computations

---

## ⚙️ Advanced Customization

### Modify Reward Function
Edit `dqn_agent.py:calculate_reward()`:
```python
# Customize reward weights
reward = vehicles_crossed * 15.0  # Increase crossing reward
reward += waiting_reduction * 3.0  # Increase queue reduction reward
```

### Change Network Architecture
Edit `dqn_agent.py:DQNNetwork`:
```python
# Add more layers or change size
self.fc1 = nn.Linear(state_size, 256)  # Bigger network
self.fc2 = nn.Linear(256, 256)
self.fc3 = nn.Linear(256, 128)
self.fc4 = nn.Linear(128, action_size)
```

### Adjust Hyperparameters
Edit `simulation_config.py:DQN_PARAMS`:
```python
'learning_rate': 0.0005,  # Faster learning
'gamma': 0.95,            # Less future discounting
'epsilon_decay': 0.999,   # Faster exploration decay
```

---

## 🐛 Troubleshooting

### Issue: Rewards stuck at zero
**Cause**: No vehicles crossing  
**Solution**: Ensure traffic generation is running (check background threads)

### Issue: Training too slow
**Cause**: Using GUI version  
**Solution**: Use `train_dqn_fast.py` instead

### Issue: Loss increasing
**Cause**: Normal during early training  
**Solution**: Wait for network to converge (15-20 episodes)

### Issue: Model not improving
**Cause**: Reward function issues or hyperparameters  
**Solution**: Check reward function returns positive values, adjust learning rate

---

## 📄 License & Credits

**Author**: Ismail  
**Project**: Traffic Light Optimization with Deep Q-Networks  
**AI Assistant**: Claude (Anthropic) - Code debugging and optimization

---

## 🔗 Next Steps

1. **Train your model**: `python train_dqn_fast.py`
2. **Evaluate performance**: Compare trained agent vs random baseline
3. **Experiment**: Try different reward functions, network architectures
4. **Deploy**: Use trained model in real simulation scenarios
5. **Extend**: Add more complex intersection layouts, multi-agent learning

---

**Happy Training! 🚦🤖**
