import os
from dotenv import load_dotenv
from api import create_app

load_dotenv()

run_environment = os.getenv("RUN_ENVIRONMENT")

app = create_app(run_environment)
debug = app.config['DEBUG']
host = app.config['HOST']

if __name__ == "__main__":
    app.run(debug=debug, port=5000, host=host)