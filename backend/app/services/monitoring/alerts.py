import logging

logger = logging.getLogger(__name__)

class AlertManager:
    """Handles system alerts for critical failures or violations."""

    @staticmethod
    def send_alert(title: str, message: str, severity: str = "warning"):
        """
        Sends an alert.
        In a real enterprise system, this could trigger PagerDuty, Slack, or email.
        For now, it logs as an error/warning and could publish to Redis.
        """
        if severity == "critical":
            logger.error(f"[CRITICAL ALERT] {title}: {message}")
        elif severity == "warning":
            logger.warning(f"[WARNING ALERT] {title}: {message}")
        else:
            logger.info(f"[INFO ALERT] {title}: {message}")

alert_manager = AlertManager()
