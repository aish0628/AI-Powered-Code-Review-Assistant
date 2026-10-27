"""Step 1: Static analyzer (rules + per-function metrics). Standard library only."""
import ast, json, re, sys
from dataclasses import dataclass, asdict

@dataclass
class Finding:
    line: int
    severity: str      # high | medium | low
    rule: str
    message: str
    function: str = ""

@dataclass
class FuncMetrics:
    name: str
    line: int
    loc: int
    complexity: int
    max_nesting: int
    n_params: int
    has_docstring: bool
    n_returns: int
    n_calls: int

SECRET_RE = re.compile(r"(password|passwd|secret|api_?key|token)", re.I)
SQL_RE = re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", re.I)
BRANCH = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With,
          ast.BoolOp, ast.IfExp, ast.comprehension)
NEST = (ast.If, ast.For, ast.While, ast.Try, ast.With)

def _nesting(node, depth=0):
    best = depth
    for ch in ast.iter_child_nodes(node):
        d = depth + 1 if isinstance(ch, NEST) else depth
        best = max(best, _nesting(ch, d))
    return best

def function_metrics(fn):
    body_nodes = list(ast.walk(fn))
    end = getattr(fn, "end_lineno", fn.lineno)
    return FuncMetrics(
        name=fn.name, line=fn.lineno, loc=end - fn.lineno + 1,
        complexity=1 + sum(isinstance(n, BRANCH) for n in body_nodes),
        max_nesting=_nesting(fn),
        n_params=len(fn.args.args) + len(fn.args.kwonlyargs),
        has_docstring=ast.get_docstring(fn) is not None,
        n_returns=sum(isinstance(n, ast.Return) for n in body_nodes),
        n_calls=sum(isinstance(n, ast.Call) for n in body_nodes),
    )

def _is_sql_concat(node):
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return any(isinstance(s, ast.Constant) and isinstance(s.value, str)
                   and SQL_RE.search(s.value) for s in ast.walk(node))
    if isinstance(node, ast.JoinedStr):
        return any(isinstance(s, ast.Constant) and isinstance(s.value, str)
                   and SQL_RE.search(s.value) for s in node.values)
    return False

def analyze(source: str):
    """Returns (findings, metrics). Raises SyntaxError on invalid code."""
    tree = ast.parse(source)
    findings, metrics = [], []
    owner = {}  # node id -> function name
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            m = function_metrics(fn)
            metrics.append(m)
            for n in ast.walk(fn):
                owner[id(n)] = fn.name
            # metric-based rules
            if m.complexity > 10:
                findings.append(Finding(fn.lineno, "medium", "high-complexity",
                    f"Cyclomatic complexity {m.complexity} (>10). Split the function.", fn.name))
            if m.loc > 50:
                findings.append(Finding(fn.lineno, "low", "long-function",
                    f"{m.loc} lines long (>50).", fn.name))
            if m.max_nesting > 3:
                findings.append(Finding(fn.lineno, "medium", "deep-nesting",
                    f"Nesting depth {m.max_nesting} (>3). Use early returns.", fn.name))
            if m.n_params > 5:
                findings.append(Finding(fn.lineno, "low", "many-params",
                    f"{m.n_params} parameters (>5).", fn.name))
            if not m.has_docstring:
                findings.append(Finding(fn.lineno, "low", "missing-docstring",
                    "Function has no docstring.", fn.name))
            for d in fn.args.defaults + fn.args.kw_defaults:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    findings.append(Finding(fn.lineno, "medium", "mutable-default",
                        "Mutable default argument.", fn.name))
    # node-based rules
    for n in ast.walk(tree):
        f = owner.get(id(n), "")
        ln = getattr(n, "lineno", 0)
        if isinstance(n, ast.ExceptHandler):
            if n.type is None:
                findings.append(Finding(ln, "medium", "bare-except",
                    "Bare 'except:' hides errors. Catch specific exceptions.", f))
            if len(n.body) == 1 and isinstance(n.body[0], ast.Pass):
                findings.append(Finding(ln, "medium", "swallowed-exception",
                    "Exception silently ignored.", f))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("eval", "exec"):
            findings.append(Finding(ln, "high", "dynamic-exec",
                f"Use of {n.func.id}() is dangerous.", f))
        elif isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) \
                and isinstance(n.value.value, str) and n.value.value:
            for t in n.targets:
                if isinstance(t, ast.Name) and SECRET_RE.search(t.id):
                    findings.append(Finding(ln, "high", "hardcoded-secret",
                        f"Hardcoded secret in '{t.id}'. Use env vars.", f))
        if _is_sql_concat(n):
            findings.append(Finding(ln, "high", "sql-injection",
                "SQL built with string formatting. Use parameterized queries.", f))
    # dedupe
    seen, out = set(), []
    for x in sorted(findings, key=lambda x: (x.line, x.rule)):
        k = (x.line, x.rule)
        if k not in seen:
            seen.add(k); out.append(x)
    return out, metrics

if __name__ == "__main__":
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    fs, ms = analyze(src)
    print(json.dumps({"findings": [asdict(f) for f in fs],
                      "metrics": [asdict(m) for m in ms]}, indent=2))