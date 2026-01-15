"""
Pipeline principal para análise de risco de hipertensão.
Executa todo o workflow de Machine Learning do projeto.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Adicionar src ao path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from src.data.data_loader import HypertensionDataLoader
from src.data.preprocessor import MedicalDataPreprocessor
from src.data.feature_engineering import MedicalFeatureEngineer
from src.models.ensemble_models import HypertensionEnsemble
from src.evaluation.visualization import ModelVisualizer
from src.evaluation.medical_analysis import MedicalAnalyzer
from src.analysis.interpretability import ModelInterpreter
from src.utils.helpers import print_section
from src.utils.config import load_config


def run_complete_pipeline(data_path: str, quick_run: bool = False):
    """
    Executa pipeline completo de Machine Learning.
    
    Args:
        data_path: Caminho para o arquivo de dados
        quick_run: Se True, executa versão rápida para testes
    """
    print_section("🚀 INICIANDO PIPELINE COMPLETO DE ML - HIPERTENSÃO", "=", 80)
    
    config = load_config()
    
    # 1. CARREGAMENTO E EXPLORAÇÃO DOS DADOS
    print_section("📊 FASE 1: CARREGAMENTO E EXPLORAÇÃO DOS DADOS")
    
    loader = HypertensionDataLoader()
    df = loader.load_data(data_path)
    
    if df is None:
        print("❌ Erro ao carregar dados. Verifique o caminho do arquivo.")
        return False
    
    # EDA básica
    eda_results = loader.perform_basic_eda(df)
    
    # 2. PRÉ-PROCESSAMENTO DOS DADOS  
    print_section("🔧 FASE 2: PRÉ-PROCESSAMENTO DOS DADOS")
    
    preprocessor = MedicalDataPreprocessor()
    
    # Limpeza e validação
    df_clean = preprocessor.clean_and_validate(df)
    
    # Tratamento de valores ausentes
    df_processed = preprocessor.handle_missing_values(df_clean)
    
    # Detecção de outliers
    outliers_info = preprocessor.detect_outliers(df_processed)
    
    # 3. FEATURE ENGINEERING
    print_section("⚙️ FASE 3: FEATURE ENGINEERING")
    
    feature_engineer = MedicalFeatureEngineer()
    
    # Criar features médicas especializadas
    df_features = feature_engineer.create_blood_pressure_features(df_processed)
    df_features = feature_engineer.create_cardiovascular_features(df_features)
    df_features = feature_engineer.create_risk_interaction_features(df_features)
    
    # Seleção de features
    target_col = config['data']['target_column']
    selected_features = feature_engineer.select_features(
        df_features, target_col, 
        max_features=20 if quick_run else 30
    )
    
    # 4. TREINAMENTO DE MODELOS
    print_section("🤖 FASE 4: TREINAMENTO DE MODELOS")
    
    # Preparar dados para treinamento
    X = df_features[selected_features['selected_features']]
    y = df_features[target_col]
    
    # Treinar ensemble de modelos
    ensemble = HypertensionEnsemble()
    
    if quick_run:
        # Versão rápida para testes
        results = ensemble.train_quick_ensemble(X, y)
    else:
        # Treinamento completo
        results = ensemble.train_complete_ensemble(X, y)
    
    # 5. AVALIAÇÃO E VISUALIZAÇÃO
    print_section("📈 FASE 5: AVALIAÇÃO E VISUALIZAÇÃO")
    
    visualizer = ModelVisualizer()
    
    # Criar visualizações dos modelos
    visualizer.create_model_comparison_plots(results)
    visualizer.create_feature_importance_plots(results, selected_features)
    
    # Salvar o melhor modelo
    best_model_path = ensemble.save_best_model(results)
    
    # 6. ANÁLISE MÉDICA
    print_section("🏥 FASE 6: ANÁLISE MÉDICA ESPECIALIZADA")
    
    medical_analyzer = MedicalAnalyzer()
    medical_report = medical_analyzer.create_medical_report(df_features, target_col)
    
    # 7. INTERPRETABILIDADE
    print_section("🔍 FASE 7: INTERPRETABILIDADE DO MODELO")
    
    if best_model_path and not quick_run:
        interpreter = ModelInterpreter()
        
        # Carregar dados de teste
        X_test = results['test_data']['X_test']
        y_test = results['test_data']['y_test']
        X_train = results['test_data']['X_train']
        
        # Carregar modelo e analisar
        interpreter.load_model_and_data(best_model_path, X_test, y_test, X_train)
        
        # Análise de importância
        feature_importance = interpreter.analyze_feature_importance()
        
        # Criar explicações SHAP
        shap_explanations = interpreter.create_shap_explanations(n_samples=100)
        
        # Análise de dependência parcial
        partial_dependence = interpreter.analyze_partial_dependence()
        
        # Criar visualizações
        interpreter.create_interpretation_visualizations()
        
        # Gerar relatório de interpretabilidade
        interpretation_report = interpreter.generate_interpretation_report()
    
    # 8. RELATÓRIO FINAL
    print_section("📋 FASE 8: RELATÓRIO FINAL", "=", 80)
    
    print("✅ PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
    print(f"📊 Dados processados: {len(df_features):,} amostras")
    print(f"🎯 Features selecionadas: {len(selected_features['selected_features'])}")
    print(f"🤖 Melhor modelo: {results['best_model']['name']} (Acurácia: {results['best_model']['accuracy']:.3f})")
    
    if best_model_path:
        print(f"💾 Modelo salvo em: {best_model_path}")
    
    print(f"📈 Visualizações salvas em: {config['paths']['figures_dir']}")
    print(f"📋 Relatórios salvos em: {config['paths']['reports_dir']}")
    
    # Resumo médico
    dados_gerais = medical_report['dados_gerais']
    print(f"\n🏥 RESUMO MÉDICO:")
    print(f"   • Prevalência de hipertensão: {dados_gerais['prevalencia_hipertensao']:.1f}%")
    print(f"   • Idade média da população: {dados_gerais['idade_media']:.1f} anos")
    print(f"   • Pressão arterial média: {dados_gerais['pressao_sistolica_media']:.0f}/{dados_gerais['pressao_diastolica_media']:.0f} mmHg")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Revisar relatórios médicos gerados")
    print("   2. Validar insights clínicos com especialistas")
    print("   3. Implementar modelo em ambiente de produção")
    print("   4. Configurar monitoramento contínuo")
    
    return True


def run_quick_analysis(data_path: str):
    """
    Executa análise rápida para verificação do pipeline.
    """
    print_section("⚡ ANÁLISE RÁPIDA DO PIPELINE")
    
    try:
        return run_complete_pipeline(data_path, quick_run=True)
    except Exception as e:
        print(f"❌ Erro na análise rápida: {e}")
        return False


def main():
    """
    Função principal com interface de linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline de Machine Learning para Análise de Risco de Hipertensão",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py dados.csv                    # Pipeline completo
  python main.py dados.csv --quick           # Análise rápida
  python main.py --demo                      # Dados de demonstração
        """
    )
    
    parser.add_argument(
        'data_file', 
        nargs='?',
        help='Caminho para o arquivo de dados CSV'
    )
    
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Executar versão rápida do pipeline (para testes)'
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Executar com dados de demonstração'
    )
    
    args = parser.parse_args()
    
    # Verificar argumentos
    if args.demo:
        # Usar dados de demonstração do notebook
        data_path = "notebooks/Hypertension-risk-model-main.csv"
    elif args.data_file:
        data_path = args.data_file
    else:
        print("❌ Erro: Especifique um arquivo de dados ou use --demo")
        parser.print_help()
        return
    
    # Verificar se arquivo existe
    if not Path(data_path).exists():
        print(f"❌ Erro: Arquivo não encontrado: {data_path}")
        return
    
    # Executar pipeline
    if args.quick:
        success = run_quick_analysis(data_path)
    else:
        success = run_complete_pipeline(data_path)
    
    if success:
        print("\n🎉 Pipeline executado com sucesso!")
    else:
        print("\n❌ Pipeline falhou. Verifique os logs para detalhes.")


if __name__ == "__main__":
    main()