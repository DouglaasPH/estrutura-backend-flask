import click
from flask import Flask, current_app
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Base declarativa do SQLAlchemy 2.0, a partir da qual todos os modelos ORM devem herdar para mapear classes Python a tabelas do banco de dados.
class Base(DeclarativeBase):
    pass


# Instância do SQLAlchemy configurada para usar a base declarativa personalizada `Base` nos modelos ORM.
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()

class User(db.Model):
    """
    Representa um usuário do sistema.

    Atributos:
        id (int): Identificador único do usuário.
        username (str): Nome de usuário (único e obrigatório).
        tasks (list[Task]): Lista de tarefas atribuídas ao usuário.
    """    
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String, nullable=False)
    password: Mapped[str] = mapped_column(sa.String, nullable=False)
    role_id: Mapped[int] = mapped_column(sa.ForeignKey('role.id'))
    
    tasks: Mapped[list['Task']] = relationship(back_populates='user')
    role: Mapped['Role'] = relationship(back_populates='user')
    
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.username!r})"


class Task(db.Model):
    """
    Representa uma tarefa atribuída a um usuário.

    Atributos:
        id (int): Identificador único da tarefa.
        user_id (int): Chave estrangeira que referencia o usuário dono da tarefa.
        title (str): Título da tarefa (obrigatório).
        done (bool): Indica se a tarefa foi concluída.
        user (User): Referência ao usuário dono da tarefa.
    """
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('user.id'))
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    done: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    
    user: Mapped['User'] = relationship(back_populates='tasks')
    
    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r}, done={self.done!r})"


class Role(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)

    user: Mapped[list["User"]] = relationship(back_populates='role')
    
    def __repr__(self) -> str:
        return f"Role(id={self.id!r}, name={self.name!r})"


@click.command("init-db")
def init_db_command():
    """
    Comando CLI para inicializar o banco de dados da aplicação.

    Este comando cria todas as tabelas definidas pelos modelos SQLAlchemy associados
    à aplicação Flask, garantindo que o banco esteja preparado para uso.

    Executa `db.create_all()` dentro do contexto da aplicação para garantir o acesso
    correto à configuração e recursos do Flask.

    Uso no terminal:
        flask --app src.app init-db

    Exibe uma mensagem informando que o banco foi inicializado com sucesso.
    """    
    global db
    with current_app.app_context():
        db.create_all()
    click.echo("Iniatilzed the database.")


def create_app(test_config=None):
    """
    Fábrica de criação da aplicação Flask.

    Esta função configura e retorna uma instância da aplicação Flask, permitindo
    que a configuração seja modular e reutilizável para diferentes ambientes (desenvolvimento, testes, produção).

    Parâmetros:
    -----------
    test_config : dict, opcional
        Um dicionário de configurações que, se fornecido, sobrescreve a configuração padrão.
        Usado principalmente para testes.

    Retorna:
    --------
    Flask
        A instância da aplicação Flask totalmente configurada.
    
    Funcionalidades:
    ----------------
    - Define a chave secreta e o banco de dados SQLite padrão.
    - Permite carregar configurações adicionais a partir de 'instance/config.py'.
    - Inicializa a extensão SQLAlchemy.
    - Registra comandos de terminal (CLI), como o 'init-db'.
    - Prepara o ponto para registro de blueprints futuros.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///diotasks.sqlite',
        JWT_SECRET_KEY='super-secret',
    )
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # register cli commands
    app.cli.add_command(init_db_command)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # register blueprints
    from src.controllers import user, task, auth, role
    
    app.register_blueprint(user.app)
    app.register_blueprint(task.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)
    
    return app