import threading
import uuid
from typing import Any, Callable, Dict, Optional


class JobRegistry:
    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, payload: Optional[Dict[str, Any]] = None) -> str:
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "status": "pending",
                "progress": 0,
                "error": None,
                "result": None,
                "payload": payload or {},
            }
        return job_id

    def set_status(self, job_id: str, status: str, progress: Optional[int] = None) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["status"] = status
            if progress is not None:
                job["progress"] = progress

    def set_error(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["status"] = "error"
            job["error"] = error

    def set_result(self, job_id: str, result: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["status"] = "done"
            job["result"] = result

    def get(self, job_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._jobs.get(job_id)


jobs = JobRegistry()


