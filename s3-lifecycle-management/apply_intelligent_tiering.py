import boto3
import json
from botocore.exceptions import ClientError

# Inicializando o cliente S3
s3 = boto3.client('s3')

def list_buckets():
    """Lista todos os buckets na conta."""
    response = s3.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]

def get_bucket_lifecycle(bucket_name):
    """Verifica se um bucket já tem regras de ciclo de vida configuradas."""
    try:
        response = s3.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return response.get('Rules', [])
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchLifecycleConfiguration':
            return []
        else:
            print(f"Erro ao obter configuração de ciclo de vida do bucket {bucket_name}: {e}")
            raise

def apply_intelligent_tiering(bucket_name, days=30):
    """Aplica a regra de ciclo de vida para mover objetos para Intelligent-Tiering após um número de dias."""
    rules = get_bucket_lifecycle(bucket_name)

    # Verifica se já há uma regra para Intelligent-Tiering
    if any(rule.get('ID') == 'IntelligentTieringRule' for rule in rules):
        print(f"Regra de Intelligent-Tiering já aplicada no bucket {bucket_name}.")
        return

    # Adiciona a regra para mover os objetos para Intelligent-Tiering após 'days' dias
    new_rule = {
        'ID': 'IntelligentTieringRule',
        'Status': 'Enabled',
        'Filter': {'Prefix': ''},
        'Transitions': [{
            'Days': days,
            'StorageClass': 'INTELLIGENT_TIERING'
        }]
    }
    rules.append(new_rule)

    # Aplica as novas regras de ciclo de vida
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={'Rules': rules}
    )
    print(f"Regra de Intelligent-Tiering aplicada no bucket {bucket_name}.")

def lambda_handler(event, context):
    """Função Lambda para aplicar regras de Intelligent-Tiering."""
    days = int(event.get('days', 30))  # Permite flexibilidade no número de dias via evento Lambda
    buckets = list_buckets()

    for bucket in buckets:
        print(f"Verificando bucket: {bucket}")
        apply_intelligent_tiering(bucket, days=days)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Regras aplicadas em {len(buckets)} buckets.")
    }

# Se você estiver rodando localmente, use isso para executar o script
if __name__ == "__main__":
    days = 30  # Defina o número de dias desejado para mover objetos para Intelligent-Tiering
    buckets = list_buckets()
    for bucket in buckets:
        print(f"Verificando bucket: {bucket}")
        apply_intelligent_tiering(bucket, days=days)
