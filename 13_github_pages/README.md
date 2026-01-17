# GitHub Pages - Apresentação do Projeto

Esta pasta contém os arquivos para a página de apresentação do projeto hospedada no GitHub Pages.

## Estrutura

```
13_github_pages/
├── index.html              # Página principal
├── _config.yml             # Configuração Jekyll/GitHub Pages
├── css/
│   └── style.css           # Estilos responsivos
├── js/
│   ├── main.js             # Lógica principal da UI
│   └── api-integration.js  # Integração com API AWS
├── assets/
│   └── figures/            # Figuras SVG do projeto
│       ├── eda/            # Análise exploratória
│       ├── models/         # Comparação de modelos
│       ├── interpretability/  # Feature importance
│       └── clinical/       # Análise clínica
├── data/
│   └── metrics.json        # Métricas consolidadas
└── README.md               # Este arquivo
```

## Deploy no GitHub Pages

### Opção 1: Via Settings do Repositório

1. Faça push do repositório para o GitHub
2. Acesse: Settings > Pages
3. Source: Deploy from a branch
4. Branch: `main` (ou `master`)
5. Folder: `/13_github_pages` ou raiz `/`
6. Clique Save

### Opção 2: Mover para Raiz (Recomendado)

Para deploy mais simples, copie o conteúdo para a raiz do repositório:

```bash
# Criar branch gh-pages
git checkout -b gh-pages

# Copiar conteúdo
cp -r 13_github_pages/* .

# Commit e push
git add .
git commit -m "Deploy GitHub Pages"
git push origin gh-pages
```

Depois configure Settings > Pages > Branch: `gh-pages`

## URLs

### GitHub Pages
```
https://SEU-USUARIO.github.io/trabalho_tcc_mod_classifc_hipertensao/
```

### Demo AWS (Integrada)
```
https://dl52cpaeesvk0.cloudfront.net/ui/index.html
```

### API AWS
```
https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict
```

## Funcionalidades

### Seções da Página

1. **Hero**: Métricas principais e CTAs
2. **Problema**: Contexto da hipertensão
3. **Metodologia**: Pipeline de 5 etapas
4. **Dataset**: Estatísticas e features
5. **Resultados**: Comparação de modelos e métricas
6. **Interpretabilidade**: Feature importance e thresholds
7. **Demo**: Formulário integrado com API AWS
8. **Equipe**: Orientador e alunos

### Integração AWS

A página inclui um formulário de demonstração que:
- Coleta dados do paciente
- Envia para a API AWS via fetch
- Exibe resultado inline
- Oferece link para demo completa

## Desenvolvimento Local

```bash
# Usando Python
cd 13_github_pages
python -m http.server 8000
# Acesse: http://localhost:8000

# Usando Node.js
npx serve .
# Acesse: http://localhost:3000
```

## Responsividade

A página é totalmente responsiva:
- Desktop: Layout completo com grids
- Tablet: Layout adaptado
- Mobile: Layout em coluna única

## Figuras Incluídas

| Categoria | Arquivo | Descrição |
|-----------|---------|-----------|
| EDA | target_distribution.svg | Distribuição de classes |
| EDA | correlation_matrix.svg | Matriz de correlação |
| EDA | vif_analysis.svg | Análise VIF |
| Models | 01_comparison_p1_metricas.svg | Comparação de métricas |
| Models | 02_confusion_gradient_boosting.svg | Matriz de confusão |
| Models | 03_roc_p1_curvas.svg | Curvas ROC |
| Interp | 06_feat_p1_consenso.svg | Feature importance |
| Interp | 08_threshold_p1_metricas.svg | Análise de threshold |
| Clinical | clinical_performance_analysis.svg | Performance clínica |

## Cross-links

A página GitHub Pages e a Demo AWS estão integradas:

- **GitHub Pages → AWS**: Botão "Testar Modelo" e formulário de demo
- **AWS → GitHub Pages**: Link "Ver Metodologia" (a ser adicionado)

## Manutenção

### Atualizar Métricas

Edite `data/metrics.json` com novos valores.

### Adicionar Figuras

1. Copie SVG para `assets/figures/[categoria]/`
2. Adicione tag `<img>` no HTML

### Atualizar Estilos

Edite `css/style.css` - usa CSS Variables para fácil customização.

---

**Criado em**: 2026-01-17
**Última atualização**: 2026-01-17
