import os
from app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", Config.PORT))
    is_dev = os.environ.get("FLASK_ENV") == "development"
    # host="0.0.0.0" permite conexões locais ou pela rede/container
    app.run(host="0.0.0.0", port=port, debug=is_dev)
