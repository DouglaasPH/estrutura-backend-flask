from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity
from src.app import User, db
from functools import wraps
from flask import request


def requires_role(role_name):
    """
    Decorador dinâmico que protege uma rota exigindo que o usuário autenticado
    possua um papel (role) específico.

    Parâmetros:
        role_name (str): Nome do papel necessário para acessar a rota (ex: 'admin').

    Retorna:
        A função decorada, ou uma resposta 403 FORBIDDEN se o papel não corresponder.

    Uso:
        @jwt_required()
        @requires_role('admin')
        def rota_admin():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = get_jwt_identity()
            user = db.get_or_404(User, user_id)
            
            if user.role.name != role_name:
                return { 'message': 'User dont have access.' }, HTTPStatus.FORBIDDEN
            return f(*args, **kwargs)
        return wrapped
    return decorator


def requires_user():
    """
    Decorador que protege uma rota exigindo que o usuário autenticado
    seja o mesmo usuário cujo ID está na URL da requisição.

    Requer que a rota tenha um parâmetro <int:user_id>.

    Retorna:
        A função decorada, ou uma resposta 403 FORBIDDEN se o usuário logado
        não for o mesmo do ID presente na URL.

    Uso:
        @jwt_required()
        @requires_user()
        def get_user(user_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            user_id = int(get_jwt_identity())
            target_user_id = int(request.view_args.get('user_id'))  # pega da URL

            if user_id != target_user_id:
                return { 'message': 'User dont have access.' }, HTTPStatus.FORBIDDEN
            return f(*args, **kwargs)
        return wrapped
    return decorator