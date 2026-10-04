# Forge ⚒️

**Forge** is a local-first AI coding agent built from scratch using Python and Ollama.

It allows an LLM to interact with a real software workspace through tools, inspect source code, modify files, execute commands, and iteratively work on coding tasks.

## Features

* 🤖 Local LLM inference through Ollama
* 📂 Workspace and file inspection
* 📖 Source-code reading
* ✏️ Targeted file editing
* 📝 File creation and replacement
* 💻 Shell command execution
* 🔄 Iterative agent execution
* 🧠 Agent execution state
* ⏱️ Maximum iteration limit
* ✅ Test and command verification
* 🎯 Explicit task completion

## How It Works

Forge gives the LLM access to a small set of tools:

```text
                    User
                      │
                      ▼
                ┌──────────┐
                │  Forge   │
                │   Agent  │
                └────┬─────┘
                     │
              LLM tool calls
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
   File Tools    Edit Tools    Shell Tools
       │             │             │
       └─────────────┼─────────────┘
                     ▼
                  Workspace
```

For a typical coding task, Forge can follow a workflow such as:

```text
Inspect → Read → Modify → Test → Diagnose → Fix → Verify
```

The agent can stop before reaching the maximum iteration count when it determines that the task has been completed.

## Available Tools

### `list_files`

Lists files and directories inside the workspace.

```text
list_files(path)
```

### `read_file`

Reads a UTF-8 text file.

```text
read_file(path)
```

### `write_file`

Creates or completely replaces a text file.

```text
write_file(path, content)
```

### `edit_file`

Replaces a specific section of text in an existing file.

```text
edit_file(path, old, new)
```

### `run_command`

Runs a shell command inside the workspace.

```text
run_command(command, timeout)
```

This can be used for running tests, linters, development commands, or other project-specific commands.

### `finish`

Marks the task as complete after the agent has verified its work.

```text
finish(summary, verification)
```

## Requirements

* Python 3.10+
* Ollama
* An Ollama-compatible model
* Linux or WSL recommended

## Installation

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

Make sure Ollama is installed and running.

Check the available models:

```bash
ollama list
```

## Ollama Configuration

Forge uses the Ollama Python client.

If Ollama is running on the host machine while Forge is running inside WSL, configure the Ollama endpoint accordingly.

For example:

```bash
export OLLAMA_HOST="http://$(ip route | grep default | awk '{print $3}'):11434"
```

Verify the connection:

```bash
python -c "import ollama; print(ollama.list())"
```

## Running Forge

Start Forge with an Ollama model:

```bash
python -m forge.cli --model YOUR_MODEL
```

For example:

```bash
python -m forge.cli --model gemma4:cloud
```

You should see:

```text
Starting Forge...
Connecting to Ollama with model: gemma4:cloud
Forge is ready.
Type 'exit' to quit.

forge ›
```

## Example

Once Forge is running, describe the coding task:

```text
forge › Change sandbox_project/hello.py so that it takes a name as input and test if it works.
```

Forge can then inspect the project, modify the file, execute the program, and use the command output to determine whether the change works.

Another example:

```text
forge › Fix the failing tests in this project and verify that everything passes.
```

## Project Structure

```text
forge/
├── agent.py       # Agent loop, system prompt and tool definitions
├── state.py       # Agent execution state
├── tools.py       # File and command execution tools
├── llm.py         # Ollama integration
└── cli.py         # Command-line interface

requirements.txt
README.md
```

## Configuration

The model is selected from the command line:

```bash
python -m forge.cli --model MODEL_NAME
```

The Ollama connection is controlled through `OLLAMA_HOST`.

## Current Version

**Forge v0.1**

Forge v0.1 is a functional coding-agent MVP focused on LLM tool calling, workspace interaction, command execution, iterative execution, and verification.

NOTE: This is still in development, the agent may execute harmful commands since validation is lacking, use at your own risk.