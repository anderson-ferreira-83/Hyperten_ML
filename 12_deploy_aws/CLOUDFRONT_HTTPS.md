# CloudFront HTTPS - Configuração e Documentação

## Resumo

Configuração do Amazon CloudFront para fornecer acesso HTTPS seguro à interface web da aplicação de predição de hipertensão.

## Problema Resolvido

- Navegadores modernos (Chrome, Safari, Firefox) marcam páginas HTTP como "não seguras"
- Dispositivos móveis bloqueiam ou alertam sobre conexões HTTP
- A interface web no S3 só suportava HTTP nativamente

## Solução Implementada

```
┌─────────────┐    HTTPS     ┌─────────────┐    HTTP      ┌─────────────┐
│   Usuário   │ ──────────►  │  CloudFront │ ──────────►  │  S3 Bucket  │
│  (Celular)  │              │   (CDN)     │              │  (Website)  │
└─────────────┘              └─────────────┘              └─────────────┘
```

## URLs Ativas

### Interface Web (HTTPS) - Nova URL Segura
```
https://dl52cpaeesvk0.cloudfront.net/ui/index.html
```

### API de Predição (HTTPS)
```
https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/predict
```

### Health Check (HTTPS)
```
https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health
```

## Recursos AWS Criados

| Recurso | ID/Nome | Região |
|---------|---------|--------|
| CloudFront Distribution | E390ZKBDLPPSSU | Global (Edge Locations) |
| Domain Name | dl52cpaeesvk0.cloudfront.net | - |
| Origin | S3 Website | sa-east-1 |
| Certificado SSL | CloudFront Default | Automático |

## Configuração Técnica

### CloudFront Distribution Config

```json
{
    "Id": "E390ZKBDLPPSSU",
    "DomainName": "dl52cpaeesvk0.cloudfront.net",
    "Origin": "hypertension-tcc-ceunsp-2026.s3-website-sa-east-1.amazonaws.com",
    "ViewerProtocolPolicy": "redirect-to-https",
    "PriceClass": "PriceClass_100",
    "HttpVersion": "http2",
    "Compress": true,
    "DefaultRootObject": "index.html"
}
```

### Detalhes da Configuração

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| ViewerProtocolPolicy | redirect-to-https | Redireciona HTTP para HTTPS automaticamente |
| PriceClass | PriceClass_100 | Edge locations na América do Norte e Europa (menor custo) |
| Compress | true | Compressão gzip/brotli automática |
| Cache Policy | CachingOptimized | Cache otimizado para conteúdo estático |
| HTTP Version | HTTP/2 | Protocolo moderno para melhor performance |

## Custo Estimado

| Componente | Custo |
|------------|-------|
| CloudFront (primeiros 1TB/mês) | Grátis (Free Tier - 12 meses) |
| CloudFront (após Free Tier) | ~$0.085/GB |
| Certificado SSL | Grátis (incluso no CloudFront) |
| **Total estimado** | **$0.00 - $1.00/mês** (uso leve) |

## Comandos Úteis

### Verificar Status da Distribuição
```bash
aws cloudfront get-distribution --id E390ZKBDLPPSSU --query 'Distribution.Status'
```

### Invalidar Cache (forçar atualização)
```bash
aws cloudfront create-invalidation --distribution-id E390ZKBDLPPSSU --paths "/*"
```

### Listar Distribuições
```bash
aws cloudfront list-distributions --query 'DistributionList.Items[*].[Id,DomainName,Status]' --output table
```

## Testando a Aplicação

### Via Navegador
Acesse: https://dl52cpaeesvk0.cloudfront.net/ui/index.html

### Via cURL
```bash
# Testar interface web
curl -I https://dl52cpaeesvk0.cloudfront.net/ui/index.html

# Testar API
curl https://yrac79mzj9.execute-api.sa-east-1.amazonaws.com/health
```

### Via Script
```bash
cd 12_deploy_aws
./run_all_tests.sh
```

## Vantagens do CloudFront

1. **HTTPS Automático**: Certificado SSL gratuito incluído
2. **Performance**: CDN global com cache nas edge locations
3. **Compressão**: Reduz tamanho dos arquivos automaticamente
4. **DDoS Protection**: AWS Shield Standard incluído
5. **HTTP/2**: Protocolo moderno para carregamento mais rápido

## Troubleshooting

### Página não atualiza após mudanças no S3
Execute invalidação de cache:
```bash
aws cloudfront create-invalidation --distribution-id E390ZKBDLPPSSU --paths "/*"
```

### Erro 403 Forbidden
Verifique se o bucket S3 está configurado como website público.

### Certificado inválido
O CloudFront usa certificado padrão `*.cloudfront.net`. Se precisar de domínio próprio, configure ACM.

## Histórico

| Data | Ação |
|------|------|
| 2026-01-17 | Criação da distribuição CloudFront |
| 2026-01-17 | Deploy concluído e testado |

---

**Criado em**: 2026-01-17
**Última atualização**: 2026-01-17
