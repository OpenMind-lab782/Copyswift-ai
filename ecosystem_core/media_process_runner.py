import logging
import os
import signal
import subprocess
import time
from dataclasses import dataclass


logger = logging.getLogger(__name__)


class MediaProcessTimeoutError(RuntimeError):
    pass


@dataclass(frozen=True)
class MediaProcessResult:
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool
    elapsed_seconds: float


class MediaProcessRunner:
    def run(self, command, timeout):
        if not command:
            raise ValueError("Media process command must not be empty.")
        if timeout is None or timeout <= 0:
            raise ValueError("Media process timeout must be greater than zero.")

        started = time.monotonic()
        process = subprocess.Popen(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            logger.warning(
                "MEDIA_PROCESS_TIMEOUT elapsed=%.3f",
                time.monotonic() - started,
            )
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            raise MediaProcessTimeoutError(
                "Media process exceeded its allowed execution time."
            ) from exc

        return MediaProcessResult(
            return_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
            timed_out=False,
            elapsed_seconds=time.monotonic() - started,
        )
