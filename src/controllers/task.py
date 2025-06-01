from http import HTTPStatus
from flask import Blueprint, request
from src.app import Task, db
from sqlalchemy import inspect

# Define um Blueprint chamado 'task' para agrupar rotas relacionadas aos usuários,
# com prefixo '/tasks' nas URLs.
app = Blueprint('task', __name__, url_prefix='/tasks')

def _create_task():
    data = request.json
    task = Task(
        user_id= data['user_id'],
        title= data['title'],
        done= data['done'],        
    )
    db.session.add(task)
    db.session.commit()


def _list_tasks():
    query = db.select(Task)
    tasks = db.session.excute(query).scalars()
    return [
        {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "done": task.done,
        }
        for task in tasks
    ]


@app.route('/', methods=['GET', 'POST'])
def list_or_create_user():
    if request.method == 'POST':
        _create_task()
        return { 'message': 'Task created!' }, HTTPStatus.CREATED
    else:
        return { 'tasks': _list_tasks() }, HTTPStatus.OK


@app.route('/<int:task_id>')
def get_task(task_id):
    """
    Retorna os detalhes de uma tarefa específica pelo seu ID.

    Parâmetros:
        task_id (int): ID da tarefa a ser buscada.

    Retorna:
        dict: Um dicionário contendo o ID da tarefa, ID do usuário associado, título e status de conclusão.

    Levanta:
        404 Not Found: Se a tarefa com o ID especificado não for encontrada no banco de dados.
    """
    task = db.get_or_404(Task, task_id)
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "done": task.done,
        }


@app.route('/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    """
    Atualiza os campos de uma tarefa existente com os dados fornecidos na requisição JSON.

    Parâmetros:
        task_id (int): ID da tarefa a ser atualizada.

    Corpo da requisição:
        JSON com os campos da tarefa que devem ser atualizados (ex: "title", "done").

    Retorna:
        dict: Um dicionário com os dados atualizados da tarefa.

    Levanta:
        404 Not Found: Se a tarefa com o ID especificado não for encontrada no banco de dados.
    """
    task = db.get_or_404(Task, task_id)
    data = request.json
    
    mapper = inspect(Task)
    for column in mapper.attrs:
        if column.key in data:
            setattr(task, column.key, data[column.key]) 
    db.session.commit()
    
    return {
        "id": task.id,
        "user_id": task.user_id,
        "title": task.title,
        "done": task.done,
    }


@app.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Remove uma tarefa existente do banco de dados pelo seu ID.

    Parâmetros:
        task_id (int): ID da tarefa a ser deletada.

    Retorna:
        str: Resposta vazia com status HTTP 204 (No Content) em caso de sucesso.

    Levanta:
        404 Not Found: Se a tarefa com o ID especificado não for encontrada no banco de dados.
    """
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    
    return '', HTTPStatus.NO_CONTENT