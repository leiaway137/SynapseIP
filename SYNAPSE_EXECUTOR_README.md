# SynapseIP Blueprint Executor

This package provides tools for SynapseIP to self-execute blueprint plans, enabling automated file creation, package installation, and project setup.

## Components

### 1. MCP Server (`synapse-executor-mcp/`)

A Model Context Protocol (MCP) server that provides tools for:

- **File Operations**: Create, read, update, delete files
- **Shell Commands**: Run safe, whitelisted commands
- **Package Management**: Install NPM and pip packages
- **Project Initialization**: Create new Next.js, Python, or Node.js projects
- **Blueprint Parsing**: Parse SynapseIP blueprints into actionable steps

#### Available MCP Tools

| Tool | Description |
|------|-------------|
| `file/create` | Create a new file with content |
| `file/read` | Read file contents |
| `file/update` | Update existing file |
| `file/delete` | Delete a file |
| `directory/list` | List directory contents |
| `command/run` | Run shell commands (whitelisted) |
| `package/npm-install` | Install NPM packages |
| `package/pip-install` | Install Python packages |
| `project/init` | Initialize new projects |
| `blueprint/parse` | Parse blueprint markdown into steps |

#### Configuration

Add to your MCP config file:

```json
{
  "mcpServers": {
    "synapse-executor": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}/synapse-executor-mcp",
      "env": {
        "SYNAPSE_WORKSPACE": "${workspaceFolder}"
      }
    }
  }
}
```

#### Usage Example

```python
# Test the server
python server.py create-file test.txt "Hello World"
python server.py run-command "ls -la"
python server.py parse-blueprint blueprint.md
```

### 2. VS Code Extension (`extension/synapse-executor/`)

A VS Code extension for manually reviewing and executing blueprint steps.

#### Features

- **Open Blueprint**: Fetch blueprints from SynapseIP server
- **Parse Document**: Parse current document as blueprint
- **Execute Steps**: Create files and run commands with approval
- **Status Bar**: Shows execution status

#### Commands

| Command | Description |
|---------|-------------|
| `SynapseIP: Open Blueprint from URL` | Fetch blueprint from SynapseIP |
| `SynapseIP: Parse Current Document as Blueprint` | Parse active editor |
| `SynapseIP: Execute Next Step` | Execute selected step |
| `SynapseIP: Execute All Steps` | Execute all steps with confirmation |
| `SynapseIP: Show Status` | Show output channel |

#### Installation

1. Open VS Code
2. Run `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Select `Extensions: Install from VSIX`
4. Select the packaged `.vsix` file

Or for development:

```bash
cd extension/synapse-executor
npm install
npm run package
# Then install the .vsix file
```

## Workflow

### Manual Flow (VS Code Extension)

1. Generate blueprint in SynapseIP (http://192.168.1.174:8002)
2. Open VS Code extension
3. Select "Open Blueprint from URL"
4. Review each step
5. Approve file creation/commands individually

### Automated Flow (MCP Server)

1. Generate blueprint in SynapseIP
2. Use MCP tools to parse blueprint
3. Programmatically execute steps via MCP API
4. Monitor execution results

## Security

- **Whitelisted Commands**: Only safe commands allowed (npm, pip, python, git, etc.)
- **User Approval**: VS Code extension requires confirmation for all actions
- **Workspace Isolation**: Operations confined to workspace directory
- **No Dangerous Operations**: No `rm -rf`, `sudo`, or network operations

## Development

### MCP Server

```bash
cd synapse-executor-mcp
python server.py list-dir  # Test
```

### VS Code Extension

```bash
cd extension/synapse-executor
npm install
npm run package  # Creates .vsix
```

## Future Enhancements

1. **Auto-detect dependencies** from blueprints
2. **Sandboxed execution** in Docker containers
3. **Rollback support** for failed steps
4. **Progress tracking** and checkpointing
5. **Multi-language** blueprint parsing (more robust)

## License

MIT