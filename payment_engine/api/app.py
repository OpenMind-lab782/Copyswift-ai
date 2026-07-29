from flask import Flask

from payment_engine.api.routes import api
from payment_engine.api.transactions import transactions


def create_app():
    app = Flask(__name__)

    app.register_blueprint(api)
    app.register_blueprint(transactions)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False,
    )
