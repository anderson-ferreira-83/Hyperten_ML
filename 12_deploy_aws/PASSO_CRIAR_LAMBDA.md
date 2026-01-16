# 🚀 Guia Rápido: Criar Lambda Manualmente

## ✅ O Que Já Está Pronto
- ✅ Imagem Docker no ECR: `710586046477.dkr.ecr.sa-east-1.amazonaws.com/hypertension-api:latest`
- ✅ Role IAM criada: `hypertension-lambda-execution-role`

## 📝 Passos para Criar a Lambda (3 minutos)

### Passo 1: Acessar Console Lambda
1. Abra: https://sa-east-1.console.aws.amazon.com/lambda/home?region=sa-east-1#/create/function
2. Ou navegue: **AWS Console → Lambda → Create function**

### Passo 2: Configurar Função
Na tela "Create function":

**Opção 1: Container image** (selecione esta)

**Basic information**:
- Function name: `hypertension-api`
- Container image URI: `710586046477.dkr.ecr.sa-east-1.amazonaws.com/hypertension-api:latest`

  💡 Clique em **"Browse images"** para:
  - Selecionar: `hypertension-api`
  - Selecionar tag: `latest`
  - Confirmar

**Permissions**:
- Execution role: **"Use an existing role"**
- Existing role: `hypertension-lambda-execution-role`

### Passo 3: Criar
Clique no botão **"Create function"** (canto inferior direito)

⏳ Aguarde alguns segundos até aparecer: "Successfully created the function hypertension-api"

### Passo 4: Configurar Memória e Timeout
Agora na página da função criada:

1. Vá na aba **"Configuration"** (menu superior)
2. No menu lateral esquerdo, clique em **"General configuration"**
3. Clique em **"Edit"** (canto superior direito)
4. Ajuste:
   - **Memory**: `1024` MB
   - **Timeout**: `0` min `30` sec
5. Clique em **"Save"**

### Passo 5: Testar (Opcional)
1. Volte para a aba **"Test"**
2. Clique em **"Test"**
3. Crie um teste básico (pode deixar o JSON padrão)
4. Execute

**Possíveis resultados**:
- ✅ Se funcionar: Ótimo!
- ⚠️ Se der erro: Normal, vamos ajustar depois com o API Gateway

---

## ✅ Pronto!
Quando terminar, me avise que vou continuar com:
- Criar API Gateway
- Conectar Lambda ao API Gateway
- Deploy da UI no S3
- Configurar CloudFront

---

## 🆘 Problemas?

### "Container image not found"
- Verifique se está na região `sa-east-1`
- Verifique se o URI está correto

### "Execution role does not exist"
- Selecione "Create a new role with basic Lambda permissions"
- Anote o nome da role criada

### "Timeout"
- Aumente para 60 segundos
- Aumente memória para 1536 MB

---

**Criado? Me avise para continuar! 🚀**
