"""
Configuration CORRIGÉE pour un entraînement DQN fonctionnel
Basée sur l'analyse de vos logs d'entraînement
"""

# =========================================
# MODE DE SIMULATION
# =========================================

SIMULATION_MODE = 'DQN'
DQN_TRAINING_MODE = True

# =========================================
# PARAMÈTRES D'ENTRAÎNEMENT OPTIMISÉS
# =========================================

# Nombre d'épisodes
DQN_TRAINING_EPISODES = 50

# CRITIQUE : Intervalle de décision optimisé
# 8s permet de voir les effets tout en gardant une bonne réactivité
DQN_DECISION_INTERVAL = 8  # Optimisé (était 10s)

DQN_MODEL_PATH = 'models/dqn_traffic_agent_fixed.pth'

# =========================================
# PARAMÈTRES DQN OPTIMISÉS
# =========================================

DQN_PARAMS = {
    # Learning rate faible pour stabilité
    'learning_rate': 0.0001,
    
    # Gamma augmenté pour vision à long terme
    'gamma': 0.99,  # Augmenté de 0.95 à 0.99
    
    # CRITIQUE : Exploration très lente pour bien apprendre
    'epsilon_start': 1.0,
    'epsilon_end': 0.01,
    'epsilon_decay': 0.9997,  # Encore plus lent (était 0.9995)
    # Avec 0.9997, epsilon reste > 0.5 pendant ~1500 steps
    
    # Batch size réduit
    'batch_size': 32,
    
    # Mémoire suffisante
    'memory_size': 10000,
    
    # Target update fréquent
    'target_update': 100
}

# =========================================
# RÉCOMPENSES DELTA-BASED (COMPLÈTEMENT REPENSÉES)
# =========================================

# PHILOSOPHIE : Récompenser l'AMÉLIORATION, pas pénaliser l'état absolu
# L'agent doit apprendre à faire PROGRESSER le trafic

DQN_REWARDS = {
    # OBJECTIF PRINCIPAL : Faire passer les véhicules
    'vehicle_crossed': 10.0,  # Récompense élevée pour chaque véhicule qui traverse
    
    # OBJECTIF SECONDAIRE : Réduire les files d'attente (delta-based)
    'waiting_reduction': 2.0,  # NOUVEAU: Récompense pour réduction de la file
    'waiting_increase_penalty': -1.0,  # NOUVEAU: Pénalité pour augmentation de la file
    
    # BONUS : Équilibrage du trafic
    'traffic_balance_bonus': 2.0,  # Bonus pour trafic équilibré
    
    # SUPPRIMÉS : Ces pénalités constantes causaient le drainage des rewards
    # 'waiting_penalty': -0.05,  # SUPPRIMÉ (causait accumulation de pénalités)
    # 'long_wait_penalty': -0.5,  # SUPPRIMÉ (causait accumulation de pénalités)
    # 'efficient_switch_bonus': 5.0,  # SUPPRIMÉ (pas utilisé dans le code)
}

# =========================================
# AFFICHAGE
# =========================================

SHOW_STATS = True
SHOW_DQN_INFO = True
STATS_UPDATE_INTERVAL = 10  # Toutes les 10 secondes

# =========================================
# SAUVEGARDE
# =========================================

AUTO_SAVE_STATS = True
AUTO_SAVE_INTERVAL = 300
SAVE_DIRECTORY = 'saved_data/'


# =========================================
# MODE NORMAL (pour comparer)
# =========================================

USE_RANDOM_GREEN_TIMER = True
RANDOM_GREEN_RANGE = [10, 20]
FIXED_GREEN_DURATIONS = {0: 15, 1: 15, 2: 15, 3: 15}


# =========================================
# FONCTIONS UTILITAIRES (NE PAS MODIFIER)
# =========================================

def get_control_mode():
    if SIMULATION_MODE == 'DQN':
        return 'manual'
    else:
        return 'auto'

def is_dqn_mode():
    return SIMULATION_MODE == 'DQN'

def is_normal_mode():
    return SIMULATION_MODE == 'NORMAL'

def validate_config():
    valid = True
    
    if SIMULATION_MODE not in ['NORMAL', 'DQN']:
        print(f"[ERREUR] SIMULATION_MODE invalide: {SIMULATION_MODE}")
        valid = False
    
    if SIMULATION_MODE == 'DQN':
        if DQN_DECISION_INTERVAL < 1:
            print("[AVERTISSEMENT] DQN_DECISION_INTERVAL trop petit (< 1s)")
        
        if DQN_PARAMS['learning_rate'] <= 0:
            print("[ERREUR] learning_rate doit être > 0")
            valid = False
        
        if not (0 <= DQN_PARAMS['gamma'] <= 1):
            print("[ERREUR] gamma doit être entre 0 et 1")
            valid = False
    
    return valid

def print_config_summary():
    print("\n" + "="*60)
    print("CONFIGURATION DE LA SIMULATION")
    print("="*60)
    print(f"Mode: {SIMULATION_MODE}")
    print(f"Contrôle: {get_control_mode()}")
    
    if is_dqn_mode():
        print(f"\nParamètres Mode DQN:")
        print(f"  - Entraînement: {DQN_TRAINING_MODE}")
        if DQN_TRAINING_MODE:
            print(f"  - Épisodes: {DQN_TRAINING_EPISODES}")
        print(f"  - Intervalle décision: {DQN_DECISION_INTERVAL}s")
        print(f"  - Learning rate: {DQN_PARAMS['learning_rate']}")
        print(f"  - Epsilon decay: {DQN_PARAMS['epsilon_decay']}")
        print(f"\n  RÉCOMPENSES:")
        print(f"  - Vehicle crossed: {DQN_REWARDS['vehicle_crossed']}")
        print(f"  - Waiting penalty: {DQN_REWARDS['waiting_penalty']}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    if validate_config():
        print("[OK] Configuration valide")
        print_config_summary()
    else:
        print("[ERREUR] Configuration invalide!")