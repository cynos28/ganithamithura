"""
Performance Metrics Model Configuration

Contains default configurations for all models in the ensemble.
"""

from typing import Dict


class ModelConfig:
    """Configuration class for performance metrics models."""

    # XGBoost Configuration
    XGBOOST_CONFIG = {
        'objective': 'multi:softprob',
        'eval_metric': 'mlogloss',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'min_child_weight': 1,
        'gamma': 0,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': 42,
        'tree_method': 'hist',
        'enable_categorical': False
    }

    # Random Forest Configuration
    RANDOM_FOREST_CONFIG = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'max_features': 'sqrt',
        'bootstrap': True,
        'random_state': 42,
        'n_jobs': -1
    }

    # Neural Network Configuration
    NEURAL_NETWORK_CONFIG = {
        'hidden_layer_sizes': (100, 50, 25),
        'activation': 'relu',
        'solver': 'adam',
        'alpha': 0.0001,
        'batch_size': 'auto',
        'learning_rate': 'adaptive',
        'learning_rate_init': 0.001,
        'max_iter': 300,
        'early_stopping': True,
        'validation_fraction': 0.1,
        'n_iter_no_change': 10,
        'random_state': 42
    }

    # SVM Configuration
    SVM_CONFIG = {
        'kernel': 'rbf',
        'C': 1.0,
        'gamma': 'scale',
        'probability': True,
        'class_weight': 'balanced',
        'random_state': 42,
        'max_iter': 1000
    }

    # LightGBM Configuration
    LIGHTGBM_CONFIG = {
        'objective': 'multiclass',
        'metric': 'multi_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'n_estimators': 100,
        'max_depth': -1,
        'min_child_samples': 20,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'reg_alpha': 0.1,
        'reg_lambda': 0.1,
        'random_state': 42,
        'verbose': -1
    }

    # Ensemble Weights Configuration
    ENSEMBLE_WEIGHTS = {
        'default': {
            'xgboost': 0.22,
            'random_forest': 0.18,
            'neural_network': 0.16,
            'svm': 0.16,
            'lightgbm': 0.20,
            'kmap': 0.08
        },
        'high_confidence': {
            'xgboost': 0.25,
            'random_forest': 0.20,
            'neural_network': 0.15,
            'svm': 0.15,
            'lightgbm': 0.20,
            'kmap': 0.05
        },
        'exploratory': {
            'xgboost': 0.18,
            'random_forest': 0.18,
            'neural_network': 0.16,
            'svm': 0.16,
            'lightgbm': 0.18,
            'kmap': 0.14
        }
    }

    # Feature Engineering Thresholds
    FEATURE_THRESHOLDS = {
        'score_threshold': 70.0,
        'time_threshold': 60.0,
        'efficiency_threshold': 1.0,
        'percentile_threshold': 50.0
    }

    # Performance Targets
    PERFORMANCE_TARGETS = {
        'level_accuracy': 0.94,  # 92-96% target
        'sublevel_accuracy': 0.90,  # 88-92% target
        'prediction_latency_ms': 150,  # <150ms target
        'system_reliability': 0.999  # 99.9% uptime
    }

    @classmethod
    def get_model_config(cls, model_name: str) -> Dict:
        """
        Get configuration for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Configuration dictionary
        """
        config_map = {
            'xgboost': cls.XGBOOST_CONFIG,
            'random_forest': cls.RANDOM_FOREST_CONFIG,
            'neural_network': cls.NEURAL_NETWORK_CONFIG,
            'svm': cls.SVM_CONFIG,
            'lightgbm': cls.LIGHTGBM_CONFIG
        }
        return config_map.get(model_name, {})

    @classmethod
    def get_ensemble_weights(cls, scenario: str = 'default') -> Dict:
        """
        Get ensemble weights for a specific scenario.

        Args:
            scenario: Weighting scenario name

        Returns:
            Weights dictionary
        """
        return cls.ENSEMBLE_WEIGHTS.get(scenario, cls.ENSEMBLE_WEIGHTS['default'])
