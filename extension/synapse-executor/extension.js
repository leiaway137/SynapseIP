/**
 * SynapseIP Blueprint Executor Extension for VS Code
 * Allows users to read SynapseIP blueprints and execute steps with approval
 */

const vscode = require('vscode');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

let outputChannel;
let statusBarItem;

function activate(context) {
    outputChannel = vscode.window.createOutputChannel('SynapseIP Executor');
    
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = 'SynapseIP Ready';
    statusBarItem.command = 'synapseExecutor.showStatus';
    statusBarItem.show();

    // Register commands
    const subscriptions = [
        // Open blueprint from URL
        vscode.commands.registerCommand('synapseExecutor.openBlueprint', async () => {
            const url = await vscode.window.showInputBox({
                prompt: 'Enter SynapseIP Blueprint URL or select from recent',
                placeHolder: 'http://192.168.1.174:8002/api/architect/blueprint/1'
            });
            
            if (url) {
                await fetchAndOpenBlueprint(url);
            }
        }),

        // Parse current document as blueprint
        vscode.commands.registerCommand('synapseExecutor.parseCurrentDocument', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active document to parse');
                return;
            }
            
            const content = editor.document.getText();
            const steps = parseBlueprintSteps(content);
            await showBlueprintSteps(steps);
        }),

        // Execute next step
        vscode.commands.registerCommand('synapseExecutor.executeNextStep', async (step) => {
            if (!step) {
                vscode.window.showWarningMessage('No step selected');
                return;
            }
            await executeStep(step);
        }),

        // Execute all steps with confirmation
        vscode.commands.registerCommand('synapseExecutor.executeAllSteps', async (steps) => {
            if (!steps || steps.length === 0) {
                vscode.window.showWarningMessage('No steps to execute');
                return;
            }
            await executeAllSteps(steps);
        }),

        // Show status
        vscode.commands.registerCommand('synapseExecutor.showStatus', () => {
            outputChannel.show();
            outputChannel.appendLine('SynapseIP Blueprint Executor');
            outputChannel.appendLine('Version: 1.0.0');
            outputChannel.appendLine('Workspace: ' + vscode.workspace.workspaceFolder?.uri.fsPath || 'No workspace');
        }),

        // Create file from step
        vscode.commands.registerCommand('synapseExecutor.createFileFromStep', async (step) => {
            if (!step || !step.file || !step.content) {
                vscode.window.showWarningMessage('Invalid step');
                return;
            }
            await createFileFromStep(step);
        }),

        // Run command from step
        vscode.commands.registerCommand('synapseExecutor.runCommand', async (command) => {
            if (!command) {
                vscode.window.showWarningMessage('No command specified');
                return;
            }
            await runShellCommand(command);
        })
    ];

    context.subscriptions.push(...subscriptions, outputChannel, statusBarItem);
    
    outputChannel.appendLine('SynapseIP Blueprint Executor activated');
}

function deactivate() {
    if (outputChannel) {
        outputChannel.dispose();
    }
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}

// ========== BLUEPRINT PARSING ==========

function parseBlueprintSteps(content) {
    const steps = [];
    const lines = content.split('\n');
    let currentStep = null;
    let currentFile = null;
    let currentContent = [];
    let inCodeBlock = false;
    let codeBlockLang = '';

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Detect step headers (## Step X: Title or ## <label...> Step X: Title)
        const stepMatch = line.match(/^##\s*\[?\s*\[?\s*Step\s*(\d+)[\.\:]?\s*:?\s*(.+)?/i);
        const htmlStepMatch = line.match(/data-idx=['"]?(\d+)['"]?\s*>\s*Step\s*(\d+)[\.\:]?\s*:?\s*([^<]+)/i);
        
        if (stepMatch || htmlStepMatch) {
            // Save previous step
            if (currentStep && currentContent.length > 0) {
                steps.push({
                    step: currentStep,
                    file: currentFile,
                    content: currentContent.join('\n').trim(),
                    type: 'text'
                });
            }
            
            // Handle both plain text and HTML checkbox formats
            if (htmlStepMatch) {
                currentStep = {
                    number: parseInt(htmlStepMatch[2]),
                    title: htmlStepMatch[3].trim() || 'Untitled'
                };
            } else {
                currentStep = {
                    number: parseInt(stepMatch[1]),
                    title: stepMatch[2] || 'Untitled'
                };
            }
            currentFile = null;
            currentContent = [];
            inCodeBlock = false;
            continue;
        }
        
        // Detect file references
        const fileMatch = line.match(/(?:file|path)[:\s]+['"]?([^\s'"]+\.(?:ts|tsx|js|jsx|py|md|json|yaml|yml|html|css|scss|sql|sh|txt))['"]?/i);
        if (fileMatch && currentStep) {
            currentFile = fileMatch[1];
        }
        
        // Detect code blocks
        if (line.trim().startsWith('```')) {
            if (!inCodeBlock) {
                inCodeBlock = true;
                codeBlockLang = line.trim().replace('```', '').trim() || 'text';
                if (currentStep && !currentFile) {
                    currentFile = `step_${currentStep.number}_${codeBlockLang}`;
                }
            } else {
                inCodeBlock = false;
                if (currentStep && currentContent.length > 0) {
                    steps.push({
                        step: currentStep.number,
                        title: currentStep.title,
                        file: currentFile,
                        content: currentContent.join('\n').trim(),
                        language: codeBlockLang,
                        type: 'code'
                    });
                    currentContent = [];
                    currentFile = null;
                }
            }
            continue;
        }
        
        // Collect content
        if (currentStep) {
            if (inCodeBlock) {
                currentContent.push(line);
            } else if (line.trim()) {
                currentContent.push(line);
            }
        }
    }
    
    // Don't forget the last step
    if (currentStep && currentContent.length > 0) {
        steps.push({
            step: currentStep.number,
            title: currentStep.title,
            file: currentFile,
            content: currentContent.join('\n').trim(),
            type: currentFile ? 'code' : 'text'
        });
    }
    
    return steps;
}

// ========== NETWORK OPERATIONS ==========

async function fetchAndOpenBlueprint(url) {
    statusBarItem.text = 'SynapseIP Loading...';
    
    try {
        // VS Code extensions can't use fetch() directly for external URLs
        // Use http/https module instead
        const http = require('http');
        const https = require('https');
        const { URL } = require('url');
        
        const parsedUrl = new URL(url);
        const lib = parsedUrl.protocol === 'https:' ? https : http;
        
        const content = await new Promise((resolve, reject) => {
            lib.get(url, (res) => {
                if (res.statusCode !== 200) {
                    reject(new Error(`Request failed. Status code: ${res.statusCode}`));
                    return;
                }
                
                let data = '';
                res.on('data', (chunk) => { data += chunk; });
                res.on('end', () => resolve(data));
            }).on('error', reject);
        });
        
        outputChannel.appendLine('Successfully fetched blueprint from: ' + url);
        const steps = parseBlueprintSteps(content);
        outputChannel.appendLine('Found ' + steps.length + ' steps in blueprint');
        await showBlueprintSteps(steps);
        
        statusBarItem.text = 'SynapseIP Ready';
    } catch (error) {
        outputChannel.appendLine('Error fetching blueprint: ' + error.message);
        vscode.window.showErrorMessage('Failed to fetch blueprint: ' + error.message);
        statusBarItem.text = 'SynapseIP Error';
    }
}

// ========== UI OPERATIONS ==========

async function showBlueprintSteps(steps) {
    if (steps.length === 0) {
        vscode.window.showInformationMessage('No steps found in blueprint');
        return;
    }
    
    outputChannel.appendLine(`Found ${steps.length} steps in blueprint`);
    
    // Show as quick pick
    const options = steps.map((step, index) => ({
        label: `Step ${step.number}: ${step.title || 'Untitled'}`,
        description: step.file || 'Text content',
        detail: step.content?.substring(0, 50) + '...' || 'No content',
        step: step
    }));
    
    const selected = await vscode.window.showQuickPick(options, {
        placeHolder: 'Select a step to execute',
        canPickMany: false
    });
    
    if (selected) {
        await executeStep(selected.step);
    }
}

// ========== FILE OPERATIONS ==========

async function createFileFromStep(step) {
    if (!step.file || !step.content) {
        vscode.window.showWarningMessage('Step has no file or content');
        return;
    }
    
    const workspacePath = vscode.workspace.workspaceFolder?.uri.fsPath;
    if (!workspacePath) {
        vscode.window.showWarningMessage('No workspace folder open');
        return;
    }
    
    const filePath = path.join(workspacePath, step.file);
    const dirPath = path.dirname(filePath);
    
    // Ensure directory exists
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
    
    // Ask for confirmation
    const confirm = await vscode.window.showInformationMessage(
        `Create file: ${step.file} (${step.content.length} chars)`,
        { modal: true },
        'Create',
        'Cancel'
    );
    
    if (confirm !== 'Create') {
        return;
    }
    
    // Write file
    fs.writeFileSync(filePath, step.content, 'utf8');
    
    outputChannel.appendLine(`Created file: ${filePath}`);
    vscode.window.showInformationMessage(`Created: ${step.file}`);
    
    // Open the file
    const document = await vscode.workspace.openTextDocument(filePath);
    await vscode.window.showTextDocument(document);
}

// ========== COMMAND EXECUTION ==========

async function runShellCommand(command) {
    const workspacePath = vscode.workspace.workspaceFolder?.uri.fsPath;
    if (!workspacePath) {
        vscode.window.showWarningMessage('No workspace folder open');
        return;
    }
    
    // Security check - only allow safe commands
    const allowedCommands = ['npm', 'npx', 'pip', 'pip3', 'python', 'python3', 'node', 'git', 'mkdir', 'touch', 'rm', 'cp', 'mv'];
    const baseCommand = command.split(' ')[0];
    
    if (!allowedCommands.includes(baseCommand)) {
        vscode.window.showErrorMessage(`Command not allowed: ${baseCommand}`);
        return;
    }
    
    const confirm = await vscode.window.showWarningMessage(
        `Run command: ${command}`,
        { modal: true },
        'Run',
        'Cancel'
    );
    
    if (confirm !== 'Run') {
        return;
    }
    
    outputChannel.appendLine(`Running: ${command}`);
    statusBarItem.text = 'SynapseIP Running...';
    
    exec(command, { cwd: workspacePath }, (error, stdout, stderr) => {
        if (error) {
            outputChannel.appendLine(`Error: ${error.message}`);
            vscode.window.showErrorMessage(`Command failed: ${error.message}`);
        }
        if (stdout) {
            outputChannel.appendLine(stdout);
        }
        if (stderr) {
            outputChannel.appendLine(stderr);
        }
        
        statusBarItem.text = 'SynapseIP Ready';
        outputChannel.show();
    });
}

async function executeStep(step) {
    if (!step) {
        return;
    }
    
    const actions = [];
    
    if (step.type === 'code' || step.file) {
        actions.push({
            label: 'Create File',
            fn: () => createFileFromStep(step)
        });
    }
    
    if (step.content?.includes('npm install') || step.content?.includes('pip install')) {
        const match = step.content.match(/(npm|pip)(?:3)?\s+install\s+([^\n]+)/);
        if (match) {
            actions.push({
                label: 'Install Packages',
                fn: () => runShellCommand(match[0])
            });
        }
    }
    
    if (actions.length === 0) {
        vscode.window.showInformationMessage('No executable actions in this step');
        return;
    }
    
    const selectedAction = await vscode.window.showQuickPick(
        actions.map(a => a.label),
        { placeHolder: 'Choose action' }
    );
    
    if (selectedAction) {
        const action = actions.find(a => a.label === selectedAction);
        await action.fn();
    }
}

async function executeAllSteps(steps) {
    const confirm = await vscode.window.showWarningMessage(
        `Execute ${steps.length} steps? This will create/modify files.`,
        { modal: true },
        'Execute All',
        'Cancel'
    );
    
    if (confirm !== 'Execute All') {
        return;
    }
    
    statusBarItem.text = 'SynapseIP Executing...';
    
    for (const step of steps) {
        outputChannel.appendLine(`\n=== Executing Step ${step.number}: ${step.title || 'Untitled'} ===`);
        
        if (step.type === 'code' && step.file) {
            await createFileFromStep(step);
        }
        
        // Small delay between steps
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    statusBarItem.text = 'SynapseIP Complete';
    vscode.window.showInformationMessage(`Completed ${steps.length} steps`);
}

module.exports = {
    activate,
    deactivate
};