# 🚀 Deploy AWS - Documentação Completa

Este diretório contém todos os arquivos necessários para fazer o deploy da aplicação de predição de hipertensão na AWS.

## 📁 Estrutura de Arquivos

```
12_deploy_aws/
├── README.md                    # Este arquivo - índice e navegação
├── Dockerfile                   # Imagem Docker otimizada para Lambda
├── .dockerignore               # Otimização do build Docker
├── deploy_config.example.sh    # Template de configuração (copiar e editar)
├── deploy_aws.sh               # Script principal de deploy (executável)
├── test_local.sh               # Script de validação local (executável)
├── DEPLOY_RESUMO.md            # Guia rápido (5 passos, ~30 min)
├── GUIA_DEPLOY_RAPIDO.md       # Guia completo (13 passos, ~90 min)
├── CHECKLIST_DEPLOY.md         # Checklist de validação
├── DEPLOY_INDICE.md            # Índice detalhado de navegação
└── ARQUIVOS_CRIADOS.md         # Inventário completo
```

## 🎯 Por Onde Começar?

### 1️⃣ Primeira vez fazendo deploy na AWS?
👉 **Leia primeiro**: [GUIA_DEPLOY_RAPIDO.md](GUIA_DEPLOY_RAPIDO.md)

### 2️⃣ Já conhece AWS e quer fazer rápido?
👉 **Comece aqui**: [DEPLOY_RESUMO.md](DEPLOY_RESUMO.md)

### 3️⃣ Não sabe por onde começar?
👉 **Navegue aqui**: [DEPLOY_INDICE.md](DEPLOY_INDICE.md)

## ⚡ Deploy em 3 Comandos

```bash
# 1. Entre no diretório de deploy
cd 12_deploy_aws

# 2. Configure suas credenciais
cp deploy_config.example.sh deploy_config.sh
nano deploy_config.sh  # Edite: AWS_REGION, AWS_ACCOUNT_ID, S3_BUCKET_NAME

# 3. Execute o deploy
./deploy_aws.sh
```

## 📚 Guias Disponíveis

| Arquivo | Descrição | Quando Usar |
|---------|-----------|-------------|
| **DEPLOY_RESUMO.md** | Resumo executivo em 5 passos | Início rápido (~30 min) |
| **GUIA_DEPLOY_RAPIDO.md** | Tutorial completo passo a passo | Primeira vez (~90 min) |
| **CHECKLIST_DEPLOY.md** | Lista de validação | Durante o deploy |
| **DEPLOY_INDICE.md** | Índice de navegação | Encontrar informações |
| **ARQUIVOS_CRIADOS.md** | Inventário completo | Referência técnica |

## 🛠️ Scripts Disponíveis

### deploy_aws.sh (Principal)
Script automatizado com menu interativo:
- Opção 1: Deploy completo (ECR + Lambda + API Gateway)
- Opção 2: Apenas build e push da imagem Docker
- Opção 3: Apenas atualizar Lambda
- Opção 4: Deploy da UI no S3

**Uso**:
```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

### test_local.sh (Validação)
Testa a aplicação localmente antes do deploy:
- Verifica dependências (Python, Docker)
- Valida arquivos essenciais
- Verifica artefatos do modelo
- Opção de testar build Docker
- Opção de iniciar servidor local

**Uso**:
```bash
chmod +x test_local.sh
./test_local.sh
```

## 🏗️ Arquitetura do Deploy

```
┌─────────────────┐
│   CloudFront    │  ← Interface (HTML/CSS/JS)
│   + S3 Bucket   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  API Gateway    │  ← Endpoint público
└────────┬────────┘
         │ Invoke
         ▼
┌─────────────────┐
│  Lambda (ECR)   │  ← FastAPI + Modelo ML
└─────────────────┘
```

## ⚙️ Configuração Necessária

Antes de executar o deploy, você precisa:

1. **Conta AWS** ativa
2. **AWS CLI** instalado e configurado:
   ```bash
   aws configure
   ```
3. **Docker** instalado e rodando
4. **Credenciais AWS**:
   - AWS Account ID (12 dígitos)
   - AWS Region (ex: `us-east-1`)
   - Nome único para bucket S3

## 📋 Fluxo Recomendado

```
1. Ler DEPLOY_RESUMO.md ou GUIA_DEPLOY_RAPIDO.md
   ↓
2. Executar test_local.sh (validar localmente)
   ↓
3. Copiar deploy_config.example.sh → deploy_config.sh
   ↓
4. Editar deploy_config.sh com suas credenciais
   ↓
5. Executar deploy_aws.sh
   ↓
6. Seguir CHECKLIST_DEPLOY.md
   ↓
7. Aplicação online! 🎉
```

## 💰 Estimativa de Custos

Com AWS Free Tier (primeiros 12 meses):
- ✅ Lambda: 1M requisições/mês GRÁTIS
- ✅ API Gateway: 1M requisições/mês GRÁTIS
- ✅ S3: 5GB GRÁTIS
- ✅ CloudFront: 50GB transferência GRÁTIS

**Para TCC com baixo tráfego**: Custo zero ou < $5/mês

## 🔒 Segurança

**IMPORTANTE**: O arquivo `deploy_config.sh` contém credenciais AWS.
- ✅ Nunca commite este arquivo no Git
- ✅ Use apenas o arquivo `.example` como template
- ✅ Mantenha backup seguro local

## 🆘 Precisa de Ajuda?

1. Consulte a seção "Troubleshooting" em [GUIA_DEPLOY_RAPIDO.md](GUIA_DEPLOY_RAPIDO.md)
2. Verifique [CHECKLIST_DEPLOY.md](CHECKLIST_DEPLOY.md) - algum passo foi pulado?
3. Execute `test_local.sh` para validar localmente
4. Consulte a documentação técnica em `../04_reports/docs/DEPLOY_AWS.md`

## 📖 Documentação Adicional

Além dos arquivos neste diretório, consulte também:
- `../04_reports/docs/DEPLOY_AWS.md` - Documentação técnica detalhada
- `../04_reports/docs/PASSO_API_GATEWAY.md` - Configuração do API Gateway
- `../04_reports/docs/TUTORIAL_INFERENCIA_LOCAL.md` - Inferência local

## 🎓 Desenvolvido por

- **Alunos**: Marcelo V Duarte Colpani, Nicolas Souza, Rubens Jose Collin, Tiago Dias Borges
- **Orientador**: Prof. Dr. Anderson Henrique Rodrigues Ferreira
- **Instituição**: CEUNSP - Centro Universitário Nossa Senhora do Patrocínio

---

**Versão**: 1.0.0
**Última atualização**: 2026-01-16
**Compatível com**: AWS Lambda, API Gateway, S3, CloudFront, ECR
