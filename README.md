# Pequeno Rebanho

Sistema de gestão de salas, professores, equipes e escalas para ministério infantil.

## Visão geral

Este projeto reúne:
- backend em FastAPI
- banco PostgreSQL via Supabase
- frontend em HTML, CSS e JavaScript
- autenticação por JWT
- gestão de salas, equipes, professores e escalas mensais
- layout responsivo para desktop e mobile

## Status atual do projeto

O sistema já está estruturado e funcional em sua base, com:
- autenticação de usuários
- CRUD de salas, professores, equipes e escalas
- geração mensal de escala por sala
- painel administrativo
- interface responsiva

O que ainda precisa ser validado antes da entrega final:
- revisão completa de dados reais no Supabase
- testes de fluxo completos em produção/local
- revisão final de permissões e regras de negócio
- ajuste de alguns fluxos de UI conforme uso real

## Stack

- Python 3.11+
- FastAPI
- Supabase / PostgreSQL
- Pydantic + Pydantic Settings
- JWT (python-jose)
- passlib + bcrypt
- HTML/CSS/JavaScript vanilla

## Requisitos

- Python 3.11 ou superior
- pip
- conta no Supabase
- acesso ao GitHub

## Instalação local

1. Clone o repositório.
2. Crie o ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Copie o arquivo de exemplo:
   ```bash
   copy .env.example .env
   ```
5. Ajuste as variáveis no `.env` conforme o projeto Supabase.

## Variáveis de ambiente

Exemplo em `.env.example`:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-service-role-key
JWT_SECRET=troque-esta-chave-por-uma-forte
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

Importante:
- nunca commite o arquivo `.env`
- use uma JWT_SECRET forte e diferente para cada ambiente
- no deploy real, configure as variáveis em ambiente do provedor e não no repositório

## Banco de dados

1. Crie um projeto no Supabase
2. Execute o conteúdo de `schema.sql` no SQL Editor
3. Verifique se as tabelas e campos esperados existem

## Execução local

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Acesso:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/login
- http://127.0.0.1:8000/app

## Segurança aplicada

Este projeto foi preparado para reduzir risco antes do push para GitHub:
- `.gitignore` configurado para ignorar segredos, ambiente virtual e caches
- variáveis sensíveis em `.env` fora do controle de versão
- validação de `jwt_secret` e `supabase_url` / `supabase_key`
- CORS com lista explícita
- rate limiting simples por IP
- senha normalizada e protegida com bcrypt
- token JWT validado com algoritmos e expiração

## Estrutura do projeto

```text
.
├── backend/
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── security.py
│   ├── routers/
│   └── schemas/
├── static/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── schema.sql
└── .env
```

## Próximo passo recomendado

Antes de subir ao GitHub, faça:
1. confirmar se `.env` está no `.gitignore`
2. validar que o projeto inicia sem erro localmente
3. testar os fluxos principais em navegador
4. criar o repositório no GitHub
5. subir o projeto com commit inicial

## Observação final

Este projeto está em uma etapa funcional, mas ainda não está finalizado como entrega comercial. O estado atual é de desenvolvimento em andamento, com a base pronta e a interface principal implementada.
