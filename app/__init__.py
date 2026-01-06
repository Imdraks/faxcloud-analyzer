"""
Application principale FaxCloud Analyzer
Structure propre et modulaire
"""
import os
import logging
from flask import Flask, render_template, request
from flask_compress import Compress
from config.settings import DEBUG, LOG_LEVEL, LOG_FILE

# ========== LOGGING ==========
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """Créer et configurer l'application Flask"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # ========== CONFIGURATION ==========
    if config:
        app.config.from_object(config)
    else:
        from config import settings
        app.config.update(
            DEBUG=settings.DEBUG,
            SQLALCHEMY_DATABASE_URI=settings.SQLALCHEMY_DATABASE_URI,
            SQLALCHEMY_TRACK_MODIFICATIONS=settings.SQLALCHEMY_TRACK_MODIFICATIONS,
            SECRET_KEY=settings.SECRET_KEY,
            UPLOAD_FOLDER=settings.UPLOAD_FOLDER,
            MAX_CONTENT_LENGTH=settings.MAX_CONTENT_LENGTH,
        )
    
    # ========== EXTENSIONS ==========
    Compress(app)
    
    # ========== ROUTES ==========
    from app.routes import bp_web, bp_api
    app.register_blueprint(bp_web)
    app.register_blueprint(bp_api)
    
    # ========== ERROR HANDLERS ==========
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return {'error': 'Not found'}, 404
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        if request.path.startswith('/api/'):
            return {'error': 'Internal server error'}, 500
        return render_template('500.html'), 500
    
    logger.info("[OK] Application initialized successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("Starting FaxCloud Analyzer v3.0...")
    app.run(debug=DEBUG)
