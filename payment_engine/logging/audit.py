from pathlib import Path
from datetime import datetime, timezone


class AuditLogger:
    """
    Records important payment events to an audit log.
    """

    def __init__(self, logfile="logs/payment_audit.log"):
        self.logfile = Path(logfile)
        self.logfile.parent.mkdir(parents=True, exist_ok=True)

    def log(self, action, reference, status, gateway="", details=""):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        line = (
            f"{timestamp} | "
            f"{action:<10} | "
            f"{reference:<20} | "
            f"{status:<10} | "
            f"{gateway:<12} | "
            f"{details}\n"
        )

        with self.logfile.open("a", encoding="utf-8") as f:
            f.write(line)
