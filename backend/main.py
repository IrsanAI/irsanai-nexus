from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes_analyze import router as analyze_router
from backend.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(analyze_router)

frontend_dir = Path('frontend')

if frontend_dir.exists():
    app.mount('/assets', StaticFiles(directory=frontend_dir), name='frontend-assets')


@app.get('/health')
def health():
    return {'status': 'ok', 'version': settings.app_version}


@app.get('/')
def home():
    index = frontend_dir / 'index.html'
    if index.exists():
        return FileResponse(index)
    return {'message': 'IRSAN AI Nexus API', 'health': '/health'}
