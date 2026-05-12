"""OC+ Runtime Cloud — API Server"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import subprocess, tempfile, os, uuid, json
from datetime import datetime
import docker

app = FastAPI(title="OC+ Runtime Cloud", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCKER_IMAGE = "ocp-sandbox:latest"
EXEC_TIMEOUT = 300  # 5 menit default
MAX_SCRIPT_SIZE = 100 * 1024  # 100KB cap

# --- Models ---

class ExecuteRequest(BaseModel):
    script: str  # OC+ script content
    timeout: Optional[int] = 300
    env_vars: Optional[dict] = {}

class ExecuteResponse(BaseModel):
    execution_id: str
    status: str
    stdout: str
    stderr: str
    duration_ms: int
    created_at: str


# --- Routes ---

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/execute", response_model=ExecuteResponse)
async def execute_script(req: ExecuteRequest, x_api_key: Optional[str] = Header(None)):
    """Jalanin OC+ script dalam Docker sandbox."""
    exec_id = str(uuid.uuid4())[:8]
    started = datetime.utcnow()

    # Input validation: script size cap
    if len(req.script.encode("utf-8")) > MAX_SCRIPT_SIZE:
        raise HTTPException(413, "Script exceeds 100KB size limit")

    # Simpen script ke file temporary
    script_path = f"/tmp/ocp-{exec_id}.ocp"
    with open(script_path, "w") as f:
        f.write(req.script)

    try:
        client = docker.from_env()
        container = client.containers.run(
            DOCKER_IMAGE,
            command=f"/script/{os.path.basename(script_path)}",
            volumes={os.path.dirname(script_path): {"bind": "/script", "mode": "ro"}},
            mem_limit="512m",
            cpu_quota=50000,
            pids_limit=50,
            read_only=True,
            tmpfs={"/tmp": "size=64M,mode=1777"},
            security_opt=["no-new-privileges:true"],
            cap_drop=["ALL"],
            network_disabled=True,
            detach=True,
            remove=False,
        )

        result = container.wait(timeout=req.timeout)
        stdout_bytes = container.logs(stdout=True, stderr=False)
        stderr_bytes = container.logs(stdout=False, stderr=True)

        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        container.remove()

        status = "success" if result["StatusCode"] == 0 else "failed"

    except Exception as e:
        stdout = ""
        stderr = str(e)
        status = "error"
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

    duration = int((datetime.utcnow() - started).total_seconds() * 1000)

    return ExecuteResponse(
        execution_id=exec_id,
        status=status,
        stdout=stdout,
        stderr=stderr,
        duration_ms=duration,
        created_at=started.isoformat(),
    )


@app.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    return {"execution_id": execution_id, "message": "History not implemented yet"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
