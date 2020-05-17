from typing import List, Tuple
from services.models.VisitModel import Visit, db
from sqlalchemy import func, desc

class Visits:
    @classmethod
    def set_visit(cls,ip: str, visitable_id: int, visitable_type: str) -> None:
        visit = Visit.query.filter(Visit.ip == ip,
            Visit.visitable_id == visitable_id,
            Visit.visitable_type == visitable_type).first()
        if not visit:
            save_visit = Visit(ip,visitable_id,visitable_type)
            save_visit.save_to_db()

    @classmethod
    def visit_popular_by(cls,visit_type: str,limit: int) -> List[Tuple[int,int]]:
        visits = db.session.query(Visit.visitable_id.label('visit_id'),
            func.count(Visit.visitable_id).label('count_total')).group_by('visit_id').order_by(desc('count_total')).filter(
            Visit.visitable_type == visit_type).limit(limit).all()
        return visits
