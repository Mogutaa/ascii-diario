from flask import Flask, render_template, request, session, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
from config import Config
import bcrypt
import datetime
import re

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Database setup
client = MongoClient(app.config['MONGO_URI'])
db = client[app.config['DATABASE_NAME']]
posts_collection = db.posts

def init_session():
    session.setdefault('history', [])
    session.setdefault('admin', False)
    session.setdefault('editing', False)
    session.setdefault('post_data', {})

@app.route('/', methods=['GET'])
def terminal():
    init_session()
    return render_template('terminal.html')

@app.route('/command', methods=['POST'])
def handle_command():
    init_session()
    command = request.form['command'].strip()
    
    if command.lower() == '/clear':
        session['history'] = []
        return redirect(url_for('terminal'))
    
    output = process_command(command)
    session['history'] = session['history'] + [{'command': command, 'output': output}]
    
    return redirect(url_for('terminal'))

def process_command(command):
    if not command:
        return ""
    
    command_lower = command.lower()
    
    if command_lower == '/help':
        return help_text()
    
    if command_lower == '/sobre':
        return render_about()
    
    if command_lower.startswith('/login'):
        return handle_login(command)
    
    if command_lower == '/logout':
        return handle_logout()
    
    if command_lower == '/list':
        return list_posts()
    
    if command_lower.startswith('/view'):
        return view_post(command)
    
    if session.get('admin'):
        return process_admin_commands(command)
    
    return "Comando inválido. Digite /help para ajuda."

def handle_login(command):
    try:
        _, password = command.split(' ', 1)
        if bcrypt.checkpw(password.encode('utf-8'), app.config['ADMIN_HASH']):
            session['admin'] = True
            return "Login realizado com sucesso!"
        return "Senha incorreta!"
    except:
        return "Formato correto: /login <senha>"

def handle_logout():
    session.clear()
    init_session()
    return "Logout realizado com sucesso!"

def list_posts():
    try:
        posts = posts_collection.find().sort('date', -1)
        return "\n".join(
            f"[{post['id_str'][-4:]}] {post['title']} ({post.get('type', 'sem tipo')}) - {post['date'].strftime('%d/%m/%Y')}"
            for post in posts
        ) or "Nenhum post encontrado"
    except Exception as e:
        return f"Erro: {str(e)}"

def view_post(command):
    try:
        parts = command.split(' ', 1)
        if len(parts) < 2:
            return "Formato: /view <id_do_post>"
            
        post_id = parts[1].strip()
        
        # Busca por ID completo
        if ObjectId.is_valid(post_id):
            post = posts_collection.find_one({'_id': ObjectId(post_id)})
            if post:
                return format_post(post)
        
        # Busca por parte do ID string
        regex = re.compile(f'.*{re.escape(post_id)}$', re.IGNORECASE)
        post = posts_collection.find_one({'id_str': {'$regex': regex}})
        
        return format_post(post) if post else f"Nenhum post encontrado com ID contendo: {post_id}"
    except Exception as e:
        return f"Erro: {str(e)}"

def process_admin_commands(command):
    if command.lower() == '/newpost':
        session['editing'] = True
        session['post_data'] = {
            'title': 'Sem título',
            'type': 'diario',
            'content': [],
            'tags': []
        }
        return (
            "Modo edição ativado\n\n"
            "Comandos disponíveis:\n"
            "/title <texto>  - Definir título\n"
            "/type <tipo>    - Escolher tipo\n"
            "/tags <lista>   - Adicionar tags\n"
            "Digite o conteúdo linha por linha\n\n"
            "Finalize com:\n"
            "/salvar    - Salvar post\n"
            "/cancelar  - Cancelar edição"
        )
    
    if command.lower() == '/salvar' and session.get('editing'):
        return save_post()
    
    if command.lower() == '/cancelar' and session.get('editing'):
        session['editing'] = False
        session.pop('post_data', None)
        return "Edição cancelada"
    
    if command.lower().startswith('/title ') and session.get('editing'):
        session['post_data']['title'] = command[7:]
        return f"Título definido: {command[7:]}"
    
    if command.lower().startswith('/type ') and session.get('editing'):
        session['post_data']['type'] = command[6:]
        return f"Tipo definido: {command[6:]}"
    
    if command.lower().startswith('/tags ') and session.get('editing'):
        session['post_data']['tags'] = [t.strip() for t in command[6:].split(',')]
        return f"Tags definidas: {command[6:]}"
    
    if session.get('editing'):
        session['post_data']['content'].append(command)
        content_preview = '\n'.join(session['post_data']['content'][-3:])
        return (
            f"Conteúdo adicionado (linha {len(session['post_data']['content'])})\\n"
            f"Últimas linhas:\\n{content_preview}\\n"
            f"Continue digitando ou use /salvar"
        )
    
    return "Comando admin inválido"

def save_post():
    if not session['post_data']['content']:
        return "Adicione conteúdo antes de salvar!"
    
    try:
        new_id = ObjectId()
        post_data = {
            '_id': new_id,
            'id_str': str(new_id),
            'title': session['post_data']['title'],
            'type': session['post_data']['type'],
            'content': session['post_data']['content'],
            'tags': session['post_data']['tags'],
            'date': datetime.datetime.utcnow(),
            'author': 'admin'
        }
        posts_collection.insert_one(post_data)
        session['editing'] = False
        session.pop('post_data', None)
        return "Post salvo com sucesso!"
    except Exception as e:
        return f"Erro ao salvar: {str(e)}"

def format_post(post):
    
    content = '\n'.join(post.get('content', [])) 

    return f"""
    {post['title'].upper()}
    {post['date'].strftime('%d/%m/%Y %H:%M')}
    ━━━━━━━━━━━━━━━━━━
    {content}  
    ━━━━━━━━━━━━━━━━━━
    ID: {post['id_str']}
    Tags: {', '.join(post.get('tags', [])) or 'Nenhuma'}
    """.strip()

def help_text():
    general_help = """
COMANDOS DISPONÍVEIS:
/help          - Mostra esta ajuda
/clear         - Limpa o terminal
/list          - Lista todos os posts
/view <id>     - Visualiza post específico
/sobre         - Informações sobre o autor
/login <senha> - Login admin
    """.strip()
    
    admin_help = """
COMANDOS ADMIN:
/logout        - Sair da conta
/newpost       - Criar novo post
/salvar        - Salvar post em edição
/cancelar      - Cancelar edição
/title <texto> - Definir título
/type <tipo>   - Escolher tipo <diario, projeto, reflexao, arte>
/tags <lista>  - Adicionar tags <separadas por vírgula>
    """.strip()
    
    if session.get('admin'):
        return f"{general_help}\\n\\n{admin_help}"
    else:
        return general_help

def render_about():
    return r"""

Olá! Me chamo Alan José, e este é meu espaço pessoal em ASCII.

Sou desenvolvedor backend Python, 
com experiência em criação de APIs, automações, e sistemas para web.

Também atuo como analista de dados, onde transformo números em decisões, 
usando ferramentas como Python e Power BI.

Minha paixão por jogos me acompanha desde criança. 
E, com o tempo, descobri outra forma de arte que me fascina: ASCII art. 
A beleza das imagens feitas só com caracteres me lembra que a simplicidade também pode ser poderosa.

Este blog é meu diário digital, meu portfólio, e meu refúgio criativo. Tudo em texto, tudo no terminal — como deve ser.

Use `/list` para explorar o que eu tenho publicado.

Nos vemos por aqui.

>"Obrigado por visitar!"

--=++++++++++++++++++++++++++++++++++********+++**++++***+++******************
::::::--=++++++++++++++++++++*#@%#*#%@@@@@%#%%%%##*++*************************
---:::-:::::---=++++++++++++*%@@@@@@@@@@@@@@@@@@@@%%##************************
-:::::::::::::-:::---==+++++#@@@@@@@@@@@@@@@@@@@@@@@%##***********************
:::::::::::::::--::::::---=+%@@@@@@@@@@@@@@@@@@@@@@@@@@@%##**************#*##*
:::::::::::::::::::--:--+%#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%##****#######******
:::::::::::::::::::--*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%#######****#######
::::::::::::::::::::#%@@@@@@@@%%@@@*+==+@@@@@@@@@@@@@@@@@@@@@@####*####*####*+
:::::..:::::::::::::+*@@@@@@@#*###+====+%#@@@@@@@@@@@@@@@@@@@@@%##########*+++
:::::::::::::::::::=+@@@@@@@*+++===----=@%@@@#@@@@@@@@@@@@@@@@@%#######**+++++
:::::::::::::::::::-%@@@@@#*++========+%@@@#@@@@@@@@@@@@@@@@@@@####%#*++*+++++
..::::::::::::::::::=%@@@@@@%*++++*@@@@@@@@@%@@@%@@@@@@@@@@@@@@*+++**+++++++++
.......:...:::::::::+%*@@@@@@%*+++*%@@@@@@@@@@##+#@@@@@@@@@@@@@%+++*++++++++++
.......:...........::--@@@@@@@@*++#@@@@%#+*@@@%++*%@@@@@@@@@@@@%++++++++++++==
......-=...............+@@%@@@%=--+*%@%*=::=+**++=+@@@@@@@@@@@@#+==++===++====
......+:...............-%@@@@*-::---*@@@@@@@%+=====*@@@@@@@@@@@+=-----:::::...
......=................:%@%#=-:::::::--===---::---=*@@@@@@@@@@=::.............
.....::................-+==-::::--:::::::::::::--==*@@@@@@@@@=:.:.............
.....=:...............-==+*=-===-------::::::::--=+#@@@@@@@#=:..:.............
.....+................+++#@%#*@@@@%*--++=------==+*#@@@@+-*#:...:.............
....--...............:**#@@@@%++=--:::-+%+====+++*#%%*+=*+*=:...:.............
....=................-#%@@@@%**++++===+++*+=++**##%%%+=:-+=::...:.............
....++++++=-:::.....:+@@@@@@%%#**###%%#%%#+=**#%%%@@#+=+++::::..:.............
....+++++++++++++++++#@@@*++===-.:-==+*%%++*##%@@@@%#@%#*-:::...::............
...-+++**************#@@@@@@%###**+====+++*%%@@@@@@@%#@@+:::::..::............
...:::--===+++********#%@@@@@@%#*+=====++*%@@@@@@@@@%*#*::::::::::.::.........
.....::::::::::-------=+%#*+==-------==+*#%@@@@@@@@@*+:.....::#::::+*.........
......:::::::::::-----=#@@%%##++=====+#%#%%@@@@@@@@%+........=#::::*#:........
...::::.::::::::::---=*@@@@@@@@@@@@%%@@@@@@@@@@@@@%+..........::.::*%::.......
.::::::::::::::----:--*@@@@@@@@@@@@@@@@@@@@@@@@@%+=............:...=%::::.....
#=-----::-------:::::-=%@@@@@@@@@@@@@@@@@@@@@@#=-:...............:::=::.......
*****++**=+++=+=--------+#@@@@@@@@@@@@@@@@@@#+--....................:::::::::.
#+**#=#*++***%**+++#+++***%%@@@@@@@@@@@@@%#*=--......................:::::::::


    ...................,,BBBBBBBBBuod8B8bou,,.
              ..,uod8BBBBBBBBBBBBBBBBRPFT?l!i:.
         ,=m8BBBBBBBBBBBBBBBRPFT?!||||||||||||||
         !...:!TVBBBRPFT||||||||||!!^^""'   ||||
         !.......:!?|||||!!^^""'            ||||
         !.........||||                     ||||
         !.........||||  > Desenvolvedor:Alan|||       
         !.........||||    github.com/Mogutaa ||               
         !.........||||    linkedin.com/in/alan-jose-filho       
         !.........||||                     ||||                
         !.........||||                     ||||
         `.........||||                    ,||||
          .;.......||||               _.-!!|||||
   .,uodWBBBBb.....||||       _.-!!|||||||||!:'
!YBBBBBBBBBBBBBBb..!|||:..-!!|||||||!iof68BBBBBb....
!..YBBBBBBBBBBBBBBb!!||||||||!iof68BBBBBBRPFT?!::   `.
!....YBBBBBBBBBBBBBBbaaitf68BBBBBBRPFT?!:::::::::     `.
!......YBBBBBBBBBBBBBBBBBBBRPFT?!::::::;:!^"`;:::       `.
!........YBBBBBBBBBBRPFT?!::::::::::^''...::::::;         iBBbo.
`..........YBRPFT?!::::::::::::::::::::::::;iof68bo.      WBBBBbo.
  `..........:::::::::::::::::::::::;iof688888888888b.     `YBBBP^'
    `........::::::::::::::::;iof688888888888888888888b.     `
      `......:::::::::;iof688888888888888888888888888888b.
        `....:::;iof688888888888888888888888888888888899fT!
          `..::!8888888888888888888888888888888899fT|!^"'
            `' !!988888888888888888888888899fT|!^"'
                `!!8888888888888888899fT|!^"'
                  `!988888888899fT|!^"'
                    `!9899fT|!^"'
                      `!^"'
    """.strip()

if __name__ == '__main__':
    app.run(debug=True)