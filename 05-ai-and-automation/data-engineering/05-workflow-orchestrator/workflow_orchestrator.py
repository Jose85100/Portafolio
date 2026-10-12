"""Local DAG runner with idempotent checkpoints and bounded retries."""
import json
import os
import tempfile
from pathlib import Path

class Workflow:
    def __init__(self):
        self.tasks = {}

    def add(self, name, fn, dependencies=(), retries=0):
        if not name or name in self.tasks or retries < 0 or not callable(fn):
            raise ValueError("invalid task")
        self.tasks[name] = (fn, tuple(dependencies), retries)

    def order(self):
        state, ordered = {}, []
        def visit(name):
            if name not in self.tasks:
                raise ValueError("unknown dependency: " + name)
            if state.get(name) == 1:
                raise ValueError("cycle detected")
            if state.get(name) == 2:
                return
            state[name] = 1
            for dep in self.tasks[name][1]:
                visit(dep)
            state[name] = 2
            ordered.append(name)
        for name in self.tasks:
            visit(name)
        return ordered

    def run(self, checkpoint, run_id):
        if not run_id:
            raise ValueError("run_id required")
        path = Path(checkpoint)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        done = set(state.get(run_id, []))
        for name in self.order():
            if name in done:
                continue
            fn, _, retries = self.tasks[name]
            for attempt in range(retries + 1):
                try:
                    fn()
                    break
                except Exception:
                    if attempt == retries:
                        raise
            done.add(name)
            state[run_id] = sorted(done)
            tmp = None
            try:
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                                 delete=False, prefix=".checkpoint-") as f:
                    tmp = f.name
                    json.dump(state, f, sort_keys=True)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp, path)
            finally:
                if tmp and os.path.exists(tmp):
                    os.unlink(tmp)
        return sorted(done)
