from dataclasses import dataclass, field


@dataclass
class AgentState:
    task: str
    iteration: int = 0
    max_iterations: int = 15

    files_read: set[str] = field(default_factory=set)
    files_changed: set[str] = field(default_factory=set)
    commands_run: list[str] = field(default_factory=list)

    tests_passed: bool = False
    finished: bool = False

    def next_iteration(self) -> bool:
        self.iteration += 1
        return self.iteration <= self.max_iterations