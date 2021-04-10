import re
from glob import glob
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "fname",
    [
        f
        for f in glob("**/*.md", recursive=True)
        if "_build" not in f and Path(f).read_text(encoding="utf-8").startswith("---")
    ],
)
def test_doc_code_cells(fname, qapp, globalns=globals()):
    """Make sure that all code cells in documentation perform as expected."""
    text = Path(fname).read_text()
    code_cells = re.findall(r"```{code-cell}[^\n]+\n(.*?)`{3}", text, re.S)
    for cell in code_cells:
        nontags = [ln for ln in cell.splitlines() if not ln.startswith(":tags:")]
        cell = "\n".join(nontags)
        header = re.search(r"-{3}(.+?)-{3}", cell, re.S)
        if header:
            print("header", header)
            cell = cell.replace(header.group(), "")
            if "warns" in header.group():
                with pytest.warns(None):
                    exec(cell, globalns)
                continue
            if "raises-exception" in header.group():
                with pytest.raises(Exception):
                    exec(cell, globalns)
                continue
        exec(cell, globalns)