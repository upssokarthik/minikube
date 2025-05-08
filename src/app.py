import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def print_env():
    env_vars = {key: os.environ[key] for key in os.environ}
    return "<br>".join([f"{key}: {value}" for key, value in env_vars.items()])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)