# tests — regression fixture for check_draft.py

The synthetic draft in `.data-folds/data-fold-fixture/` embeds known defects of every rule family (no real data).

Run and compare:
    python scripts/check_draft.py tests/.data-folds/data-fold-fixture | diff - tests/expected.txt

Pass criterion: empty diff. Any change to the script or to the spec's "Draft form" / "Canonical formats" sections must keep the diff empty — or update expected.txt in the same commit, with each changed line reviewed against the rule inventory.
