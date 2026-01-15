"""
Módulo para modelos ensemble avançados e otimização.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import joblib
import json
from pathlib import Path

# Modelos base
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, StackingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Validação e métricas
from sklearn.model_selection import cross_val_score, StratifiedKFold, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix, roc_curve, precision_recall_curve
)

# Otimização
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️  Optuna não disponível - usando GridSearch como fallback")

import warnings
warnings.filterwarnings('ignore')

from ..utils.config import load_config, get_results_path
from ..utils.helpers import print_section


class EnsembleModelManager:
    """
    Gerenciador de modelos ensemble avançados para predição de hipertensão.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de modelos ensemble.
        """
        self.config = load_config()
        self.models = {}
        self.ensemble_models = {}
        self.best_models = {}
        self.results = {}
        self.cv_results = {}
        
        # Configurar modelos base
        self._setup_base_models()
        
    def _setup_base_models(self) -> None:
        """
        Configura modelos base com parâmetros otimizados.
        """
        model_params = self.config.get('models', {})
        general_params = self.config.get('general', {})
        random_state = general_params.get('random_state', 42)
        
        self.models = {
            'logistic_regression': LogisticRegression(
                random_state=random_state,
                max_iter=2000,
                solver='liblinear',
                class_weight='balanced'
            ),
            
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=random_state,
                n_jobs=-1
            ),
            
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=random_state
            ),
            
            'xgboost': XGBClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=random_state,
                eval_metric='logloss',
                n_jobs=-1
            ),
            
            'lightgbm': LGBMClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=random_state,
                n_jobs=-1,
                verbosity=-1
            ),
            
            'svm': SVC(
                kernel='rbf',
                probability=True,
                class_weight='balanced',
                random_state=random_state
            ),
            
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=1000,
                random_state=random_state,
                early_stopping=True
            ),
            
            'knn': KNeighborsClassifier(
                n_neighbors=7,
                weights='distance',
                n_jobs=-1
            )
        }
    
    def train_base_models(self, X_train: pd.DataFrame, y_train: pd.Series, 
                         cv_folds: int = 5) -> Dict[str, Dict[str, float]]:
        """
        Treina todos os modelos base com validação cruzada.
        
        Args:
            X_train: Features de treino
            y_train: Target de treino
            cv_folds: Número de folds para validação cruzada
            
        Returns:
            Dict com resultados de validação cruzada
        """
        print_section("TREINAMENTO DE MODELOS BASE COM VALIDAÇÃO CRUZADA")
        
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        self.cv_results = {}
        
        for name, model in self.models.items():
            print(f"\\n🔄 Treinando {name}...")
            
            try:
                # Validação cruzada
                cv_scores = {
                    'accuracy': cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy', n_jobs=-1),
                    'precision': cross_val_score(model, X_train, y_train, cv=cv, scoring='precision', n_jobs=-1),
                    'recall': cross_val_score(model, X_train, y_train, cv=cv, scoring='recall', n_jobs=-1),
                    'f1': cross_val_score(model, X_train, y_train, cv=cv, scoring='f1', n_jobs=-1),
                    'roc_auc': cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=-1)
                }
                
                # Estatísticas resumidas
                cv_summary = {
                    metric: {
                        'mean': scores.mean(),
                        'std': scores.std(),
                        'min': scores.min(),
                        'max': scores.max()
                    }
                    for metric, scores in cv_scores.items()
                }
                
                self.cv_results[name] = cv_summary
                
                # Treinar modelo final
                model.fit(X_train, y_train)
                
                print(f"  ✅ {name} treinado")
                print(f"     AUC: {cv_summary['roc_auc']['mean']:.3f} (±{cv_summary['roc_auc']['std']:.3f})")
                print(f"     F1:  {cv_summary['f1']['mean']:.3f} (±{cv_summary['f1']['std']:.3f})")
                
            except Exception as e:
                print(f"  ❌ Erro ao treinar {name}: {e}")
                continue
        
        return self.cv_results
    
    def create_voting_ensemble(self, X_train: pd.DataFrame, y_train: pd.Series,
                              voting_type: str = 'soft') -> VotingClassifier:
        """
        Cria ensemble de votação com os melhores modelos.
        
        Args:
            X_train: Features de treino
            y_train: Target de treino
            voting_type: Tipo de votação ('hard' ou 'soft')
            
        Returns:
            VotingClassifier treinado
        """
        print_section("CRIANDO ENSEMBLE DE VOTAÇÃO")
        
        # Selecionar top 5 modelos baseado na AUC
        if not self.cv_results:
            print("⚠️  Execute train_base_models() primeiro")
            return None
        
        # Ranking por AUC
        model_ranking = sorted(
            self.cv_results.items(),
            key=lambda x: x[1]['roc_auc']['mean'],
            reverse=True
        )
        
        print("🏆 Ranking de modelos por AUC:")
        for i, (name, results) in enumerate(model_ranking[:5], 1):
            auc = results['roc_auc']['mean']
            std = results['roc_auc']['std']
            print(f"  {i}. {name}: {auc:.3f} (±{std:.3f})")
        
        # Selecionar top modelos para ensemble
        selected_models = [
            (name, self.models[name]) 
            for name, _ in model_ranking[:5]
            if name in self.models
        ]
        
        # Criar ensemble
        voting_ensemble = VotingClassifier(
            estimators=selected_models,
            voting=voting_type,
            n_jobs=-1
        )
        
        print(f"\\n🗳️  Criando ensemble de votação ({voting_type}) com {len(selected_models)} modelos...")
        voting_ensemble.fit(X_train, y_train)
        
        self.ensemble_models['voting_' + voting_type] = voting_ensemble
        
        print("✅ Ensemble de votação criado e treinado!")
        return voting_ensemble
    
    def create_stacking_ensemble(self, X_train: pd.DataFrame, y_train: pd.Series,
                               meta_learner: str = 'logistic') -> StackingClassifier:
        """
        Cria ensemble de stacking com meta-learner.
        
        Args:
            X_train: Features de treino
            y_train: Target de treino
            meta_learner: Tipo de meta-learner
            
        Returns:
            StackingClassifier treinado
        """
        print_section("CRIANDO ENSEMBLE DE STACKING")
        
        if not self.cv_results:
            print("⚠️  Execute train_base_models() primeiro")
            return None
        
        # Selecionar modelos diversos (diferentes tipos)
        diverse_models = [
            ('rf', self.models['random_forest']),
            ('xgb', self.models['xgboost']),
            ('svm', self.models['svm']),
            ('nn', self.models['neural_network']),
            ('lgbm', self.models['lightgbm'])
        ]
        
        # Meta-learner
        if meta_learner == 'logistic':
            final_estimator = LogisticRegression(random_state=42, max_iter=1000)
        elif meta_learner == 'rf':
            final_estimator = RandomForestClassifier(n_estimators=50, random_state=42)
        else:
            final_estimator = LogisticRegression(random_state=42, max_iter=1000)
        
        # Criar stacking ensemble
        stacking_ensemble = StackingClassifier(
            estimators=diverse_models,
            final_estimator=final_estimator,
            cv=3,  # Cross-validation para meta-features
            n_jobs=-1
        )
        
        print(f"🏗️  Criando ensemble de stacking com meta-learner: {meta_learner}")
        print(f"📊 Base learners: {[name for name, _ in diverse_models]}")
        
        stacking_ensemble.fit(X_train, y_train)
        
        self.ensemble_models['stacking_' + meta_learner] = stacking_ensemble
        
        print("✅ Ensemble de stacking criado e treinado!")
        return stacking_ensemble
    
    def optimize_hyperparameters(self, X_train: pd.DataFrame, y_train: pd.Series,
                                models_to_optimize: List[str] = None,
                                method: str = 'optuna') -> Dict[str, Any]:
        """
        Otimiza hiperparâmetros dos modelos selecionados.
        
        Args:
            X_train: Features de treino
            y_train: Target de treino
            models_to_optimize: Lista de modelos para otimizar
            method: Método de otimização ('optuna', 'grid', 'random')
            
        Returns:
            Dict com melhores parâmetros encontrados
        """
        print_section("OTIMIZAÇÃO DE HIPERPARÂMETROS")
        
        if models_to_optimize is None:
            # Otimizar top 3 modelos
            if self.cv_results:
                model_ranking = sorted(
                    self.cv_results.items(),
                    key=lambda x: x[1]['roc_auc']['mean'],
                    reverse=True
                )
                models_to_optimize = [name for name, _ in model_ranking[:3]]
            else:
                models_to_optimize = ['random_forest', 'xgboost', 'lightgbm']
        
        optimization_results = {}
        
        for model_name in models_to_optimize:
            if model_name not in self.models:
                continue
                
            print(f"\\n🔍 Otimizando {model_name}...")
            
            if method == 'optuna' and OPTUNA_AVAILABLE:
                best_params = self._optimize_with_optuna(model_name, X_train, y_train)
            else:
                best_params = self._optimize_with_sklearn(model_name, X_train, y_train, method)
            
            optimization_results[model_name] = best_params
            
            # Criar modelo otimizado
            optimized_model = self._create_model_with_params(model_name, best_params)
            optimized_model.fit(X_train, y_train)
            self.best_models[model_name] = optimized_model
            
            print(f"  ✅ {model_name} otimizado!")
        
        return optimization_results
    
    def _optimize_with_optuna(self, model_name: str, X_train: pd.DataFrame, 
                            y_train: pd.Series, n_trials: int = 50) -> Dict[str, Any]:
        """
        Otimização com Optuna (Bayesian Optimization).
        """
        def objective(trial):
            params = self._get_optuna_params(model_name, trial)
            model = self._create_model_with_params(model_name, params)
            
            cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
            scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='roc_auc', n_jobs=-1)
            
            return scores.mean()
        
        study = optuna.create_study(direction='maximize', 
                                   sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
        
        print(f"    Best AUC: {study.best_value:.4f}")
        return study.best_params
    
    def _optimize_with_sklearn(self, model_name: str, X_train: pd.DataFrame,
                             y_train: pd.Series, method: str = 'grid') -> Dict[str, Any]:
        """
        Otimização com GridSearch ou RandomizedSearch.
        """
        param_grid = self._get_sklearn_param_grid(model_name)
        base_model = self._create_model_with_params(model_name, {})
        
        cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        
        if method == 'grid':
            search = GridSearchCV(
                base_model, param_grid, cv=cv, scoring='roc_auc',
                n_jobs=-1, verbose=0
            )
        else:  # random
            search = RandomizedSearchCV(
                base_model, param_grid, cv=cv, scoring='roc_auc',
                n_jobs=-1, verbose=0, n_iter=20, random_state=42
            )
        
        search.fit(X_train, y_train)
        
        print(f"    Best AUC: {search.best_score_:.4f}")
        return search.best_params_
    
    def _get_optuna_params(self, model_name: str, trial) -> Dict[str, Any]:
        """
        Define espaço de busca para Optuna.
        """
        if model_name == 'random_forest':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 20),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10)
            }
        elif model_name == 'xgboost':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
            }
        elif model_name == 'lightgbm':
            return {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'num_leaves': trial.suggest_int('num_leaves', 10, 100)
            }
        else:
            return {}
    
    def _get_sklearn_param_grid(self, model_name: str) -> Dict[str, List]:
        """
        Define grade de parâmetros para GridSearch/RandomizedSearch.
        """
        grids = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.05, 0.1, 0.2],
                'max_depth': [3, 4, 6],
                'subsample': [0.8, 0.9, 1.0]
            },
            'lightgbm': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.05, 0.1, 0.2],
                'max_depth': [3, 4, 6],
                'num_leaves': [20, 50, 100]
            }
        }
        return grids.get(model_name, {})
    
    def _create_model_with_params(self, model_name: str, params: Dict[str, Any]):
        """
        Cria modelo com parâmetros específicos.
        """
        base_params = {
            'random_state': 42,
            'n_jobs': -1
        }
        
        if model_name == 'random_forest':
            return RandomForestClassifier(**{**base_params, **params, 'class_weight': 'balanced'})
        elif model_name == 'xgboost':
            return XGBClassifier(**{**base_params, **params, 'eval_metric': 'logloss'})
        elif model_name == 'lightgbm':
            return LGBMClassifier(**{**base_params, **params, 'verbosity': -1})
        elif model_name == 'gradient_boosting':
            return GradientBoostingClassifier(**{**base_params, **params})
        else:
            return self.models[model_name]
    
    def evaluate_all_models(self, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
        """
        Avalia todos os modelos (base + ensemble) no conjunto de teste.
        
        Args:
            X_test: Features de teste
            y_test: Target de teste
            
        Returns:
            DataFrame com resultados de todos os modelos
        """
        print_section("AVALIAÇÃO FINAL DE TODOS OS MODELOS")
        
        all_models = {**self.models, **self.ensemble_models, **self.best_models}
        results = []
        
        for name, model in all_models.items():
            if not hasattr(model, 'predict'):
                continue
                
            print(f"🔍 Avaliando {name}...")
            
            try:
                # Predições
                y_pred = model.predict(X_test)
                
                if hasattr(model, 'predict_proba'):
                    y_prob = model.predict_proba(X_test)[:, 1]
                elif hasattr(model, 'decision_function'):
                    y_prob = model.decision_function(X_test)
                else:
                    y_prob = y_pred  # Fallback
                
                # Métricas
                metrics = {
                    'Model': name,
                    'Accuracy': accuracy_score(y_test, y_pred),
                    'Precision': precision_score(y_test, y_pred, zero_division=0),
                    'Recall': recall_score(y_test, y_pred, zero_division=0),
                    'F1_Score': f1_score(y_test, y_pred, zero_division=0),
                    'ROC_AUC': roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0
                }
                
                results.append(metrics)
                
                print(f"  ✅ AUC: {metrics['ROC_AUC']:.3f}, F1: {metrics['F1_Score']:.3f}")
                
            except Exception as e:
                print(f"  ❌ Erro ao avaliar {name}: {e}")
                continue
        
        # Criar DataFrame e ordenar por AUC
        results_df = pd.DataFrame(results)
        if len(results_df) > 0:
            results_df = results_df.sort_values('ROC_AUC', ascending=False).reset_index(drop=True)
            results_df = results_df.round(4)
        
        self.results = results_df
        
        print(f"\\n🏆 RANKING FINAL DOS MODELOS:")
        if len(results_df) > 0:
            for i, row in results_df.head(5).iterrows():
                print(f"  {i+1}. {row['Model']}: AUC={row['ROC_AUC']:.3f}, F1={row['F1_Score']:.3f}")
        
        return results_df
    
    def save_best_model(self, model_name: str = None, save_path: str = None) -> str:
        """
        Salva o melhor modelo encontrado.
        
        Args:
            model_name: Nome específico do modelo (None = melhor por AUC)
            save_path: Caminho para salvar
            
        Returns:
            Caminho onde o modelo foi salvo
        """
        if len(self.results) == 0:
            print("❌ Execute evaluate_all_models() primeiro")
            return None
        
        # Selecionar modelo
        if model_name is None:
            best_row = self.results.iloc[0]
            model_name = best_row['Model']
        
        # Encontrar modelo
        all_models = {**self.models, **self.ensemble_models, **self.best_models}
        if model_name not in all_models:
            print(f"❌ Modelo {model_name} não encontrado")
            return None
        
        model = all_models[model_name]
        
        # Definir caminho de salvamento
        if save_path is None:
            results_path = get_results_path('models')
            save_path = results_path / f'best_model_{model_name.replace(" ", "_")}.pkl'
        
        # Salvar modelo
        joblib.dump(model, save_path)
        
        # Salvar metadados
        metadata = {
            'model_name': model_name,
            'model_type': type(model).__name__,
            'performance': self.results[self.results['Model'] == model_name].iloc[0].to_dict(),
            'training_date': pd.Timestamp.now().isoformat(),
            'features_count': len(model.feature_names_in_) if hasattr(model, 'feature_names_in_') else None
        }
        
        metadata_path = save_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Modelo salvo: {save_path}")
        print(f"📋 Metadados salvos: {metadata_path}")
        
        return str(save_path)
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo completo dos experimentos.
        
        Returns:
            Dict com resumo dos experimentos
        """
        summary = {
            'base_models_trained': len(self.models),
            'ensemble_models_created': len(self.ensemble_models),
            'optimized_models': len(self.best_models),
            'cv_results_available': len(self.cv_results) > 0,
            'final_evaluation_done': len(self.results) > 0,
            'best_model': self.results.iloc[0]['Model'] if len(self.results) > 0 else None,
            'best_auc': self.results.iloc[0]['ROC_AUC'] if len(self.results) > 0 else None
        }
        
        return summary


def create_ensemble_manager() -> EnsembleModelManager:
    \"\"\"Função de conveniência para criar gerenciador de ensemble.\"\"\"
    return EnsembleModelManager()


if __name__ == \"__main__\":
    print(\"🧪 Testando módulo EnsembleModelManager...\")
    
    # Criar dados de teste
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    X_test_data = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    y_test_data = pd.Series(np.random.choice([0, 1], n_samples, p=[0.7, 0.3]))
    
    # Testar gerenciador
    manager = EnsembleModelManager()
    
    print(f\"\\n✅ Teste concluído!\")
    print(f\"📊 {len(manager.models)} modelos base configurados\")
    print(f\"🏥 EnsembleModelManager pronto para uso\")"