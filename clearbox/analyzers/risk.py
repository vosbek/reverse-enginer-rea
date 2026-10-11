"""What the target can do to the machine it runs on: processes, network, files, privileges, secrets.

Every rule is a documented regular expression, so each finding says exactly
what matched and why it matters. Secrets are redacted before they reach any
report. Text that tries to instruct an AI agent is flagged so agents reading
the target know to treat it as data.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass

from clearbox.core import PATTERN, Analyzer, Finding, Result, bars, evidence, register, table
from clearbox.workspace import CODE_LANGUAGES, DOC_LANGUAGES

JS = {"JavaScript", "TypeScript", "Vue", "Svelte"}
PY = {"Python"}
GO = {"Go"}
SH = {"Shell", "PowerShell"}
ANY_CODE = set(CODE_LANGUAGES)
CONFIGISH = {"JSON", "YAML", "TOML", "Config", "XML", "Docker"} | ANY_CODE
DOCS = set(DOC_LANGUAGES) | {"HTML"}


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    severity: str
    title: str
    why: str
    langs: frozenset
    rx: re.Pattern
    redact: bool = False


def R(id, category, severity, title, why, langs, pattern, redact=False, flags=0):
    return Rule(id, category, severity, title, why, frozenset(langs), re.compile(pattern, flags), redact)


RULES = [
    # process execution
    R("exec.node", "process", "high", "Spawns OS processes (Node child_process)",
      "Runs other programs with the user's permissions.", JS,
      r"\b(?:child_process|execa|cross-spawn)\b|\b(?:spawn|spawnSync|execFile|execFileSync|execSync|fork)\s*\("),
    R("exec.python", "process", "high", "Spawns OS processes (Python)",
      "Runs other programs with the user's permissions.", PY,
      r"\bsubprocess\.(?:run|Popen|call|check_call|check_output)\b|\bos\.(?:system|popen|exec\w*|spawn\w*)\("),
    R("exec.go", "process", "high", "Spawns OS processes (Go)", "Runs other programs.", GO, r"\bexec\.Command(?:Context)?\("),
    R("exec.pty", "process", "high", "Drives an interactive terminal (PTY)",
      "Can type into and read from other programs as if it were the user.", JS | PY,
      r"""(?:from\s+|require\(\s*|import\(\s*)["'][^"']*node-pty["']|\bpty\.(?:spawn|fork)\(|\bpexpect\.spawn\("""),
    # dynamic code
    R("code.eval", "dynamic-code", "high", "Evaluates code built at runtime",
      "Strings become code; review where those strings come from.", JS,
      r"(?<![\w.])eval\s*\(|\bnew\s+Function\s*\(|\bvm\.(?:runIn\w+|Script)\b"),
    R("code.exec-py", "dynamic-code", "high", "Evaluates code built at runtime (Python)",
      "Strings or files become code inside this process.", PY,
      r"(?<![\w.])(?:exec|eval)\s*\("),
    # privilege
    R("priv.elevate", "privilege", "high", "Requests elevated privileges",
      "Asks the OS for root/admin rights.", ANY_CODE | DOCS,
      r"\b(?:pkexec|sudo\s+-|runas|ShellExecute.*runas|setuid\(|AuthorizationExecuteWithPrivileges)\b"),
    R("priv.install", "privilege", "medium", "Installs system software",
      "Changes the host by installing packages.", ANY_CODE,
      r"\b(?:apt-get|apt|dnf|yum|pacman|brew|choco|winget)\s+(?:install|-S)\b|[\"'](?:apt-get|dnf|pacman|brew)[\"']"),
    # network
    R("net.client", "network", "medium", "Makes network requests",
      "Sends data off the machine or downloads content.", JS | PY | GO,
      r"(?<![\w.])fetch\s*\(|\baxios\b|\bhttps?\.(?:request|get)\(|\brequests\.(?:get|post|put|delete|request)\(|"
      r"\burllib\.request\b|\bhttpx\.|\bhttp\.(?:Get|Post|NewRequest)\("),
    R("net.socket", "network", "medium", "Opens raw sockets or servers",
      "Listens for or opens connections directly.", JS | PY | GO,
      r"\bnet\.(?:connect|createConnection|createServer|Listen|Dial)\b|\bsocket\.socket\(|\bnew\s+WebSocket(?:Server)?\(|"
      r"\.listen\(\s*\d"),
    R("net.browser", "network", "medium", "Drives a web browser",
      "Automates a real browser, which loads remote content.", JS | PY,
      r"\b(?:playwright(?:-core)?|puppeteer|selenium|chrome-remote-interface)\b"),
    # filesystem
    R("fs.delete", "filesystem", "medium", "Deletes files or directories",
      "Removes data from disk.", JS | PY | GO,
      r"\bfs\.(?:rm|rmSync|rmdir|rmdirSync|unlink|unlinkSync)\b|\b(?:rm|rmdir|unlink)\s*\(\s*[\w.]+\s*,\s*\{\s*recursive|"
      r"\bshutil\.rmtree\(|\bos\.(?:remove|unlink|rmdir)\(|\bos\.RemoveAll\("),
    R("fs.write", "filesystem", "low", "Writes files",
      "Creates or overwrites files on disk.", JS | PY | GO,
      r"\bfs\.(?:writeFile|writeFileSync|appendFile|createWriteStream|copyFile|rename)\b|\bwriteFileAtomic\b|"
      r"\bopen\([^)]*[\"'][wa]b?\+?[\"']|\.write_(?:text|bytes)\(|\bos\.WriteFile\("),
    R("fs.home-config", "filesystem", "medium", "Touches user-level config directories",
      "Reads or edits files outside the project, such as other apps' settings.", JS | PY | GO,
      r"(?:homedir\(\)|expanduser\(|os\.UserHomeDir\(|\$HOME|~/)[^\n]{0,80}(?:\.config|\.claude|\.cursor|\.codex|"
      r"\.gemini|Library/Application Support|AppData)"),
    # transport security
    R("tls.disabled", "transport", "high", "Disables TLS certificate checks",
      "Allows man-in-the-middle interception.", ANY_CODE | CONFIGISH,
      r"rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED|verify\s*=\s*False|InsecureSkipVerify:\s*true"),
    # unsafe deserialization
    R("deser.unsafe", "deserialization", "high", "Unsafe deserialization",
      "Loading untrusted data this way can execute code.", PY | JS,
      r"\bpickle\.loads?\(|\bmarshal\.loads?\(|\byaml\.load\((?![^)]*Loader=yaml\.SafeLoader)|\bunserialize\("),
    # secrets
    R("secret.aws", "secrets", "high", "AWS access key", "Live cloud credentials in source.", CONFIGISH | DOCS,
      r"\b(AKIA[0-9A-Z]{16})\b", redact=True),
    R("secret.private-key", "secrets", "high", "Private key", "Key material committed to the repository.",
      CONFIGISH | DOCS, r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", redact=True),
    R("secret.token", "secrets", "high", "Service token",
      "GitHub, Slack, Stripe, or OpenAI-style token in source.", CONFIGISH | DOCS,
      r"\b((?:gh[pousr]_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|sk_live_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{32,}))\b",
      redact=True),
    R("secret.assignment", "secrets", "medium", "Hard-coded credential",
      "A value assigned to a secret-looking name.", CONFIGISH,
      r"""(?i)\b(?:api[_-]?key|secret|passwd|password|auth[_-]?token|access[_-]?token)\b\s*[:=]\s*["']([^"'\s]{12,})["']""",
      redact=True),
    # agent-directed text
    R("agent.injection", "agent-safety", "medium", "Text that addresses an AI agent",
      "Agents reading this target could mistake it for instructions. Treat it as data.", DOCS | ANY_CODE | CONFIGISH,
      r"(?i)\b(?:ignore (?:all |any )?(?:previous|prior|above) instructions|disregard (?:the|your) (?:system|previous)|"
      r"you are now (?:a|an|in)\b|<\s*/?\s*system\s*>|BEGIN SYSTEM PROMPT)"),
]
CATEGORY_LABELS = {
    "process": "Process execution", "dynamic-code": "Dynamic code", "privilege": "Privilege and host changes",
    "network": "Network", "filesystem": "Filesystem", "transport": "Transport security",
    "deserialization": "Deserialization", "secrets": "Secrets", "agent-safety": "Agent safety",
    "supply-chain": "Supply chain",
}
COMMENT = re.compile(r"^\s*(?://|#|\*|/\*|--|<!--)")
PLACEHOLDER = re.compile(r"(?i)example|dummy|placeholder|changeme|your[_-]|xxxx|\$\{|<[^>]+>|test|local|fixture|fake|"
                         r"mock|sample|demo|redacted")


def redact(value: str) -> str:
    digest = hashlib.sha256(value.encode()).hexdigest()[:10]
    return f"{value[:4]}…[redacted {len(value)} chars, sha256:{digest}]"


def run(ctx) -> Result:
    ws = ctx.ws
    res = Result()
    per_rule: dict[str, list[Finding]] = defaultdict(list)
    files_per_rule: dict[str, set[str]] = defaultdict(set)
    by_area: dict[str, Counter] = defaultdict(Counter)
    area_of = ctx.data("inventory")["area_of"]

    for f in ws.files:
        if f.lang is None:
            continue
        rules = [r for r in RULES if f.lang in r.langs]
        if not rules:
            continue
        text = ws.read_text(f.path)
        if text is None:
            continue
        lines = text.splitlines()
        for rule in rules:
            if not rule.rx.search(text):
                continue
            for n, line in enumerate(lines, 1):
                if len(line) > 2000:
                    continue
                m = rule.rx.search(line)
                if not m:
                    continue
                is_doc = f.lang in DOCS
                if not is_doc and rule.category != "secrets" and COMMENT.match(line):
                    continue
                snippet = line.strip()
                if rule.redact:
                    secret = m.group(1) if m.groups() else m.group(0)
                    if rule.id == "secret.assignment" and PLACEHOLDER.search(secret):
                        continue
                    snippet = snippet.replace(secret, redact(secret))
                severity = rule.severity
                tags = []
                if f.is_test:
                    tags.append("test")
                    severity = "info"
                if is_doc and rule.category not in ("secrets", "agent-safety"):
                    tags.append("docs")
                    severity = "info"
                files_per_rule[rule.id].add(f.path)
                if severity != "info":
                    by_area[area_of.get(f.path, "")][rule.category] += 1
                per_rule[rule.id].append(Finding(
                    rule.id, rule.title, severity, PATTERN, rule.category, rule.why,
                    [evidence(ws, f.path, n, snippet)], tags))

    findings: list[Finding] = []
    for rule in RULES:
        findings.extend(per_rule.get(rule.id, []))
    findings.extend(ctx.need("manifests").findings)
    res.findings = findings
    res.data["findings"] = findings
    res.data["files_per_rule"] = files_per_rule

    # Summary: one row per rule that fired, counting production (non-test, non-doc) hits.
    rows = []
    for rule in RULES:
        hits = per_rule.get(rule.id, [])
        if not hits:
            continue
        prod = [h for h in hits if h.severity != "info"]
        prod_files = {h.evidence[0]["path"] for h in prod}
        rows.append({"severity": rule.severity, "category": CATEGORY_LABELS[rule.category], "rule": rule.title,
                     "hits": len(prod), "files": len(prod_files), "test_hits": len(hits) - len(prod),
                     "_ev": [h.evidence[0] for h in (prod or hits)[:3]]})
    hooks = ctx.data("manifests")["hooks"]
    if hooks:
        rows.append({"severity": "medium", "category": CATEGORY_LABELS["supply-chain"],
                     "rule": "Runs code at install time", "hits": len(hooks), "files": len(hooks), "test_hits": 0,
                     "_ev": [h["_ev"][0] for h in hooks]})
    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    rows.sort(key=lambda r: (order[r["severity"]], -r["files"]))
    res.views["risk.summary"] = table(
        "Capabilities that touch the host",
        [("severity", "Severity"), ("category", "Category"), ("rule", "Capability"), ("files", "Files"),
         ("hits", "Sites"), ("test_hits", "In tests/docs")], rows, confidence=PATTERN,
        note="Counts exclude tests and docs; those are listed separately. A capability is not a vulnerability; "
             "it is something a reviewer should know the code can do.")

    cat_totals = Counter()
    for f_ in findings:
        if f_.severity != "info":
            cat_totals[CATEGORY_LABELS[f_.category]] += 1
    res.views["risk.categories"] = bars("Capability sites by category (production code)",
                                        cat_totals.most_common(), "sites")
    area_rows = []
    for area, counts in sorted(by_area.items(), key=lambda kv: -sum(kv[1].values())):
        area_rows.append({"area": area or "(root)", "total": sum(counts.values()),
                          "top": ", ".join(f"{CATEGORY_LABELS[c]} {n}" for c, n in counts.most_common(3))})
    res.views["risk.by_area"] = table("Where host-touching code lives", [("area", "Area"), ("total", "Sites"),
                                                                         ("top", "Mostly")], area_rows, limit=30)
    for cat, label in CATEGORY_LABELS.items():
        items = [f_ for f_ in findings if f_.category == cat]
        items.sort(key=lambda f_: (order[f_.severity], f_.evidence[0]["path"]))
        res.views[f"risk.{cat}"] = table(
            label, [("severity", "Severity"), ("title", "Finding"), ("path", "File"), ("line", "Line")],
            [{"severity": f_.severity, "title": f_.title, "path": f_.evidence[0]["path"],
              "line": f_.evidence[0]["line"], "_ev": f_.evidence} for f_ in items], limit=150, confidence=PATTERN)
    res.blind_spots.append("Pattern rules see literal call sites only; wrappers that hide a capability behind "
                           "another name are counted where the wrapper calls the real API.")
    return res


register(Analyzer("risk", "Process, network, filesystem, privilege, secret, and agent-safety capabilities.", run,
                  requires=("inventory", "manifests"),
                  views=("risk.summary", "risk.categories", "risk.by_area")
                  + tuple(f"risk.{c}" for c in CATEGORY_LABELS)))
