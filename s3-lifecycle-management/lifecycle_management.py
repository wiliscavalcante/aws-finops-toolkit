import boto3
import json

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
    except s3.exceptions.NoSuchLifecycleConfiguration:
        return []

def apply_multipart_upload_rule(bucket_name):
    """Aplica a regra de ciclo de vida para deletar uploads incompletos após 7 dias."""
    rules = get_bucket_lifecycle(bucket_name)
    
    # Verifica se já há uma regra para multipart uploads
    if any(rule.get('ID') == 'MultipartUploadRule' for rule in rules):
        print(f"Regra de multipart upload já aplicada no bucket {bucket_name}.")
        return

    # Adiciona a regra para excluir uploads incompletos após 7 dias
    new_rule = {
        'ID': 'MultipartUploadRule',
        'Status': 'Enabled',
        'Filter': {'Prefix': ''},
        'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 7}
    }
    rules.append(new_rule)

    # Aplica as novas regras de ciclo de vida
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={'Rules': rules}
    )
    print(f"Regra de multipart upload aplicada no bucket {bucket_name}.")

def apply_intelligent_tiering(bucket_name):
    """Aplica a regra para mover os objetos para o Intelligent-Tiering."""
    rules = get_bucket_lifecycle(bucket_name)

    # Verifica se já há uma regra para Intelligent-Tiering
    if any(rule.get('ID') == 'IntelligentTieringRule' for rule in rules):
        print(f"Regra de Intelligent-Tiering já aplicada no bucket {bucket_name}.")
        return

    # Adiciona a regra para mover os objetos para Intelligent-Tiering
    new_rule = {
        'ID': 'IntelligentTieringRule',
        'Status': 'Enabled',
        'Filter': {'Prefix': ''},
        'Transitions': [{
            'Days': 30,
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
    """Função Lambda para aplicar regras de ciclo de vida e Intelligent-Tiering."""
    buckets = list_buckets()

    for bucket in buckets:
        print(f"Verificando bucket: {bucket}")
        apply_multipart_upload_rule(bucket)
        apply_intelligent_tiering(bucket)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Regras aplicadas em {len(buckets)} buckets.")
    }

# Se você estiver rodando localmente, use isso para executar o script
if __name__ == "__main__":
    buckets = list_buckets()
    for bucket in buckets:
        print(f"Verificando bucket: {bucket}")
        apply_multipart_upload_rule(bucket)
        apply_intelligent_tiering(bucket)
