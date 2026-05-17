"""
SynapseIP Blueprint Executor MCP Server
Provides tools for file operations, shell commands, and package management
to enable self-execution of blueprint plans.
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio

# Configuration
WORKSPACE_DIR = os.environ.get("SYNAPSE_WORKSPACE", ".")
ALLOWED_COMMANDS = [
    "npm", "npx", "pip", "pip3", "python", "python3", "node", "git",
    "mkdir", "touch", "rm", "cp", "mv", "cat", "echo", "ls", "pwd"
]

class SynapseExecutorServer:
    def __init__(self):
        self.workspace = Path(WORKSPACE_DIR).resolve()
        
    def ensure_workspace(self):
        """Ensure workspace directory exists and is accessible."""
        if not self.workspace.exists():
            self.workspace.mkdir(parents=True, exist_ok=True)
        return self.workspace
    
    # ========== FILE OPERATIONS ==========
    
    async def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Create a new file with the given content."""
        file_path = self.ensure_workspace() / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "path": str(file_path),
            "size": len(content),
            "message": f"Created file: {path}"
        }
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read the contents of a file."""
        file_path = self.ensure_workspace() / path
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "path": str(file_path),
            "content": content,
            "size": len(content)
        }
    
    async def update_file(self, path: str, content: str) -> Dict[str, Any]:
        """Update or create a file with the given content."""
        file_path = self.ensure_workspace() / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "path": str(file_path),
            "size": len(content),
            "message": f"Updated file: {path}"
        }
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file."""
        file_path = self.ensure_workspace() / path
        
        if not file_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        
        file_path.unlink()
        return {
            "success": True,
            "path": str(file_path),
            "message": f"Deleted file: {path}"
        }
    
    async def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """List contents of a directory."""
        dir_path = self.ensure_workspace() / path
        
        if not dir_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
        
        if not dir_path.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}
        
        items = []
        for item in dir_path.iterdir():
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0
            })
        
        return {
            "success": True,
            "path": str(dir_path),
            "items": items
        }
    
    # ========== SHELL COMMANDS ==========
    
    async def run_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a shell command safely.
        Only allows whitelisted commands.
        """
        # Parse the command to check if it's allowed
        parts = command.split()
        if not parts:
            return {"success": False, "error": "Empty command"}
        
        base_cmd = parts[0]
        if base_cmd not in ALLOWED_COMMANDS:
            return {
                "success": False, 
                "error": f"Command not allowed: {base_cmd}. Allowed: {ALLOWED_COMMANDS}"
            }
        
        # Set working directory
        work_dir = self.ensure_workspace()
        if cwd:
            work_dir = work_dir / cwd
            if not work_dir.exists():
                work_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            result = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(work_dir)
            )
            
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    # ========== PACKAGE MANAGEMENT ==========
    
    async def install_npm_package(self, package: str, dev: bool = False) -> Dict[str, Any]:
        """Install an NPM package."""
        flag = "--save-dev" if dev else "--save"
        result = await self.run_command(f"npm {flag} {package}")
        return result
    
    async def install_pip_package(self, package: str) -> Dict[str, Any]:
        """Install a Python package."""
        result = await self.run_command(f"pip install {package}")
        return result
    
    # ========== PROJECT SETUP ==========
    
    async def init_project(self, project_type: str, name: str) -> Dict[str, Any]:
        """Initialize a new project of the specified type."""
        project_path = self.ensure_workspace() / name
        
        if project_path.exists():
            return {"success": False, "error": f"Project already exists: {name}"}
        
        if project_type == "nextjs":
            result = await self.run_command(f"npx create-next-app@latest {name} --typescript --tailwind --app --no-src-dir --import-alias \"@/*\" --yes")
        elif project_type == "python":
            project_path.mkdir(parents=True, exist_ok=True)
            # Create basic Python project structure
            (project_path / "requirements.txt").touch()
            (project_path / "README.md").write_text(f"# {name}\n")
            result = {"success": True, "message": f"Created Python project: {name}"}
        elif project_type == "node":
            await self.run_command(f"cd {name} && npm init -y", cwd=".")
            result = {"success": True, "message": f"Created Node.js project: {name}"}
        else:
            return {"success": False, "error": f"Unknown project type: {project_type}"}
        
        return result
    
    # ========== BLUEPRINT PARSING ==========
    
    async def parse_blueprint(self, blueprint_content: str) -> Dict[str, Any]:
        """
        Parse a blueprint markdown document and extract actionable steps.
        Returns a structured list of steps with file paths and content.
        """
        import re
        
        steps = []
        current_step = None
        current_file = None
        current_content = []
        in_code_block = False
        
        lines = blueprint_content.split('\n')
        
        for i, line in enumerate(lines):
            # Detect step headers
            step_match = re.match(r'^##\s*\[?\s*\[?\s*Step\s*(\d+)', line, re.IGNORECASE)
            if step_match:
                if current_step and current_file and current_content:
                    steps.append({
                        "step": current_step,
                        "file": current_file,
                        "content": '\n'.join(current_content)
                    })
                current_step = int(step_match.group(1))
                current_file = None
                current_content = []
                in_code_block = False
            
            # Detect file path in comments or headers
            file_match = re.search(r'(?:file|path)[:\s]+[\'"]?([^\s\'"]+\.(?:ts|tsx|js|jsx|py|md|json|yaml|yml|html|css|scss|sql|sh))[\'"]?', line, re.IGNORECASE)
            if file_match and current_step:
                current_file = file_match.group(1)
            
            # Detect code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block and current_step:
                    # Extract file name from code block language or context
                    if not current_file:
                        lang = line.strip().strip('`')
                        if lang and lang not in ['text', '']:
                            current_file = f"step_{current_step}_{lang}"
                continue
            
            # Collect content
            if current_step and (in_code_block or current_file):
                current_content.append(line)
        
        # Don't forget the last step
        if current_step and current_file and current_content:
            steps.append({
                "step": current_step,
                "file": current_file,
                "content": '\n'.join(current_content)
            })
        
        return {
            "success": True,
            "steps": steps,
            "total_steps": len(steps)
        }


# MCP Server Implementation
class MCPHandler:
    def __init__(self):
        self.executor = SynapseExecutorServer()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            if method == "file/create":
                return await self.executor.create_file(
                    params.get("path", ""),
                    params.get("content", "")
                )
            
            elif method == "file/read":
                return await self.executor.read_file(params.get("path", ""))
            
            elif method == "file/update":
                return await self.executor.update_file(
                    params.get("path", ""),
                    params.get("content", "")
                )
            
            elif method == "file/delete":
                return await self.executor.delete_file(params.get("path", ""))
            
            elif method == "directory/list":
                return await self.executor.list_directory(params.get("path", "."))
            
            elif method == "command/run":
                return await self.executor.run_command(
                    params.get("command", ""),
                    params.get("cwd")
                )
            
            elif method == "package/npm-install":
                return await self.executor.install_npm_package(
                    params.get("package", ""),
                    params.get("dev", False)
                )
            
            elif method == "package/pip-install":
                return await self.executor.install_pip_package(params.get("package", ""))
            
            elif method == "project/init":
                return await self.executor.init_project(
                    params.get("type", ""),
                    params.get("name", "")
                )
            
            elif method == "blueprint/parse":
                return await self.executor.parse_blueprint(params.get("content", ""))
            
            else:
                return {"success": False, "error": f"Unknown method: {method}"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


# Standalone server for testing
if __name__ == "__main__":
    import sys
    
    # Simple CLI for testing
    if len(sys.argv) < 2:
        print("Usage: python server.py <command> [args]")
        print("Commands: create-file, read-file, update-file, delete-file, list-dir, run-command, parse-blueprint")
        sys.exit(1)
    
    handler = MCPHandler()
    command = sys.argv[1]
    
    async def run_cli():
        if command == "create-file":
            result = await handler.handle_request({
                "method": "file/create",
                "params": {
                    "path": sys.argv[2] if len(sys.argv) > 2 else "test.txt",
                    "content": sys.argv[3] if len(sys.argv) > 3 else "Hello, World!"
                }
            })
        elif command == "read-file":
            result = await handler.handle_request({
                "method": "file/read",
                "params": {"path": sys.argv[2] if len(sys.argv) > 2 else "test.txt"}
            })
        elif command == "run-command":
            result = await handler.handle_request({
                "method": "command/run",
                "params": {"command": " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "ls -la"}
            })
        elif command == "parse-blueprint":
            blueprint_path = sys.argv[2] if len(sys.argv) > 2 else "blueprint.md"
            with open(blueprint_path, 'r') as f:
                content = f.read()
            result = await handler.handle_request({
                "method": "blueprint/parse",
                "params": {"content": content}
            })
        else:
            print(f"Unknown command: {command}")
            return
        
        print(json.dumps(result, indent=2))
    
    asyncio.run(run_cli())