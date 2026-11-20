"""Check structural parity and bibliography integrity of standalone thesis files."""
from pathlib import Path
import json
import re

CODE = Path(__file__).resolve().parents[1]
PROJECT = CODE.parent
LANGUAGES = ("vi", "en")


def bib_keys(text: str) -> list[str]:
    return re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", text)


def citations(text: str) -> list[str]:
    return [key.strip() for group in re.findall(r"\\cite\w*\{([^}]+)\}", text)
            for key in group.split(",")]


inspected = {}
for lang in LANGUAGES:
    folder = PROJECT / "thesis" / lang
    expected = {"figs", "slide", "main.tex", "refs.bib"}
    actual = {item.name for item in folder.iterdir()}
    assert expected.issubset(actual), (lang, "Missing required thesis entries", sorted(expected - actual))
    main = (folder / "main.tex").read_text(encoding="utf-8")
    bib = (folder / "refs.bib").read_text(encoding="utf-8")
    keys = bib_keys(bib)
    assert len(keys) == len(set(keys)), (lang, "Duplicate bibliography keys")
    cites = citations(main)
    assert set(cites) <= set(keys), (lang, "Unknown citations", sorted(set(cites) - set(keys)))
    labels = re.findall(r"\\label\{([^}]+)\}", main)
    assert len(labels) == len(set(labels)), (lang, "Duplicate labels")
    assert "\\input{" not in main, (lang, "External TeX input")
    assert "**" not in main, (lang, "Markdown syntax in TeX")
    assert r"\chap{Abstract}" in main, (lang, "Missing Abstract chapter")
    inspected[lang] = {
        "bibliography_entries": len(keys),
        "cited_unique": len(set(cites)),
        "uncited_keys": sorted(set(keys) - set(cites)),
        "sections": len(re.findall(r"\\section(?:\[[^\]]*\])?\{", main)),
        "subsections": len(re.findall(r"\\subsection(?:\[[^\]]*\])?\{", main)),
        "labels": sorted(labels),
        "citations": sorted(cites),
        "bib_keys": sorted(keys),
    }

for field in ("bib_keys", "labels", "citations", "sections", "subsections"):
    assert inspected["vi"][field] == inspected["en"][field], ("Bilingual parity", field)

report = {
    "scope": "Standalone folder shape, citation/label/section parity, bibliography keys; translation meaning and visual layout require separate review.",
    "bibliography_entries": inspected["vi"]["bibliography_entries"],
    "cited_unique": inspected["vi"]["cited_unique"],
    "uncited_keys": inspected["vi"]["uncited_keys"],
    "sections": inspected["vi"]["sections"],
    "subsections": inspected["vi"]["subsections"],
    "status": "PASS",
}
output = CODE / "results" / "manuscript_structure_check.json"
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
