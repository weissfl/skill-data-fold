#!/usr/bin/env python3
# check_draft.py — deterministic gate for the data-fold draft file.
# Source of truth: SKILL.md, section state_shape ("Draft form", "Canonical formats").
# Sync convention: a change to those spec sections requires a paired change to
# this file's rules in the same commit. Rules: 30 (25 FAIL, 5 WARN).
# Usage: python check_draft.py <task-dir | draft-file>
# Exit codes: 0 — no FAIL findings; 1 — at least one FAIL or a fatal error;
#             2 — usage error.
# Cross-platform: Python 3.7+ stdlib only (pathlib, re, xml.etree, datetime).
#
# Rule traceability (rule -> SKILL.md anchor); keep in sync with spec edits:
#   R01 state_shape: Storage              R02 operational (UTF-8 discipline)
#   R03 state_shape: Artifacts            R04 Draft form: artifacts index
#   R05 Draft form + protocol 10          R06 state_shape: Artifacts
#   R07 Draft form (well-formed XML)      R08 Draft form: root
#   R09 state_shape: Statuses             R10 state_shape: Unit (PRIMACY)
#   R11 protocol 1                        R12 state_shape: Unit (verified=>PRIMACY)
#   R13 state_shape: Unit + protocol 5    R14 Canonical formats: VALIDITY
#   R15 state_shape: Unit (snake_case)    R16 Canonical formats: ISO dates
#   R17 state_shape: Edges                R18 Draft form: edges FROM/TO
#   R19 protocol 2                        R20 protocol 11
#   R21 state_shape: Artifacts (ARTIFACT) R22 state_shape: Artifacts + Draft form
#   R23 Canonical formats: ORIGIN + protocol 1
#   R24/R25/R26 state_shape: Demand registry (branch/owner; deadlines; verdicts)
#   R27 Draft form (qN continuous) + protocol 10
#   R28 Draft form: UPDATED + operational freshness
#   R29 Draft form: action                R30 package TRIGGER + Success (convergence)

import datetime
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUS_VOCAB = {"unverified", "verified", "refuted", "superseded"}
PRIMACY_VOCAB = {"primary", "secondary"}
EDGE_VOCAB = {"supersedes", "contradicts", "derived-from", "confirms", "depends-on"}
BRANCH_VOCAB = {"verify-myself", "ask-source", "accept-default"}
BOOL_VOCAB = {"true", "false"}
SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
# Artifact tokens in both spellings: art-007 (latin) and арт-007 (cyrillic).
ART_TOKEN_RE = re.compile(r"(?<![A-Za-zА-Яа-я0-9-])(?:art|арт)-(\d+)")
# A parenthesized note is allowed at the end of a VALIDITY value.
NOTE_RE = re.compile(r"\s*\([^()]*\)\s*$")
VALIDITY_FORMS = [
    re.compile(r"^as-of$"),
    re.compile(r"^as-of:(\d{4}-\d{2}-\d{2})$"),
    re.compile(r"^condition:\s*.+$"),
    re.compile(r"^(\d{4}-\d{2}-\d{2})$"),
    re.compile(r"^(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})$"),
]
ORIGIN_FORMS = [
    re.compile(r"^web:\s*https?://\S+$"),
    re.compile(r"^spoken:\s*person=[^,]+,\s*channel=[^,]+,\s*date=(\d{4}-\d{2}-\d{2})$"),
    re.compile(r"^check:\s*[^,]+,\s*date=(\d{4}-\d{2}-\d{2})$"),
    re.compile(r"^file:\s*\S+$"),
]
DATE_IN_TOKEN_RE = re.compile(r"date=([^\s;,]+)")


def iso_ok(s):
    if not ISO_RE.match(s or ""):
        return False
    y, m, d = s.split("-")
    try:
        datetime.date(int(y), int(m), int(d))
        return True
    except ValueError:
        return False


def F(rid, loc, msg):
    return ("FAIL", rid, loc, msg)


def W(rid, loc, msg):
    return ("WARN", rid, loc, msg)


def locate(arg):
    p = Path(arg)
    if p.is_dir():
        drafts = sorted(p.glob("data-draft-*.xml"))
        return drafts[0] if len(drafts) == 1 else None
    return p if p.is_file() else None


def build_model(root, task_dir):
    m = {"root": root, "task_dir": task_dir, "units": {}, "dup_tags": [],
         "unit_list": [], "edges": [], "questions": [], "status": None,
         "arts": {}, "art_order": [], "corpus": [], "dates": []}
    m["action"] = next((c for c in root if c.tag == "action"), None)
    m["sections"] = {name: root.find(name)
                     for name in ("units", "edges", "demand_registry", "artifacts")}
    if m["sections"]["units"] is not None:
        for u in m["sections"]["units"]:
            m["unit_list"].append(u)
            if u.tag in m["units"]:
                m["dup_tags"].append(u.tag)
            m["units"][u.tag] = u
    if m["sections"]["edges"] is not None:
        m["edges"] = [e for e in m["sections"]["edges"] if e.tag == "edge"]
    if m["sections"]["demand_registry"] is not None:
        m["questions"] = [q for q in m["sections"]["demand_registry"] if q.tag == "question"]
        m["status"] = m["sections"]["demand_registry"].find("status")
    if m["sections"]["artifacts"] is not None:
        for a in m["sections"]["artifacts"]:
            if a.tag == "art":
                m["art_order"].append(a.get("id", ""))
                m["arts"][a.get("id", "")] = a
    # Reference corpus: everything except the artifacts index itself
    # (index entries define artifacts, they do not reference them).
    m["corpus"].append((root.tag, " ".join(root.attrib.values()), (root.text or "").strip()))
    if m["action"] is not None:
        m["corpus"].append(("action", " ".join(m["action"].attrib.values()),
                            (m["action"].text or "").strip()))
    for u in m["unit_list"]:
        m["corpus"].append((u.tag, " ".join(u.attrib.values()), (u.text or "").strip()))
    for q in m["questions"]:
        m["corpus"].append((q.get("id", "?"), " ".join(q.attrib.values()), (q.text or "").strip()))
    if m["status"] is not None:
        m["corpus"].append(("status", " ".join(m["status"].attrib.values()),
                            (m["status"].text or "").strip()))
    # Single structural-date collector (used by R16 and R28).
    d = m["dates"]
    if root.get("UPDATED"):
        d.append(("root@UPDATED", root.get("UPDATED")))
    if m["status"] is not None and m["status"].get("AS_OF"):
        d.append(("status@AS_OF", m["status"].get("AS_OF")))
    for u in m["unit_list"]:
        v = u.get("VALIDITY")
        if v:
            for iso in re.findall(r"\d{4}-\d{2}-\d{2}", NOTE_RE.sub("", v)):
                d.append((u.tag + "@VALIDITY", iso))
        o = u.get("ORIGIN", "")
        for tok in o.split(";"):
            mt = DATE_IN_TOKEN_RE.search(tok)
            if mt:
                d.append((u.tag + "@ORIGIN", mt.group(1)))
    for q in m["questions"]:
        if q.get("DEADLINE"):
            d.append((q.get("id", "?") + "@DEADLINE", q.get("DEADLINE")))
    return m


def referenced_arts(m):
    refs = set()
    for _, attrs, text in m["corpus"]:
        for nn in ART_TOKEN_RE.findall(attrs + " " + text):
            refs.add(nn.lstrip("0") or "0")
    return refs


def index_arts(m):
    idx = {}
    for aid in m["art_order"]:
        mm = re.match(r"^art-(\d+)$", aid)
        if mm:
            idx[mm.group(1).lstrip("0") or "0"] = aid
        else:
            idx[aid] = aid
    return idx


def check(m):
    out = []
    root, task_dir = m["root"], m["task_dir"]

    # R01 canonical path
    draft_name = m.get("draft_name", "")
    mo = re.match(r"^data-fold-(.+)$", task_dir.name)
    if not mo or draft_name != "data-draft-%s.xml" % mo.group(1) or task_dir.parent.name != ".data-folds":
        out.append(F("R01", str(task_dir), "not the canonical .data-folds/data-fold-<slug>/data-draft-<slug>.xml"))

    # R03 artifacts index present + files exist
    if m["sections"]["artifacts"] is None:
        out.append(F("R03", "artifacts", "artifacts index section missing"))
    else:
        for aid, a in m["arts"].items():
            pth = a.get("path", "")
            if not pth or not (task_dir / pth).is_file():
                out.append(F("R03", "artifacts/%s" % aid, "file missing on disk: %s" % pth))

    # R04 canonical artifact naming, id matches file name
    for aid, a in m["arts"].items():
        mm = re.match(r"^art-(\d+)$", aid)
        pth = Path(a.get("path", ""))
        name = pth.name
        mn = re.match(r"^art-(\d+)-", name)
        if not mm or not mn or int(mm.group(1)) != int(mn.group(1)) or pth.suffix == "":
            out.append(F("R04", "artifacts/%s" % aid, "id/path not in art-<NN>-<hint>.<ext> form: %s" % name))

    # R05 dense numbering (warn)
    nums = sorted(int(re.match(r"^art-(\d+)$", a).group(1))
                  for a in m["art_order"] if re.match(r"^art-(\d+)$", a))
    if nums:
        if len(set(nums)) != len(nums):
            out.append(W("R05", "artifacts", "duplicate artifact numbers"))
        elif nums != list(range(nums[0], nums[-1] + 1)):
            missing = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums))
            out.append(W("R05", "artifacts", "numbering gaps: %s" %
                         ", ".join("art-%03d" % n for n in missing)))

    refs, idx = referenced_arts(m), index_arts(m)

    # R06 orphan index entries (warn)
    for nn in sorted(idx, key=lambda x: int(x) if x.isdigit() else 10 ** 9):
        if nn not in refs:
            out.append(W("R06", "artifacts/%s" % idx[nn], "indexed but referenced nowhere"))

    # R22 every mentioned art token resolves into the index
    for nn in sorted(refs, key=lambda x: int(x) if x.isdigit() else 10 ** 9):
        if nn not in idx:
            out.append(F("R22", "art-%s" % nn, "mentioned but not in the artifacts index"))

    # R08 root form
    if root.tag != "data_draft":
        out.append(F("R08", root.tag, "root element is not data_draft"))
    if not root.get("TASK"):
        out.append(F("R08", "root@TASK", "TASK attribute missing"))
    if root.get("UPDATED") and not iso_ok(root.get("UPDATED")):
        out.append(F("R08", "root@UPDATED", "UPDATED is not an ISO date"))
    if root.get("CYCLE") and not root.get("CYCLE").isdigit():
        out.append(F("R08", "root@CYCLE", "CYCLE is not an integer"))
    if root.get("FINAL") and root.get("FINAL") not in BOOL_VOCAB:
        out.append(F("R08", "root@FINAL", "FINAL is not true/false"))

    # R29 action element present and non-empty
    if m["action"] is None or not (m["action"].text or "").strip():
        out.append(F("R29", "action", "action element missing or empty"))

    # R11 units section, required attributes
    if m["units"] is None:
        out.append(F("R11", "units", "units section missing"))
    for u in m["unit_list"]:
        for attr in ("TYPE", "ORIGIN"):
            if not u.get(attr):
                out.append(F("R11", "units/%s@%s" % (u.tag, attr), "required attribute missing"))

    # R09/R10/R12/R13/R14/R15 per-unit rules
    for u in m["unit_list"]:
        loc = "units/%s" % u.tag
        st, prim, val = u.get("STATUS", ""), u.get("PRIMACY", ""), u.get("VALIDITY", "")
        if st and st not in STATUS_VOCAB:
            out.append(F("R09", loc + "@STATUS", "status not in the closed vocabulary"))
        if prim and prim not in PRIMACY_VOCAB:
            out.append(F("R10", loc + "@PRIMACY", "primacy not primary/secondary"))
        if st == "verified":
            if not prim:
                out.append(F("R12", loc, "verified unit without PRIMACY"))
            if not val:
                out.append(F("R13", loc, "verified unit without VALIDITY"))
        if val:
            stripped = NOTE_RE.sub("", val)
            if not any(f.match(stripped) for f in VALIDITY_FORMS):
                out.append(F("R14", loc + "@VALIDITY", "not a canonical VALIDITY form: %s" % val))
        if not SNAKE_RE.match(u.tag):
            out.append(F("R15", loc, "tag is not snake_case"))
    for tag in m["dup_tags"]:
        out.append(F("R15", "units/%s" % tag, "duplicate unit tag"))

    # R16 structural dates are ISO
    for loc, ds in m["dates"]:
        if not iso_ok(ds):
            out.append(F("R16", loc, "structural date is not ISO YYYY-MM-DD: %s" % ds))

    # R28 UPDATED freshness (warn)
    upd = root.get("UPDATED")
    if upd and iso_ok(upd):
        valid = [d for _, d in m["dates"] if iso_ok(d)]
        if valid and max(valid) > upd:
            out.append(W("R28", "root@UPDATED", "UPDATED %s is behind the newest date in file %s" % (upd, max(valid))))

    # R17/R18/R19/R20 edges
    if m["sections"]["edges"] is None:
        out.append(F("R17", "edges", "edges section missing (may be empty, but must exist)"))
    tags = set(m["units"])
    derived_from = set()
    confirms_to = {}
    for i, e in enumerate(m["edges"]):
        loc = "edges[%d]" % i
        t, f, tt = e.get("TYPE", ""), e.get("FROM", ""), e.get("TO", "")
        if t not in EDGE_VOCAB:
            out.append(F("R17", loc + "@TYPE", "edge type not in the closed vocabulary"))
        for role, v in (("FROM", f), ("TO", tt)):
            if v and v not in tags:
                out.append(F("R18", loc + "@%s" % role, "points to a non-existing unit: %s" % v))
        if t == "derived-from" and f:
            derived_from.add(f)
        if t == "confirms" and tt:
            confirms_to.setdefault(tt, []).append(f)
    for u in m["unit_list"]:
        if u.tag in derived_from and u.get("STATUS") == "verified":
            ok = any(conf in tags and m["units"][conf].get("ORIGIN", "") != u.get("ORIGIN", "")
                     for conf in confirms_to.get(u.tag, []))
            if not ok:
                out.append(F("R19", "units/%s" % u.tag,
                             "verified derivation without a confirms edge from a different-origin unit"))
    for i, e in enumerate(m["edges"]):
        if e.get("TYPE") == "contradicts":
            f, tt = e.get("FROM", ""), e.get("TO", "")
            reg = any(q.get("tag") in (f, tt) or f in (q.text or "") or tt in (q.text or "")
                      or f in q.get("VERDICT", "") or tt in q.get("VERDICT", "")
                      for q in m["questions"])
            if not reg:
                out.append(F("R20", "edges[%d]" % i,
                             "contradicts edge without a demand-registry record (protocol 11)"))

    # R21 unit ARTIFACT attribute resolves into the index
    for u in m["unit_list"]:
        av = u.get("ARTIFACT")
        if av:
            mm = ART_TOKEN_RE.search(av)
            if not mm or (mm.group(1).lstrip("0") or "0") not in idx:
                out.append(F("R21", "units/%s@ARTIFACT" % u.tag, "does not resolve into the artifacts index"))

    # R23 ORIGIN grammar
    for u in m["unit_list"]:
        o = u.get("ORIGIN", "")
        if not o:
            continue
        for tok in (t.strip() for t in o.split(";") if t.strip()):
            if not any(f.match(tok) for f in ORIGIN_FORMS):
                out.append(F("R23", "units/%s@ORIGIN" % u.tag, "token not canonical: %s" % tok))

    # R24 open questions form
    if m["sections"]["demand_registry"] is None:
        out.append(F("R24", "demand_registry", "demand_registry section missing"))
    for q in m["questions"]:
        loc = "registry/%s" % q.get("id", "?")
        if not q.get("VERDICT"):
            if not q.get("OWNER"):
                out.append(F("R24", loc + "@OWNER", "open question without an owner"))
            br = q.get("BRANCH", "")
            if br not in BRANCH_VOCAB:
                out.append(F("R24", loc + "@BRANCH", "branch missing or not in the closed vocabulary"))
        if q.get("BLOCKING") and q.get("BLOCKING") not in BOOL_VOCAB:
            out.append(F("R24", loc + "@BLOCKING", "BLOCKING is not true/false"))

    # R25 deadline form
    for loc, ds in m["dates"]:
        if loc.endswith("@DEADLINE") and not iso_ok(ds):
            out.append(F("R25", loc, "deadline is not an ISO date: %s" % ds))

    # R26 closed questions keep verdict records (warn)
    for q in m["questions"]:
        if not q.get("BRANCH"):
            if not q.get("VERDICT"):
                out.append(W("R26", "registry/%s" % q.get("id", "?"), "no branch and no verdict record"))
            elif not q.get("OWNER"):
                out.append(W("R26", "registry/%s" % q.get("id", "?"), "verdict record without an owner"))

    # R27 registry id continuity (warn)
    qnums = sorted(int(mm.group(1)) for mm in
                   (re.match(r"^q(\d+)$", q.get("id", "")) for q in m["questions"]) if mm)
    if qnums:
        if len(set(qnums)) != len(qnums):
            out.append(W("R27", "registry", "duplicate question ids"))
        elif qnums != list(range(qnums[0], qnums[-1] + 1)):
            missing = sorted(set(range(qnums[0], qnums[-1] + 1)) - set(qnums))
            out.append(W("R27", "registry", "id gaps: %s" %
                         ", ".join("q%d" % n for n in missing)))

    # R30 convergence claim consistency
    claims = []
    if root.get("FINAL") == "true":
        claims.append("root@FINAL")
    if m["status"] is not None and m["status"].get("COMPLETE") == "true":
        claims.append("status@COMPLETE")
    if claims:
        for q in m["questions"]:
            if q.get("BLOCKING") == "true":
                out.append(F("R30", "registry/%s" % q.get("id", "?"),
                             "convergence claimed (%s) with a blocking question open" % "+".join(claims)))
    return out


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("usage: check_draft.py <task-dir | draft-file>\n")
        return 2
    draft = locate(sys.argv[1])
    findings = []
    task_dir = None
    if draft is None:
        findings.append(F("R01", sys.argv[1], "draft file not found"))
    else:
        task_dir = draft.parent if draft.name.startswith("data-draft-") else draft
        if task_dir.name.startswith("data-draft-"):
            # a draft file passed directly from outside its task dir
            pass
        raw = draft.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as ex:
            findings.append(F("R02", str(draft), "not valid UTF-8: %s" % ex))
            report(findings)
            return 1
        if "\ufffd" in text:
            findings.append(F("R02", str(draft), "replacement character found (encoding corruption)"))
        try:
            root = ET.fromstring(text)
        except ET.ParseError as ex:
            findings.append(F("R07", str(draft), "XML not well-formed: %s" % ex))
            report(findings)
            return 1
        m = build_model(root, task_dir)
        m["draft_name"] = draft.name
        findings.extend(check(m))
    report(findings)
    return 1 if any(f[0] == "FAIL" for f in findings) else 0


def report(findings):
    for cls, rid, loc, msg in findings:
        sys.stdout.write("[%s] %s %s: %s\n" % (cls, rid, loc, msg))
    fails = sum(1 for f in findings if f[0] == "FAIL")
    warns = len(findings) - fails
    sys.stdout.write("summary: FAIL %d, WARN %d\n" % (fails, warns))


if __name__ == "__main__":
    sys.exit(main())
