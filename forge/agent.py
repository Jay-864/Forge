from .llm import OllamaLLM
from .state import AgentState
from .tools import (
    list_files,
    read_file,
    write_file,
    edit_file,
    run_command,
)


SYSTEM_PROMPT = """
You are Forge, an autonomous local coding agent.

Your job is to modify software inside the current workspace
to satisfy the user's request.

You have access to tools for:
- inspecting files
- reading source code
- editing files
- writing files
- running commands

Follow this workflow:

1. Understand the user's request.
2. Inspect the relevant parts of the repository.
3. Make a concrete implementation plan.
4. Modify the minimum necessary files.
5. Run appropriate tests or verification commands.
6. If verification fails, inspect the error.
7. Fix the implementation.
8. Run verification again.
9. Continue until the task is complete or the iteration limit is reached.

Important rules:

- Never claim a task is complete without verification when verification is possible.
- Do not modify unrelated files.
- Prefer targeted edits over rewriting entire files.
- Inspect code before modifying it.
- When a command fails, use its output to diagnose the problem.
- Do not repeatedly perform the same failed action.

Command failures are observations, not necessarily agent failures.

If tests fail:
1. Read the failure.
2. Determine the cause.
3. Inspect relevant code.
4. Make a correction.
5. Run the test again.

Completion rules:

- Do not finish merely because you believe the code is correct.
- Verify your changes whenever possible.
- Use tests, linters, builds, or another appropriate command.
- Only call the finish tool after verification succeeds.
- If verification fails, diagnose the failure and continue working.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path relative to the workspace.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or completely replace a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                    },
                    "content": {
                        "type": "string",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace one specific piece of text in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                    },
                    "old": {
                        "type": "string",
                    },
                    "new": {
                        "type": "string",
                    },
                },
                "required": ["path", "old", "new"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command inside the current workspace. "
                "Use this to run tests, inspect code, or execute development commands."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute.",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Maximum execution time in seconds.",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": (
                "Finish the current task after verifying that the requested "
                "work is complete. Only use this when the task has been "
                "successfully implemented and verified."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Brief summary of what was completed.",
                    },
                    "verification": {
                        "type": "string",
                        "description": "Describe how the work was verified.",
                    },
                },
                "required": ["summary", "verification"],
            },
        },
    },
]


class Agent:
    def __init__(self, model: str):
        self.llm = OllamaLLM(model)

    def run(self, task: str):
        state = AgentState(task=task)

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": task,
            },
        ]

        while state.next_iteration():

            print(
                f"[Forge] Iteration "
                f"{state.iteration}/{state.max_iterations}"
            )

            response = self.llm.client.chat(
                model=self.llm.model,
                messages=self.messages,
                tools=TOOLS,
            )

            message = response.message

            self.messages.append(message)

            # Model decided the task is complete.
            if not message.tool_calls:
                state.finished = True
                return message.content

            for call in message.tool_calls:
                name = call.function.name
                arguments = call.function.arguments

                if name == "list_files":
                    path = arguments.get("path", ".")

                    state.files_read.add(path)

                    result = list_files(path)

                elif name == "read_file":
                    path = arguments["path"]

                    state.files_read.add(path)

                    result = read_file(path)

                elif name == "write_file":
                    path = arguments["path"]

                    state.files_changed.add(path)

                    result = write_file(
                        path,
                        arguments["content"],
                    )

                elif name == "edit_file":
                    path = arguments["path"]

                    state.files_changed.add(path)

                    result = edit_file(
                        path,
                        arguments["old"],
                        arguments["new"],
                    )

                elif name == "run_command":
                    command = arguments["command"]

                    state.commands_run.append(command)

                    result = run_command(
                        command,
                        arguments.get("timeout", 30),
                    )
                
                elif name == "finish":
                    state.finished = True

                    return (
                        f"{arguments['summary']}\n\n"
                        f"Verification: {arguments['verification']}"
                    )

                else:
                    result = f"Unknown tool: {name}"

                self.messages.append(
                    {
                        "role": "tool",
                        "content": result,
                    }
                )

        return (
            f"Agent stopped after {state.max_iterations} "
            "iterations without completing the task."
        )