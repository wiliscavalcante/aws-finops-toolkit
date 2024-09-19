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

def apply_multipart_upload_rule(bucket_name, days=7):
    """Aplica ou atualiza a regra de ciclo de vida para deletar uploads incompletos após X dias."""
    rules = get_bucket_lifecycle(bucket_name)
    
    # Verifica se já há uma regra para multipart uploads
    rule_found = False
    for rule in rules:
        if rule.get('ID') == 'MultipartUploadRule':
            rule_found = True
            # Se a regra existe, atualiza se necessário
            if rule.get('AbortIncompleteMultipartUpload', {}).get('DaysAfterInitiation') != days:
                rule['AbortIncompleteMultipartUpload']['DaysAfterInitiation'] = days
                print(f"Atualizando regra de multipart upload para {days} dias no bucket {bucket_name}.")
            else:
                print(f"Regra de multipart upload já configurada corretamente para {days} dias no bucket {bucket_name}.")
    
    if not rule_found:
        # Adiciona a regra para excluir uploads incompletos após X dias
        new_rule = {
            'ID': 'MultipartUploadRule',
            'Status': 'Enabled',
            'Filter': {'Prefix': ''},
            'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': days}
        }
        rules.append(new_rule)
        print(f"Adicionando regra de multipart upload para {days} dias no bucket {bucket_name}.")
    
    # Aplica as regras de ciclo de vida (adicionadas ou atualizadas)
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={'Rules': rules}
    )
    print(f"Regras de ciclo de vida aplicadas no bucket {bucket_name}.")

def apply_intelligent_tiering(bucket_name, days=30):
    """Aplica ou atualiza a regra para mover objetos para o Intelligent-Tiering após X dias."""
    rules = get_bucket_lifecycle(bucket_name)

    # Verifica se já há uma regra para Intelligent-Tiering
    rule_found = False
    for rule in rules:
        if rule.get('ID') == 'IntelligentTieringRule':
            rule_found = True
            # Se a regra existe, atualiza se necessário
            if rule.get('Transitions', [{}])[0].get('Days') != days:
                rule['Transitions'][0]['Days'] = days
                print(f"Atualizando regra de Intelligent-Tiering para {days} dias no bucket {bucket_name}.")
            else:
                print(f"Regra de Intelligent-Tiering já configurada corretamente para {days} dias no bucket {bucket_name}.")
    
    if not rule_found:
        # Adiciona a regra para mover objetos para Intelligent-Tiering após X dias
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
        print(f"Adicionando regra de Intelligent-Tiering para {days} dias no bucket {bucket_name}.")

    # Aplica as regras de ciclo de vida (adicionadas ou atualizadas)
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={'Rules': rules}
    )
    print(f"Regras de Intelligent-Tiering aplicadas no bucket {bucket_name}.")

def lambda_handler(event, context):
    """Função Lambda para aplicar regras de ciclo de vida e Intelligent-Tiering."""
    buckets = list_buckets()

    for bucket in buckets:
        print(f"Verificando bucket: {bucket}")
        apply_multipart_upload_rule(bucket, days=7)
        apply_intelligent_tiering(bucket, days=30)

    return {
        'statusCode': 200,
        'body': json.dumps(f"Regras aplicadas em {len(buckets)} buckets.")
    }

# Se você estiver rodando localmente, use isso para executar o script
if __name__ == "__main__":
    buckets = list_buckets()
    for bucket in buckets:
        print(f"Verificando bucket: {bucket}")
        apply_multipart_upload_rule(bucket, days=7)
        apply_intelligent_tiering(bucket, days=30)
