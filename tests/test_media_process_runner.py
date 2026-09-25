import sys
import time
import unittest

from ecosystem_core.media_process_runner import (
    MediaProcessRunner,
    MediaProcessResult,
    MediaProcessTimeoutError,
)


class MediaProcessRunnerTests(unittest.TestCase):
    def test_runner_returns_structured_success_result(self):
        runner = MediaProcessRunner()
        result = runner.run(
            [sys.executable, "-c", "print(123)"],
            timeout=5,
        )

        self.assertIsInstance(result, MediaProcessResult)
        self.assertEqual(result.return_code, 0)
        self.assertEqual(result.stdout.strip(), "123")
        self.assertFalse(result.timed_out)
        self.assertGreaterEqual(result.elapsed_seconds, 0.0)

    def test_runner_reports_nonzero_exit_without_shell(self):
        runner = MediaProcessRunner()
        result = runner.run(
            [sys.executable, "-c", "import sys; print('failure'); sys.exit(7)"],
            timeout=5,
        )

        self.assertEqual(result.return_code, 7)
        self.assertIn("failure", result.stdout)
        self.assertFalse(result.timed_out)

    def test_runner_times_out_and_returns_controlled_timeout(self):
        runner = MediaProcessRunner()

        started = time.monotonic()
        with self.assertRaises(MediaProcessTimeoutError):
            runner.run(
                [sys.executable, "-c", "import time; time.sleep(30)"],
                timeout=0.2,
            )
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 5.0)

    def test_runner_rejects_empty_command(self):
        runner = MediaProcessRunner()

        with self.assertRaises(ValueError):
            runner.run([], timeout=5)

    def test_runner_rejects_invalid_timeout(self):
        runner = MediaProcessRunner()

        with self.assertRaises(ValueError):
            runner.run([sys.executable, "-c", "print(123)"], timeout=0)

    def test_timeout_terminates_process_group(self):
        import os
        import tempfile

        runner = MediaProcessRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            pid_file = os.path.join(temp_dir, "child.pid")
            child_code = "import time; time.sleep(30)"
            parent_code = (
                "import subprocess,time,sys; "
                f"child=subprocess.Popen([sys.executable, '-c', {child_code!r}], "
                "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); "
                f"open({pid_file!r}, 'w').write(str(child.pid)); "
                "time.sleep(30)"
            )
            command = [sys.executable, "-c", parent_code]

            with self.assertRaises(MediaProcessTimeoutError):
                runner.run(command, timeout=1.0)

            with open(pid_file) as pid_handle:
                child_pid = int(pid_handle.read())
            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                try:
                    os.kill(child_pid, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.05)
            else:
                self.fail("Timed-out process group left the child process alive.")


if __name__ == "__main__":
    unittest.main()
