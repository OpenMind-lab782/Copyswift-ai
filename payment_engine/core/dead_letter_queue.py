import json
from pathlib import Path
from datetime import datetime, timezone


class DeadLetterQueue:
    """
    Stores failed operations for later inspection
    and retry.
    """

    def __init__(self, filename="dead_letters.json"):
        self.file = Path(filename)

        if not self.file.exists():
            self.file.write_text("[]", encoding="utf-8")

    def _load(self):
        return json.loads(
            self.file.read_text(encoding="utf-8")
        )

    def _save(self, records):
        self.file.write_text(
            json.dumps(records, indent=4),
            encoding="utf-8"
        )

    def add(self, operation, reference, reason):
        records = self._load()

        records.append({
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "operation": operation,
            "reference": reference,
            "reason": reason
        })

        self._save(records)

    def list(self):
        return self._load()
