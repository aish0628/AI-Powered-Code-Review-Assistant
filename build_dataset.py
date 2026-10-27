"""Step 3: Build a labeled dataset from bug-fix commits of a local git repo.
Before-fix function = buggy (1). After-fix function = clean (0)."""
import ast, csv, re, subprocess, sys
from feature_extractor import extract_features, FEATURE_NAMES

FIX_RE = re.compile(r"\b(fix|fixes|fixed|bug|bugfix|patch|crash|error)\b", re.I)

def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True,
                       text=True, errors="replace")
    return r.stdout if r.returncode == 0 else ""

def bugfix_commits(repo, limit):
    out = git(repo, "log", "--no-merges", "-n", str(limit), "--pretty=%H%x09%s")
    for line in out.splitlines():
        sha, _, msg = line.partition("\t")
        if FIX_RE.search(msg):
            yield sha, msg

def modified_py_files(repo, sha):
    out = git(repo, "diff-tree", "--no-commit-id", "--name-only",
              "--diff-filter=M", "-r", sha)
    return [p for p in out.splitlines() if p.endswith(".py")]

def func_bodies(src):
    """name -> normalized source, so formatting-only changes are ignored."""
    bodies = {}
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bodies[n.name] = ast.unparse(n)
    return bodies

def rows_for_commit(repo, sha, path):
    before = git(repo, "show", f"{sha}~1:{path}")
    after = git(repo, "show", f"{sha}:{path}")
    if not before or not after:
        return []
    try:
        b_bod, a_bod = func_bodies(before), func_bodies(after)
        changed = {n for n in b_bod if n in a_bod and b_bod[n] != a_bod[n]}
        b_rows = {r["function"]: r for r in extract_features(before, path)}
        a_rows = {r["function"]: r for r in extract_features(after, path)}
    except SyntaxError:
        return []
    out = []
    for n in changed:
        if n in b_rows and n in a_rows:
            out.append({**b_rows[n], "commit": sha[:8], "label": 1})
            out.append({**a_rows[n], "commit": sha[:8], "label": 0})
    return out

def build(repo, out_csv, limit=500):
    rows = []
    for sha, msg in bugfix_commits(repo, limit):
        for path in modified_py_files(repo, sha):
            rows += rows_for_commit(repo, sha, path)
    if not rows:
        print("No bug-fix function pairs found."); return
    cols = ["file", "function", "commit"] + FEATURE_NAMES + ["label"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    buggy = sum(r["label"] for r in rows)
    print(f"{len(rows)} rows ({buggy} buggy, {len(rows)-buggy} clean) -> {out_csv}")

if __name__ == "__main__":
    # usage: python build_dataset.py <repo_path> <out.csv> [max_commits]
    build(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 500)


    