"""
Script pour utiliser un agent DQN déjà entraîné
Usage: python run_trained_agent.py
"""
import os
import sys
import time
import threading

from managers import SimulationManager
from dqn_agent import DQNTrafficAgent
import simulation_config as config


def run_with_trained_agent(model_path=None):
    """
    Lance la simulation avec un agent DQN entraîné
    
    Args:
        model_path: Chemin vers le modèle (None = utilise config)
    """
    
    if model_path is None:
        model_path = config.DQN_MODEL_PATH
    
    # Vérifier que le modèle existe
    if not os.path.exists(model_path):
        print(f"\n[ERREUR] Modèle non trouvé: {model_path}")
        print("\nVous devez d'abord entraîner l'agent:")
        print("  1. Configurez simulation_config.py avec DQN_TRAINING_MODE = True")
        print("  2. Lancez: python train_dqn.py")
        sys.exit(1)
    
    print("\n" + "="*70)
    print(" " * 20 + "AGENT DQN ENTRAÎNÉ")
    print("="*70)
    print(f"Modèle: {model_path}")
    print("="*70 + "\n")
    
    # Créer la simulation
    print("[1/4] Création de la simulation...")
    simulation = SimulationManager(control_mode='manual')
    simulation.show_stats = True
    print("      ✓ Simulation créée")
    
    # Créer l'agent
    print("[2/4] Chargement de l'agent DQN...")
    agent = DQNTrafficAgent(
        config=config.DQN_PARAMS,
        rewards=config.DQN_REWARDS
    )
    print(f"      ✓ Agent créé (device: {agent.device})")
    
    # Charger le modèle entraîné
    print("[3/4] Chargement du modèle entraîné...")
    if agent.load_model(model_path):
        print("      ✓ Modèle chargé avec succès")
    else:
        print("      ✗ Échec du chargement")
        sys.exit(1)
    
    # Afficher les stats du modèle
    print(f"\nInformations du modèle:")
    print(f"  Épisodes d'entraînement: {agent.episodes_done}")
    print(f"  Étapes d'entraînement: {agent.steps_done}")
    print(f"  Epsilon final: {agent.epsilon:.4f}")
    
    # Variables de contrôle
    agent_active = True
    decision_count = 0
    
    def agent_control_loop():
        """Boucle de contrôle de l'agent"""
        nonlocal decision_count
        
        while agent_active and simulation.running:
            # Attendre l'intervalle de décision
            time.sleep(config.DQN_DECISION_INTERVAL)
            
            if not simulation.running:
                break
            
            try:
                # Obtenir l'état actuel
                signal_state = simulation.signal_manager.get_current_signal_state()
                traffic_state = simulation.vehicle_manager.get_traffic_state_for_dqn()
                
                # Convertir en vecteur d'état
                state = agent.get_state(signal_state, traffic_state)
                
                # Agent choisit la meilleure action (pas d'exploration)
                action = agent.select_action(state, explore=False)
                
                # Exécuter l'action
                execute_action(simulation, action)
                
                decision_count += 1
                
                # Afficher les infos
                if config.SHOW_DQN_INFO and decision_count % 5 == 0:
                    action_names = [
                        "Activer DROITE", "Activer BAS", "Activer GAUCHE", 
                        "Activer HAUT", "Prolonger VERT", "Forcer SWITCH"
                    ]
                    print(f"\n[DQN] Décision #{decision_count}")
                    print(f"      Signal actuel: {signal_state['current_green']}")
                    print(f"      Action choisie: {action_names[action]}")
                    
                    # Afficher le trafic
                    for direction in ['right', 'down', 'left', 'up']:
                        waiting = traffic_state[direction]['waiting']
                        level = traffic_state[direction]['traffic_level']
                        print(f"      {direction:>5}: {waiting} en attente (niveau {level}/10)")
                
            except Exception as e:
                print(f"[ERREUR] Contrôle de l'agent: {e}")
                import traceback
                traceback.print_exc()
    
    # Démarrer le thread de contrôle
    print("\n[4/4] Démarrage du contrôle par l'agent...")
    control_thread = threading.Thread(target=agent_control_loop, daemon=True)
    control_thread.start()
    print("      ✓ Agent actif\n")
    
    print("="*70)
    print("Simulation en cours - L'agent DQN contrôle les feux")
    print("Appuyez sur S pour afficher/masquer les statistiques")
    print("Fermez la fenêtre pour arrêter")
    print("="*70 + "\n")
    
    # Lancer la simulation
    try:
        simulation.run()
    except KeyboardInterrupt:
        print("\n[INFO] Interruption par l'utilisateur")
    finally:
        agent_active = False
        control_thread.join(timeout=2)
        
        print("\n[OK] Simulation terminée")
        print(f"Décisions prises par l'agent: {decision_count}")


def execute_action(simulation, action):
    """
    Exécute une action choisie par l'agent
    
    Args:
        simulation: Instance de SimulationManager
        action: Action à exécuter (0-5)
    """
    vehicles_dict = simulation.vehicle_manager.vehicles
    
    if action < 4:
        # Activer un signal spécifique (0-3)
        simulation.signal_manager.activate_green_signal(
            action,
            vehicles_dict=vehicles_dict
        )
    elif action == 4:
        # Prolonger le vert actuel de 5 secondes
        simulation.signal_manager.extend_green_duration(5)
    elif action == 5:
        # Forcer le changement immédiat
        simulation.signal_manager.force_switch_to_next(
            vehicles_dict=vehicles_dict
        )


if __name__ == "__main__":
    # Vous pouvez spécifier un chemin de modèle différent
    # run_with_trained_agent('models/dqn_traffic_agent_best.pth')
    
    # Ou utiliser le modèle par défaut
    run_with_trained_agent()