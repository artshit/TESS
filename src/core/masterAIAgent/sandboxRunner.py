# sandboxRunner.py
import subprocess
import tempfile
import os
import shlex
import logging

class ScriptSandbox:
    def __init__(self, time_limit_sec=60, memory_limit_mb=100):
        """
        Sandbox runner to execute scripts safely with resource limits.
        :param time_limit_sec: max execution time in seconds.
        :param memory_limit_mb: max memory usage in MB (currently advisory - platform dependent).
        """
        self.time_limit_sec = time_limit_sec
        self.memory_limit_mb = memory_limit_mb

    def run_script(self, script: str, language: str = "python") -> dict:
        """
        Execute the given script safely.
        :param script: Script source code as a string.
        :param language: Script language (only 'python' implemented for now).
        :return: Dict containing 'stdout', 'stderr', 'success' boolean.
        """
        if language.lower() != "python":
            return {
                "stdout": "",
                "stderr": f"Unsupported sandbox language: {language}",
                "success": False
            }

        # Create a temporary file for the script
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tf:
            script_path = tf.name
            tf.write(script)

        try:
            # Build command with safety measures
            # On Unix, you could add 'timeout' and 'ulimit' wrappers, but for cross-platform compatibility:
            # We use subprocess.run with timeout param
            process = subprocess.run(
                ["python3", script_path],
                capture_output=True,
                timeout=self.time_limit_sec,
                text=True
            )
            success = (process.returncode == 0)
            stdout = process.stdout
            stderr = process.stderr

        except subprocess.TimeoutExpired:
            stdout = ""
            stderr = f"Execution timed out after {self.time_limit_sec} seconds."
            success = False

        except Exception as e:
            stdout = ""
            stderr = f"Error running script: {str(e)}"
            success = False

        finally:
            # Clean up the temporary file
            try:
                os.unlink(script_path)
            except Exception as cleanup_error:
                logging.warning(f"Failed to delete temp script file: {cleanup_error}")

        return {
            "stdout": stdout,
            "stderr": stderr,
            "success": success
        }
