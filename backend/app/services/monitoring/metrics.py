from sqlalchemy.orm import Session
from app.models import AnalyticsMetric
from typing import Optional
from datetime import datetime, timezone

class MetricsRegistry:
    """Core metrics registry to record analytics data."""
    
    @staticmethod
    def record_metric(db: Session, name: str, value: float, dimension: Optional[str] = None):
        """Records a single metric point."""
        metric = AnalyticsMetric(
            metric_name=name,
            metric_value=value,
            dimension=dimension,
            recorded_at=datetime.now(timezone.utc)
        )
        db.add(metric)
        db.commit()

registry = MetricsRegistry()
