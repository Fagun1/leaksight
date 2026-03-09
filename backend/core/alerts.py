"""
Alert rules for monitoring (PROJECT_SPEC_CONTINUATION §9.6).
"""
from dataclasses import dataclass
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    name: str
    metric: str
    condition: str
    threshold: float
    severity: AlertSeverity
    window_minutes: int
    message_template: str


ALERT_RULES = [
    AlertRule(
        name="high_crawl_error_rate",
        metric="crawl_error_rate",
        condition="gt",
        threshold=0.10,
        severity=AlertSeverity.WARNING,
        window_minutes=15,
        message_template="Crawl error rate is {value:.1%}, threshold is {threshold:.1%}",
    ),
    AlertRule(
        name="no_active_workers",
        metric="active_workers",
        condition="lt",
        threshold=1,
        severity=AlertSeverity.CRITICAL,
        window_minutes=5,
        message_template="No active crawl workers detected",
    ),
    AlertRule(
        name="queue_backlog",
        metric="queue_depth_high",
        condition="gt",
        threshold=1000,
        severity=AlertSeverity.WARNING,
        window_minutes=30,
        message_template="High-priority queue has {value} pending tasks",
    ),
    AlertRule(
        name="result_processing_backlog",
        metric="queue_depth_results",
        condition="gt",
        threshold=500,
        severity=AlertSeverity.WARNING,
        window_minutes=15,
        message_template="Results queue has {value} unprocessed items",
    ),
]
