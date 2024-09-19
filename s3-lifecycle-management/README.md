---

# S3 Lifecycle Management

Este script faz parte da ferramenta **AWS FinOps Toolkit** e foi criado para gerenciar automaticamente regras de ciclo de vida e otimização de armazenamento nos buckets do Amazon S3. Ele garante que todas as regras necessárias estejam configuradas e que novos buckets recebam a configuração correta de ciclo de vida e Intelligent-Tiering para controle de custos.

## Funcionalidades

1. **Multipart Upload Cleanup**: Remove uploads de várias partes incompletos que permanecem pendentes por mais de 7 dias.
2. **Intelligent-Tiering**: Aplica a regra de ciclo de vida para mover os objetos do bucket para o **Intelligent-Tiering** após 30 dias.
3. **Idempotente**: O script pode ser executado várias vezes sem causar conflitos, verificando primeiro se as regras já estão configuradas antes de aplicá-las.

## Pré-requisitos

- Python 3.x
- Biblioteca `boto3` instalada
- Credenciais AWS configuradas (via AWS CLI ou ambiente Lambda)
  
Você pode instalar as dependências executando:

```bash
pip install -r requirements.txt
```

## Execução Local

1. Clone o repositório ou copie o conteúdo do subdiretório `s3-lifecycle-management`.
2. Execute o script manualmente para gerenciar todos os buckets S3 da conta AWS configurada:

```bash
python lifecycle_management.py
```

O script irá:
- Listar todos os buckets S3.
- Verificar se as regras de ciclo de vida estão presentes.
- Aplicar as regras para **multipart upload** e **Intelligent-Tiering**, se necessário.


## Personalizações

- **Dias de retenção para uploads incompletos**: A regra de multipart upload pode ser personalizada para excluir uploads incompletos após um período diferente de 7 dias.
- **Dias para mover objetos para Intelligent-Tiering**: Atualmente, a regra move objetos para o Intelligent-Tiering após 30 dias, mas você pode ajustar o número de dias conforme necessário.

## Considerações Finais

- **Intelligent-Tiering**: O uso do **Intelligent-Tiering** é recomendado para cenários onde o padrão de acesso aos objetos pode variar. Ele monitora automaticamente o acesso e move os objetos entre as camadas de armazenamento de acordo com a frequência de acesso.
- **Custo de Monitoramento**: O Intelligent-Tiering pode adicionar um pequeno custo de monitoramento por objeto, então é importante avaliar se ele oferece economia em relação aos outros tipos de armazenamento, com base no volume e padrão de acesso.

## Contribuições

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou sugestões!

---
