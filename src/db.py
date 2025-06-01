import sqlite3

import click
from flask import current_app, g

def get_db():
    """
    Obtém a conexão com o banco de dados SQLite para a requisição atual.

    Se a conexão ainda não existir, cria uma nova conexão e armazena no objeto
    global `g` do Flask, garantindo que a mesma conexão seja reutilizada durante
    toda a requisição.

    Configura a conexão para interpretar tipos declarados e retorna as linhas
    como dicionários (sqlite3.Row).

    Returns:
        sqlite3.Connection: conexão com o banco de dados SQLite.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        
    return g.db


def close_db(e=None):
    """
    Fecha a conexão com o banco de dados armazenada no objeto global `g`.

    É chamada automaticamente ao final do ciclo de vida da requisição para liberar recursos.

    Args:
        e (Exception, opcional): exceção que pode ter sido gerada durante a requisição.
    """
    db = g.pop("db", None)
    
    if db is not None:
        db.close()


def init_db():
    """
    Inicializa o banco de dados executando o script SQL contido no arquivo 'schema.sql'.

    Lê o arquivo de esquema do banco na pasta do projeto e executa os comandos SQL
    para criar tabelas e estruturas necessárias.
    """
    db = get_db()
    
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """
    Comando de linha de comando para inicializar o banco de dados.

    Ao executar 'flask init-db', limpa dados existentes e cria novas tabelas
    conforme definido no script SQL.
    """
    init_db()
    click.echo("Initialzed the database.")


def init_app(app):
    """
    Registra funções de inicialização no app Flask.

    - Registra o fechamento automático da conexão SQLite ao término da requisição.
    - Registra o comando CLI 'init-db' para criação do banco via terminal.

    Args:
        app (Flask): instância da aplicação Flask.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)