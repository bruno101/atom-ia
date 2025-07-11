from fastapi.middleware.cors import CORSMiddleware
import logging

def configure_app(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:63001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logging.basicConfig(level=logging.INFO)