from app import create_app, db #, cli
from app.main_func import cli
from app.user.models import User, Post

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}