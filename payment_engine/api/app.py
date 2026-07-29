from flask import Flask


def create_app():
    app = Flask(__name__)

    from .routes import api
    app.register_blueprint(api)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False,
    )
