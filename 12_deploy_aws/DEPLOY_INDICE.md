# 📑 Índice de Arquivos de Deploy

Este documento lista todos os arquivos criados para facilitar o deploy da aplicação na AWS.

## 🎯 Por onde começar?

### Se você quer fazer o deploy AGORA
👉 **Comece aqui**: [DEPLOY_RESUMO.md](DEPLOY_RESUMO.md)

### Se você quer entender tudo antes
👉 **Leia primeiro**: [GUIA_DEPLOY_RAPIDO.md](GUIA_DEPLOY_RAPIDO.md)

## 📚 Arquivos disponíveis

### 1. Documentação

| Arquivo | Descrição | Quando usar |
|---------|-----------|-------------|
| **DEPLOY_RESUMO.md** | Resumo executivo (5 passos) | Início rápido, sem detalhes |
| **GUIA_DEPLOY_RAPIDO.md** | Guia completo passo a passo | Tutorial detalhado com explicações |
| **CHECKLIST_DEPLOY.md** | Checklist de validação | Durante o deploy para não esquecer nada |
| **DEPLOY_INDICE.md** | Este arquivo - índice de tudo | Navegação e referência |

### 2. Scripts e Automação

| Arquivo | Descrição | Como usar |
|---------|-----------|-----------|
| **deploy_aws.sh** | Script automatizado de deploy | `./deploy_aws.sh` |
| **test_local.sh** | Testa a aplicação localmente | `./test_local.sh` (antes do deploy) |
| **deploy_config.example.sh** | Template de configuração | Copiar para `deploy_config.sh` e editar |

### 3. Configuração Docker

| Arquivo | Descrição | Propósito |
|---------|-----------|-----------|
| **Dockerfile** | Imagem Docker otimizada | Build da imagem para Lambda |
| **.dockerignore** | Arquivos excluídos do build | Otimiza tamanho da imagem |

### 4. Documentação Técnica Existente

| Arquivo | Descrição |
|---------|-----------|
| `04_reports/docs/DEPLOY_AWS.md` | Documentação técnica detalhada (já existia) |
| `04_reports/docs/PASSO_API_GATEWAY.md` | Configuração API Gateway (já existia) |
| `04_reports/docs/TUTORIAL_INFERENCIA_LOCAL.md` | Como rodar localmente |

## 🗺️ Fluxo de Deploy Recomendado

```
1. DEPLOY_RESUMO.md
   ↓
2. test_local.sh (validar localmente)
   ↓
3. cp deploy_config.example.sh deploy_config.sh
   ↓
4. nano deploy_config.sh (configurar)
   ↓
5. deploy_aws.sh (executar deploy)
   ↓
6. CHECKLIST_DEPLOY.md (validar tudo)
   ↓
7. GUIA_DEPLOY_RAPIDO.md (resolver problemas)
```

## 📝 Fluxos por Perfil de Usuário

### Perfil 1: "Quero fazer rápido, já conheço AWS"
1. Leia: `DEPLOY_RESUMO.md` (5 min)
2. Configure: `deploy_config.sh`
3. Execute: `./deploy_aws.sh`
4. Valide: `CHECKLIST_DEPLOY.md`

**Tempo estimado**: 20-30 minutos

### Perfil 2: "Primeira vez com AWS, preciso de ajuda"
1. Leia: `GUIA_DEPLOY_RAPIDO.md` (20 min)
2. Teste local: `./test_local.sh`
3. Configure: `deploy_config.sh`
4. Execute: `./deploy_aws.sh`
5. Acompanhe: `CHECKLIST_DEPLOY.md` durante todo o processo

**Tempo estimado**: 60-90 minutos

### Perfil 3: "Quero entender tudo tecnicamente"
1. Leia: `04_reports/docs/DEPLOY_AWS.md`
2. Leia: `GUIA_DEPLOY_RAPIDO.md`
3. Revise: `Dockerfile` e `deploy_aws.sh`
4. Teste local: `./test_local.sh`
5. Execute: Deploy manual ou `./deploy_aws.sh`
6. Valide: `CHECKLIST_DEPLOY.md`

**Tempo estimado**: 2-3 horas

## 🎓 Estrutura de Aprendizado

### Nível 1: Iniciante
- **DEPLOY_RESUMO.md**: Resumo visual e direto
- **CHECKLIST_DEPLOY.md**: Lista de tarefas simples

### Nível 2: Intermediário
- **GUIA_DEPLOY_RAPIDO.md**: Tutorial completo
- **deploy_aws.sh**: Automação com menu interativo

### Nível 3: Avançado
- **04_reports/docs/DEPLOY_AWS.md**: Detalhes técnicos
- **Dockerfile**: Customização de imagem
- **deploy_aws.sh**: Código do script (modificável)

## 🔧 Troubleshooting

### Problema com deploy?
1. Consulte seção "Solução de Problemas" em `GUIA_DEPLOY_RAPIDO.md`
2. Verifique `CHECKLIST_DEPLOY.md` - algum passo foi pulado?
3. Teste localmente primeiro: `./test_local.sh`

### Erro específico?
| Erro | Onde encontrar solução |
|------|------------------------|
| Docker | `GUIA_DEPLOY_RAPIDO.md` - seção "Troubleshooting" |
| CORS | `GUIA_DEPLOY_RAPIDO.md` - Passo 6 (Habilitar CORS) |
| Lambda timeout | `CHECKLIST_DEPLOY.md` - seção "Comandos Úteis" |
| Artefatos não encontrados | `test_local.sh` - valida artefatos localmente |

## 📊 Comparação dos Guias

| Característica | DEPLOY_RESUMO | GUIA_DEPLOY_RAPIDO | CHECKLIST_DEPLOY |
|----------------|---------------|-------------------|------------------|
| Páginas | 1 | 10+ | 2 |
| Tempo leitura | 3 min | 20 min | 5 min |
| Detalhamento | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Screenshots | Não | Não | Não |
| Código | ✅ Mínimo | ✅ Completo | ✅ Útil |
| Explicações | ❌ | ✅ | ❌ |
| Checklist | ❌ | ❌ | ✅ |
| **Melhor para** | Início rápido | Aprendizado | Validação |

## 🌟 Dica Final

**Nunca fez deploy na AWS antes?**
1. Abra `GUIA_DEPLOY_RAPIDO.md`
2. Abra `CHECKLIST_DEPLOY.md` em outra janela
3. Siga o guia marcando os itens no checklist
4. Se travar, consulte a seção troubleshooting do guia

**Já é experiente com AWS?**
1. Abra `DEPLOY_RESUMO.md`
2. Configure `deploy_config.sh`
3. Execute `./deploy_aws.sh`
4. Done! ✅

---

**Criado para facilitar seu TCC! 🎓**

**Desenvolvido por**: Marcelo V Duarte Colpani, Nicolas Souza, Rubens Jose Collin, Tiago Dias Borges
**Orientador**: Prof. Dr. Anderson Henrique Rodrigues Ferreira
