from fastapi import APIRouter, HTTPException, Query

from backend.analyzer.report_store import list_reports, load_report

router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('')
def get_reports(limit: int = Query(default=25, ge=1, le=200)):
    items = list_reports(limit=limit)
    return {'items': items, 'count': len(items)}


@router.get('/{report_id}')
def get_report(report_id: str):
    try:
        return load_report(report_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
