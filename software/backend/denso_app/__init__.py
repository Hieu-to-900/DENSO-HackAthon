import os
from flask import Flask

from .config import Config
from .api import register_blueprints


def create_app() -> Flask:
    """
    Application factory for DENSO Forecast Suite backend.
    """
    # Trỏ tới /frontend folder (ngoài /backend)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_folder = os.path.join(base_dir, '../../frontend/templates')
    static_folder = os.path.join(base_dir, '../../frontend/static')
    
    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
        static_url_path="/static",
    )
    app.config.from_object(Config)
    register_blueprints(app)
    return app