<p align="center">
  <img src="https://i.ibb.co/zs1zcs3/Video-Frame.png" width="30%" />
</p>

---

# Video Frame Pro - Processamento de Frames

Este repositório contém a implementação da **lógica de processamento dos frames** do sistema **Video Frame Pro**, responsável por processar vídeos armazenados no S3 e gerar frames conforme um intervalo de tempo definido.

---

## 📌 Objetivo

A função Lambda deste repositório executa as seguintes tarefas:

1. **Baixa o vídeo do S3** com base no `video_id` do usuário.
2. **Extrai frames** do vídeo conforme o `frame_rate` definido.
3. **Compacta os frames em um ZIP** e armazena no S3.
4. **Gera uma URL pré-assinada** para o usuário fazer o download do ZIP.
5. **Remove arquivos temporários** da execução.

Caso o vídeo tenha 22 segundos e o `frame_rate` seja `10`, serão gerados **2 frames**:
- 1º frame no 10º segundo
- 2º frame no 20º segundo

---

## 📂 Estrutura do Repositório

```
/src
├── processing
│   ├── processing.py             # Lógica principal de processamento
│   ├── requirements.txt          # Dependências da Lambda
│   ├── __init__.py               # Inicialização do módulo
/tests
├── processing
│   ├── processing_test.py        # Testes unitários
│   ├── __init__.py               # Inicialização do módulo de testes
/infra
├── main.tf                       # Infraestrutura AWS (Lambda, S3, IAM, etc.)
├── outputs.tf                    # Definição dos outputs Terraform
├── variables.tf                  # Variáveis de configuração Terraform
├── terraform.tfvars              # Arquivo com valores das variáveis Terraform
```

---

## 🔹 Campos da Requisição

A função Lambda espera um **JSON** com os seguintes campos obrigatórios:

| Campo       | Tipo   | Descrição |
|-------------|--------|-----------|
| `video_id`  | String | Identificador único do vídeo no S3 |
| `user_name` | String | Nome do usuário solicitante |
| `email`     | String | Email para onde será enviado o link do ZIP |
| `frame_rate`| Int    | Intervalo de tempo entre cada frame (segundos) |

### 📥 Exemplo de Entrada

```json
{
   "body": {
        "user_name": "usuario",
        "email": "usuario@email.com",
        "video_id": "uuid", 
        "frame_rate": 10
   }
}
```

### 📤 Exemplo de Resposta - Sucesso

```json
{
   "statusCode": 200,
   "body": {
      "email": "usuario@email.com",
      "frame_url": "https://s3.amazonaws.com/video-frame-pro/output.zip"
   }
}
```

### ❌ Exemplo de Resposta - Erro

```json
{
   "statusCode": 400,
   "body": {
      "message": "Missing required fields: video_id, user_name, email, frame_rate"
   }
}
```

---

## 🚀 Configuração e Deploy

### 1️⃣ Pré-requisitos

1. **AWS CLI** configurado (`aws configure`)
2. **Terraform** instalado (`terraform -v`)
3. Permissões para criar **Lambda Functions**, **S3 Buckets** e **IAM Roles**

### 2️⃣ Deploy da Infraestrutura

1. Navegue até o diretório `infra` e inicialize o Terraform:

```sh
cd infra
terraform init
terraform apply -auto-approve
```

### 3️⃣ Executando Testes Unitários

Execute os testes e gere o relatório de cobertura:

```sh
find tests -name 'requirements.txt' -exec pip install -r {} +
pip install coverage coverage-badge
coverage run -m unittest discover -s tests -p '*_test.py'
coverage report -m
coverage html  
```

---

## 🛠 Tecnologias Utilizadas

<p>
  <img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/AWS_Lambda-4B5A2F?logo=aws-lambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FFMPEG-007DB8?logoColor=white" alt="FFMPEG" />
  <img src="https://img.shields.io/badge/GitHub-ACTION-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions" />
</p>

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo LICENSE para mais detalhes.

---

Desenvolvido com ❤️ pela equipe **Video Frame Pro**.
