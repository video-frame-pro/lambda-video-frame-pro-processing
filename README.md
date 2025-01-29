<p align="center">
  <img src="https://i.ibb.co/zs1zcs3/Video-Frame.png" width="30%" />
</p>

---

Este repositório contém a implementação da **lógica de processamento dos frames** do sistema **Video Frame Pro**, responsável por pegar o video no bucket S3 e gerar frames a partir do mesmo.

---

## Função

A função Lambda gera frames baseados no número de frame rate e compacta em um zip, exemplo:
Caso o video tenha 22 segundos será gerado 2 frames, o primeiro no 10° segundo e o outro no 20° segundo.

---

## Campos da Requisição

A função Lambda espera um evento com os seguintes campos:

- **video_url** (obrigatório): Endereço do video no bucket S3.
- **user_name** (obrigatório) nome do usuário solicitante.
- **email** (obrigatório): Email no qual será enviado os frames.
- **frame_rate** (obrigatório): Intervalo de tempo em segundo entre cada frame.

---

## Exemplos de Entrada

```json
{
   "body": {
      "video_url": "video_exemplo.mp4",
      "user_name": "usuario",
      "email": "usuario@email.com",
      "frame_rate": 10
   }
}
```
---

## Exemplos de Resposta

### Sucesso

```json
{
   "body": {
      "email": "usuario@email.com",
      "frame_url": "https://example.com/download.zip",
      "error": false
   }
}
```

### Erro

```json
{
   "body": {
      "email": "usuario@email.com",
      "error": true
   }
}
```

---

## Tecnologias

<p>
  <img src="https://img.shields.io/badge/AWS-232F3E?logo=amazonaws&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/AWS_Lambda-4B5A2F?logo=aws-lambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FFMPEG-007DB8?logoColor=white" alt="FFMPEG" />
  <img src="https://img.shields.io/badge/GitHub-ACTION-2088FF?logo=github-actions&logoColor=white" alt="GitHub Actions" />
</p>

---

## Estrutura do Repositório

```
/src
├── processing
│   ├── processing.py             # Lógica de geração de frames
│   ├── requirements.txt          # Dependências do Python
│   ├── __init__.py               # Inicialização do pacote
/tests
├── processing
│   ├── processing_test.py        # Testes unitários para a função de geração de frames
│   ├── requirements.txt          # Dependências do Python para testes
│   ├── __init__.py               # Inicialização do pacote para testes
/infra
├── main.tf                       # Definição dos recursos AWS com Terraform
├── outputs.tf                    # Outputs das funções e recursos Terraform
├── variables.tf                  # Definições de variáveis Terraform
├── terraform.tfvars              # Arquivo com variáveis de ambiente
```

---

## Passos para Configuração

### Pré-Requisitos

1. Configure as credenciais da AWS.

### Deploy da Infraestrutura

1. No diretório `infra`, configure o arquivo `terraform.tfvars`.
2. Execute o Terraform:

```bash
cd infra
terraform init
terraform apply -auto-approve
```

---

### Testes Unitários

1. Rode o bloco para instalar as dependências de testes, executar os testes e gerar o relatório de cobertura:

```sh
find tests -name 'requirements.txt' -exec pip install -r {} +
pip install coverage coverage-badge
coverage run -m unittest discover -s tests -p '*_test.py'
coverage report -m
coverage html  
```

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo LICENSE para mais detalhes.

---

Desenvolvido com ❤️ pela equipe Video Frame Pro.