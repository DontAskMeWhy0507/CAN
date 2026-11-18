from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'src'),str(Path(__file__).resolve().parents[1]/'scripts')]
import pytest
from thesis_final.mixstyle import integrate, CODE
from finalize_thesis_for_supervisor import structural


def test_verified_bilingual_supplement_has_consistent_labels_and_references():
    result={}
    for lang in ['vi','en']:
        source=CODE/'output/thesis_supervisor_final_2026-11-09'/lang
        text,bib,proof=integrate((source/'main.tex').read_text(encoding='utf-8'),(source/'refs.bib').read_text(encoding='utf-8'),lang)
        result[lang]=structural(text,bib)
        assert proof['new_fits']==12 and proof['external_captures_reused']==57
        assert text.count('\\label{sec:mixstyle-study}')==1
        assert '0.8194' in text and '0.9527' in text
        assert bib.count('{zhou2021mixstyle,')==1
        with pytest.raises(ValueError,match='already present'): integrate(text,bib,lang)
    for key in ['labels','citations','sections','subsections']:
        assert result['vi'][key]==result['en'][key]
