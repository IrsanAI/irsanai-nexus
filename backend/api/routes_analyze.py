from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from backend.analyzer.cloner import ClonerError, cleanup_repo, clone_repo
from backend.analyzer.report_store import persist_report
from backend.analyzer.unified_analyzer import analyze

router = APIRouter(tags=['analyze'])


class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl
    save_report: bool = True



class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl


@router.post('/analyze')
def analyze_repo(payload: AnalyzeRequest):
    repo_path: Path | None = None
    try:
        repo_url = str(payload.repo_url)
        repo_path = clone_repo(repo_url)
        analysis = analyze(repo_path, repo_url)

        response = {'status': 'success', 'analysis': analysis}
        if payload.save_report:
            saved_path = persist_report(analysis)
            response['report_id'] = saved_path.name

        return response
    except ClonerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if repo_path is not None:
            cleanup_repo(repo_path)
