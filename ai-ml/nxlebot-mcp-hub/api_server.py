"""
Nxlebot MCP API Server
HTTP wrapper untuk MCP tools
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
import subprocess
import os
import re
from typing import List, Optional
from pathlib import Path

app = FastAPI(title="Nxlebot MCP API", version="1.0.0")

# Path Config
WORKSPACE_ROOT = Path("/home/nxelleai/.openclaw/workspace")
GENERATED_COURSES_DIR = WORKSPACE_ROOT / "nxlebot-mcp-hub" / "generated_courses"


class DomainRequest(BaseModel):
    domain: str


class VideoPromptRequest(BaseModel):
    description: str
    style: str = "cinematic"

class ShellRequest(BaseModel):
    ip: str
    port: int
    lang: str = "bash"  # bash, python, php, perl, ruby, nc

class HydraRequest(BaseModel):
    target_ip: str
    service: str = "ssh"  # ssh, ftp, http-post-form
    user_list: str = "/usr/share/wordlists/rockyou.txt"
    pass_list: str = "/usr/share/wordlists/rockyou.txt"
    username: str = "admin"

class DocsGenerateRequest(BaseModel):
    target_path: str  # Relative to workspace or absolute path
    output_name: str = "course.html"


@app.get("/")
async def root():
    return {
        "service": "Nxlebot MCP API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "GET /status",
            "POST /security/scan",
            "POST /security/subdomains",
            "POST /video/prompt",
        ],
    }


@app.get("/status")
async def status():
    return {
        "status": "online",
        "tools_available": [
            "security_scan_domain",
            "lookup_subdomains",
            "generate_video_prompt",
        ],
        "workspace": "/home/nxelleai/.openclaw/workspace",
    }


@app.post("/security/scan")
async def scan_domain(req: DomainRequest):
    """Scan security headers"""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(f"https://{req.domain}")
            
            headers = {
                "CSP": response.headers.get("Content-Security-Policy", "MISSING"),
                "X-XSS-Protection": response.headers.get("X-XSS-Protection", "MISSING"),
                "X-Content-Type-Options": response.headers.get(
                    "X-Content-Type-Options", "MISSING"
                ),
                "Referrer-Policy": response.headers.get("Referrer-Policy", "MISSING"),
                "Strict-Transport-Security": response.headers.get(
                    "Strict-Transport-Security", "MISSING"
                ),
            }
            
            return {
                "domain": req.domain,
                "status_code": response.status_code,
                "security_headers": headers,
                "missing_headers": [
                    k for k, v in headers.items() if v == "MISSING"
                ],
            }
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@app.post("/security/subdomains")
async def find_subdomains(req: DomainRequest):
    """Lookup subdomains via Certificate Transparency"""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"https://crt.sh/?q=%.{req.domain}&output=json"
            )
            
            if response.status_code == 200:
                data = response.json()
                subdomains = set()
                for entry in data[:200]:  # Limit processing
                    name = entry.get("name_value", "")
                    subdomains.update(name.split("\n"))
                
                return {
                    "domain": req.domain,
                    "subdomains_found": len(subdomains),
                    "subdomains": sorted(list(subdomains))[:50],
                }
            
            return {"error": "Failed to fetch certificate transparency logs"}
    except httpx.RequestError as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@app.post("/video/prompt")
async def create_video_prompt(req: VideoPromptRequest):
    """Generate optimized video prompt"""
    style_templates = {
        "cinematic": "cinematic lighting, 4k, highly detailed, dramatic atmosphere",
        "anime": "anime style, vibrant colors, detailed animation, studio ghibli",
        "realistic": "photorealistic, 8k, ultra detailed, natural lighting",
        "cyberpunk": "cyberpunk, neon lights, futuristic, dystopian atmosphere",
        "fantasy": "fantasy art, magical atmosphere, ethereal lighting, epic composition",
    }
    
    style_prompt = style_templates.get(req.style, style_templates["cinematic"])
    
    return {
        "prompt": f"{req.description}, {style_prompt}",
        "style": req.style,
        "recommended_models": [
            "Stable Video Diffusion",
            "Runway Gen-2",
            "Pika Labs",
            "Kling AI",
            "Luma Dream Machine",
        ],
        "aspect_ratios": ["16:9", "9:16", "1:1", "21:9"],
    }


@app.post("/docs/generate")
async def generate_docs(req: DocsGenerateRequest):
    """Generate interactive HTML course from a codebase"""
    target_dir = WORKSPACE_ROOT / req.target_path
    
    if not target_dir.exists():
        raise HTTPException(status_code=404, detail=f"Target path not found: {req.target_path}")
        
    output_file = GENERATED_COURSES_DIR / req.output_name
    GENERATED_COURSES_DIR.mkdir(exist_ok=True)

    try:
        # Run the Python explainer script
        script_path = Path(__file__).parent / "code_explainer.py"
        process = subprocess.run(
            [
                "/home/nxelleai/.openclaw/workspace/venv_bounty/bin/python",
                str(script_path),
                str(target_dir),
                "--output", req.output_name
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if process.returncode != 0:
            return {"error": process.stderr}
            
        return {
            "status": "success",
            "message": "Course generated successfully",
            "course_path": str(output_file),
            "view_url": f"/static/courses/{req.output_name}" # Placeholder for static file serving
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Generation timed out. Codebase too large?")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
