from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.database import get_db
from app.core.deps import get_current_session
from app.models.shipment import ShipmentSession
from app.models.discrepancy import Discrepancy
from app.models.checklist_item import ChecklistItem
from app.schemas.dashboard import DashboardResponse, RecentSessionSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"], dependencies=[Depends(get_current_session)])

@router.get("", response_model=DashboardResponse)
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    # 1. Total sessions
    total_sessions_stmt = select(func.count(ShipmentSession.id))
    total_sessions = (await db.execute(total_sessions_stmt)).scalar() or 0

    # 2. Open discrepancies count by severity
    critical_stmt = select(func.count(Discrepancy.id)).where(Discrepancy.severity == "critical", Discrepancy.status == "open")
    warning_stmt = select(func.count(Discrepancy.id)).where(Discrepancy.severity == "warning", Discrepancy.status == "open")
    info_stmt = select(func.count(Discrepancy.id)).where(Discrepancy.severity == "info", Discrepancy.status == "open")

    crit_count = (await db.execute(critical_stmt)).scalar() or 0
    warn_count = (await db.execute(warning_stmt)).scalar() or 0
    info_count = (await db.execute(info_stmt)).scalar() or 0

    # 3. Overall pass rate (proportion of checklist items that passed)
    total_checklist_stmt = select(func.count(ChecklistItem.id))
    passed_checklist_stmt = select(func.count(ChecklistItem.id)).where(ChecklistItem.is_passed == True)

    total_checks = (await db.execute(total_checklist_stmt)).scalar() or 0
    passed_checks = (await db.execute(passed_checklist_stmt)).scalar() or 0

    pass_rate = round(passed_checks / total_checks, 2) if total_checks > 0 else 1.0

    # 4. Recent sessions
    recent_stmt = select(ShipmentSession).order_by(desc(ShipmentSession.created_at)).limit(5)
    recent_sessions_db = (await db.execute(recent_stmt)).scalars().all()

    recent_sessions = [
        RecentSessionSummary(
            id=s.id,
            name=s.name,
            status=s.status,
            created_at=s.created_at
        )
        for s in recent_sessions_db
    ]

    return DashboardResponse(
        total_sessions=total_sessions,
        open_discrepancies={
            "critical": crit_count,
            "warning": warn_count,
            "info": info_count
        },
        overall_pass_rate=pass_rate,
        recent_sessions=recent_sessions
    )
