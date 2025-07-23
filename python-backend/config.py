from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from dotenv import load_dotenv

load_dotenv()

def configure_app(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[os.getenv('URL_ATOM', 'http://localhost:63001'), os.getenv('URL_FRONTEND', 'http://localhost:3000')],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logging.basicConfig(level=logging.INFO)