# ASCII://DIARIO

Um blog minimalista rodando no terminal, onde posts são criados e visualizados usando comandos estilo CLI e arte ASCII. Desenvolvido em Python com Flask e MongoDB.

Acesse o blog -> [clicando aqui](https://asciidiario.onrender.com/)

![ASCII Art Preview](/static/ascii_diario.png)

## Funcionalidades

- Interface 100% terminal interativa
- Sistema de autenticação para admin
- Comandos:
  - `/help` - Lista todos os comandos
  - `/list` - Mostra posts recentes
  - `/view <id>` - Exibe post completo
  - `/login <senha>` - Acesso admin
  - `/newpost` - Cria novo post (admin)
  - `/sobre` - Informações do autor
- Suporte a:
  - Tags de conteúdo
  - Tipos de post (diário, projeto, reflexão)
  - Blocos ASCII art entre ``` ```
  - Histórico de comandos

## Como Executar

### Pré-requisitos
- Python 3.11+
- MongoDB
- Flask

### Instalação
1. Clone o repositório:
    ```bash
    git clone https://github.com/Mogutaa/ascii-diario.git
    cd ascii-diario

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt

3. Crie o arquivo .env:
    ```bash
    SECRET_KEY=sua_chave_secreta
    MONGO_URI=sua_chave_secreta
    DATABASE_NAME=seu_db
    ADMIN_HASH=hash_bcrypt_da_senha_admin

4. Execute:
    ```bash
    python app.py

## Estrutura do Projeto
```ruby
├── app.py          # Aplicação principal
├── admin.py        # Rotas administrativas
├── auth.py         # Sistema de login
├── config.py       # Configurações
├── templates/      # Templates HTML
│   └── terminal.html
├── static/
|   ├── favicon.ico 
|   └── css/        # Estilização do Terminal
|       └── styles.css 
└── .env            # Variáveis de ambiente


## Exemplos de Uso

1. Login como admin:
    ```bash
    /login senha_secreta

2. Criar novo post:
    ```bash
    /newpost
    /title Meu Primeiro Post
    /tags python,blog
    Digite o conteúdo...
    /salvar

3. Visualizar posts:
    ```bash
    /list
    /view 5f3a7b


## Dependências Principais
- Flask - Framework web
- PyMongo - Conexão com MongoDB
- bcrypt - Criptografia de senhas
- python-dotenv - Gerenciamento de variáveis de ambiente

## Contribuição
Contribuições são bem-vindas! Siga estes passos:
1. Faça um fork do projeto
2. Crie sua branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença
Distribuído sob licença MIT. Veja `LICENSE` para mais informações.

---

**Desenvolvido por Alan José**  
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github)](https://github.com/Mogutaa)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/alan-jose-filho/)
