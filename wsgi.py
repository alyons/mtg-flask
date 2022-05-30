from src.server import create_app

app = None

if __name__ == '__main__':
    app = create_app()
    app.run()
