from http import HTTPStatus
from flask import Blueprint, request
from src.app import User, db
from sqlalchemy import inspect

# Define um Blueprint chamado 'user' para agrupar rotas relacionadas aos usuários,
# com prefixo '/users' nas URLs.
app = Blueprint('user', __name__, url_prefix='/users')

def _create_user():
    """
    Cria um novo usuário a partir dos dados fornecidos no corpo da requisição JSON.

    Espera que o JSON contenha a chave 'username'.
    Adiciona o novo usuário ao banco de dados e confirma a transação.
    """
    data = request.json
    user = User(
        username=data['username'],
    )
    db.session.add(user)
    db.session.commit()


def _list_users():
    """
    Retorna uma lista de todos os usuários cadastrados no banco de dados.

    Executa uma consulta SELECT na tabela de usuários e retorna uma lista de dicionários
    com as chaves 'id' e 'username' para cada usuário encontrado.
    """
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return [
        {
            "id": user.id,
            "username": user.username,
        }
        for user in users
    ]


@app.route('/', methods=['GET', 'POST'])
def list_or_create_user():
    """
    Rota principal para manipulação de usuários.

    - GET: retorna a lista de usuários.
    - POST: cria um novo usuário com base no JSON enviado.

    Returns:
        dict: Mensagem de sucesso ou lista de usuários.
        HTTPStatus: Código de status HTTP correspondente.
    """
    if request.method == 'POST':
        _create_user()
        return { 'message': 'User created!' }, HTTPStatus.CREATED
    else:
        return { 'users': _list_users() }, HTTPStatus.OK


@app.route('/<int:user_id>')
def get_user(user_id):
    """
    Retorna os detalhes de um usuário específico junto com suas tarefas associadas.

    Parâmetros:
        user_id (int): ID do usuário a ser buscado.

    Retorna:
        dict: Um dicionário contendo o ID, nome de usuário e uma lista de tarefas do usuário.
              Cada tarefa na lista contém seu ID, título e status de conclusão.

    Levanta:
        404 Not Found: Se o usuário com o ID especificado não for encontrado no banco de dados.
    """
    user = db.get_or_404(User, user_id)
    tasks = user.tasks # usa o relacionamento para pegar as tasks do usuário
    return {
        'id': user.id,
        'username': user.username,
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'done': task.done,
            }
            for task in tasks
        ]
    }
    

@app.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    """
    Atualiza os dados de um usuário existente com base no JSON enviado na requisição.

    Args:
        user_id (int): ID do usuário a ser atualizado.

    Processo:
        - Busca o usuário pelo ID, retorna 404 se não encontrado.
        - Atualiza os atributos presentes no JSON que correspondem a colunas do modelo User.
        - Salva as alterações no banco de dados.

    Returns:
        dict: Dicionário com os campos atualizados do usuário.
    """
    user = db.get_or_404(User, user_id)
    data = request.json
    
    mapper = inspect(User)
    for column in mapper.attrs:
        if column.key in data:
            setattr(user, column.key, data[column.key])
    db.session.commit()
    
    return {
        "id": user.id,
        "username": user.username
    }


@app.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Remove um usuário do banco de dados pelo seu ID.

    Args:
        user_id (int): ID do usuário a ser deletado.

    Processo:
        - Busca o usuário pelo ID, retorna 404 se não encontrado.
        - Deleta o usuário e confirma a operação.

    Returns:
        tuple: Resposta vazia com código HTTP 204 (No Content) indicando sucesso na exclusão.
    """
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    
    return "", HTTPStatus.NO_CONTENT