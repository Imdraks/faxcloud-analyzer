#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaxCloud Analyzer v3.0 - Flask Factory
"""
import logging
from flask import Flask
from flask_compress import Compress

logger = logging.getLogger(__name__)

def create_app(config=None):
    """Create and configure the Flask application"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(current_dir, 'templates'),
                static_folder=os.path.join(current_dir, 'static'),
                static_url_path='/static')
    
    # Configuration
    app.config.update(
        DEBUG=True,
        JSON_SORT_KEYS=False,
        COMPRESS_LEVEL=6
    )
    
    if config:
        app.config.update(config)
    
    # Compression
    Compress(app)
    
    # Register blueprints
    from app.routes import bp_web, bp_api
    app.register_blueprint(bp_web)
    app.register_blueprint(bp_api)
    
    logger.info("[OK] Application initialized successfully")
    
    return app
