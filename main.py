"""
Main entry point for the traffic simulation
Supports both NORMAL and DQN modes based on simulation_config.py
"""
import sys
from managers import SimulationManager
import simulation_config as sim_config


def main():
    """Main function to run the traffic simulation"""
    try:
        # Validate configuration
        if not sim_config.validate_config():
            print("\n[ERREUR] Configuration invalide. Veuillez vérifier simulation_config.py")
            sys.exit(1)
        
        # Print configuration summary
        sim_config.print_config_summary()
        
        # Display startup message
        print("=" * 60)
        print("SIMULATION DE CARREFOUR INTELLIGENT")
        print("=" * 60)
        print(f"Mode: {sim_config.SIMULATION_MODE}")
        print("=" * 60)
        print("Démarrage de la simulation...")
        
        # Display controls
        print("\nContrôles:")
        print("  S - Afficher/Masquer statistiques")
        print("  P - Imprimer statistiques console")
        print("  E - Exporter statistiques")
        if sim_config.is_normal_mode():
            print("  M - Basculer Auto/Manual (pour tests)")
        print("  Fermer la fenêtre pour quitter")
        print("=" * 60)
        
        # Get control mode from config
        control_mode = sim_config.get_control_mode()
        
        # Create and run simulation
        if sim_config.is_normal_mode():
            # Mode normal (automatic cycling)
            run_normal_simulation(control_mode)
        
        elif sim_config.is_dqn_mode():
            # Mode DQN (agent control)
            run_dqn_simulation(control_mode)
        
        print("\n[OK] Simulation terminée avec succès")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Simulation interrompue par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERREUR] Une erreur s'est produite: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_normal_simulation(control_mode):
    """
    Run simulation in normal mode (automatic cycling)
    
    Args:
        control_mode (str): Control mode ('auto' or 'manual')
    """
    print("\n[MODE NORMAL] Cycle automatique des feux")
    
    # Create simulation manager
    simulation = SimulationManager(control_mode=control_mode)
    
    # Override config settings if needed
    if not sim_config.USE_RANDOM_GREEN_TIMER:
        # Use fixed durations
        for i, duration in sim_config.FIXED_GREEN_DURATIONS.items():
            simulation.signal_manager.signals[i].green = duration
            simulation.signal_manager.signals[i].initial_green = duration
    
    # Set stats display
    simulation.show_stats = sim_config.SHOW_STATS
    simulation.stats_update_interval = sim_config.STATS_UPDATE_INTERVAL
    
    # Run the simulation
    simulation.run()


def run_dqn_simulation(control_mode):
    """
    Run simulation in DQN mode (agent control)
    
    Args:
        control_mode (str): Control mode ('auto' or 'manual')
    """
    print("\n[MODE DQN] Contrôle par agent DQN")
    
    # Check if DQN module is available
    try:
        # This will be imported when you create the DQN module
        # For now, we'll create a placeholder
        from dqn_agent import DQNTrafficAgent
        dqn_available = True
    except ImportError:
        print("\n[AVERTISSEMENT] Module DQN non trouvé!")
        print("Le module 'dqn_agent.py' n'existe pas encore.")
        print("La simulation tournera en mode manuel pour l'instant.")
        dqn_available = False
    
    # Create simulation manager in manual mode
    simulation = SimulationManager(control_mode='manual')
    simulation.show_stats = sim_config.SHOW_STATS
    simulation.stats_update_interval = sim_config.STATS_UPDATE_INTERVAL
    
    if dqn_available:
        # Initialize DQN agent
        agent = DQNTrafficAgent(
            config=sim_config.DQN_PARAMS,
            rewards=sim_config.DQN_REWARDS
        )
        
        if sim_config.DQN_TRAINING_MODE:
            print(f"[DQN] Mode entraînement - {sim_config.DQN_TRAINING_EPISODES} épisodes")
            # Run training
            train_dqn_agent(simulation, agent)
        else:
            print(f"[DQN] Mode inférence - Chargement du modèle")
            # Load trained model
            agent.load_model(sim_config.DQN_MODEL_PATH)
            # Run with trained agent
            run_with_dqn_agent(simulation, agent)
    else:
        # Run without DQN (manual mode for testing)
        print("\n[INFO] Exécution en mode manuel (sans DQN)")
        print("Vous pouvez tester les commandes avec la touche M")
        simulation.run()


def train_dqn_agent(simulation, agent):
    """
    Train the DQN agent
    
    Args:
        simulation: SimulationManager instance
        agent: DQNTrafficAgent instance
    """
    print("\n[DQN] Démarrage de l'entraînement...")
    
    # This is a placeholder for the actual training loop
    # You'll implement this when you create the DQN agent
    
    import threading
    import time
    
    # Flag to control training
    training_active = True
    
    def training_loop():
        """Background thread for DQN training"""
        episode = 0
        
        while training_active and episode < sim_config.DQN_TRAINING_EPISODES:
            # Wait for decision interval
            time.sleep(sim_config.DQN_DECISION_INTERVAL)
            
            if not simulation.running:
                break
            
            # Get current state
            signal_state = simulation.signal_manager.get_current_signal_state()
            traffic_state = simulation.vehicle_manager.get_traffic_state_for_dqn()
            
            # Agent selects action (to be implemented)
            # action = agent.select_action(signal_state, traffic_state)
            
            # Execute action (to be implemented)
            # reward = execute_action(simulation, action)
            
            # Store experience and train (to be implemented)
            # agent.store_experience(state, action, reward, next_state)
            # agent.train()
            
            if episode % 100 == 0:
                print(f"[DQN] Épisode {episode}/{sim_config.DQN_TRAINING_EPISODES}")
            
            episode += 1
        
        # Save trained model
        print(f"\n[DQN] Sauvegarde du modèle → {sim_config.DQN_MODEL_PATH}")
        # agent.save_model(sim_config.DQN_MODEL_PATH)
    
    # Start training thread
    training_thread = threading.Thread(target=training_loop, daemon=True)
    training_thread.start()
    
    # Run simulation
    simulation.run()
    
    # Stop training
    training_active = False
    training_thread.join(timeout=2)


def run_with_dqn_agent(simulation, agent):
    """
    Run simulation with trained DQN agent
    
    Args:
        simulation: SimulationManager instance
        agent: DQNTrafficAgent instance (trained)
    """
    print("\n[DQN] Exécution avec agent entraîné...")
    
    import threading
    import time
    
    agent_active = True
    
    def agent_control_loop():
        """Background thread for DQN agent control"""
        while agent_active and simulation.running:
            # Wait for decision interval
            time.sleep(sim_config.DQN_DECISION_INTERVAL)
            
            if not simulation.running:
                break
            
            # Get current state
            signal_state = simulation.signal_manager.get_current_signal_state()
            traffic_state = simulation.vehicle_manager.get_traffic_state_for_dqn()
            
            # Agent selects best action (no exploration)
            # action = agent.select_action(signal_state, traffic_state, explore=False)
            
            # Execute action
            # execute_action(simulation, action)
            
            if sim_config.SHOW_DQN_INFO:
                print(f"[DQN] Signal actuel: {signal_state['current_green']}")
    
    # Start agent control thread
    agent_thread = threading.Thread(target=agent_control_loop, daemon=True)
    agent_thread.start()
    
    # Run simulation
    simulation.run()
    
    # Stop agent
    agent_active = False
    agent_thread.join(timeout=2)


def execute_action(simulation, action):
    """
    Execute an action chosen by the DQN agent
    
    Args:
        simulation: SimulationManager instance
        action (int): Action to execute
        
    Returns:
        float: Reward for the action
    """
    # This is a placeholder - to be implemented with actual DQN
    
    # Example action space:
    # 0-3: Activate signal 0-3
    # 4: Extend current green by 5s
    # 5: Force switch to next
    
    if action < 4:
        # Activate specific signal
        simulation.signal_manager.activate_green_signal(
            action, 
            vehicles_dict=simulation.vehicle_manager.vehicles
        )
    elif action == 4:
        # Extend current green
        simulation.signal_manager.extend_green_duration(5)
    elif action == 5:
        # Force switch
        simulation.signal_manager.force_switch_to_next(
            vehicles_dict=simulation.vehicle_manager.vehicles
        )
    
    # Calculate reward (placeholder)
    reward = 0.0
    
    # Add rewards based on traffic improvement
    # This will be implemented properly in the DQN module
    
    return reward


if __name__ == "__main__":
    main()