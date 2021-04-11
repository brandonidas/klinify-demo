from flask.cli import FlaskGroup

from project import app, db, User, Admin


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    #db.session.add(Admin(email="michael@mherman.org"))
    db.session.add(Admin(name="brandon", password="brandon"))
    db.session.commit()


if __name__ == "__main__":
    cli()