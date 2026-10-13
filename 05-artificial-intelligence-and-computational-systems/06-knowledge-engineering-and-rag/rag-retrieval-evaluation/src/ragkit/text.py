"""Normalizacion y tokenizacion (espanol/ingles) sin dependencias externas."""
from __future__ import annotations
import re
import unicodedata

STOP_ES = frozenset("a al algo ante aqui as asi aun como con contra cual cuando de del desde donde e el ella ellos en entre es esa ese eso esta este esto estos fue ha han hasta hay la las le les lo los mas me mi muy ni no nos o para pero poco por porque que se sea ser si sin sobre son su sus tambien te tiene todo tu un una uno unos y ya".split())
STOP_EN = frozenset("a about all also an and any are as at be been but by can for from has have how if in into is it its more no not of on or our over so than that the their then there these they this to was we were what when where which who will with you your".split())
STOP = STOP_ES | STOP_EN
_TOKEN = re.compile(r"[a-z0-9]+")


def fold(text: str) -> str:
    """Minusculas y sin tildes (NFKD)."""
    return unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()


def stem(tok: str) -> str:
    """Stemmer ligero por sufijos (es/en). Deliberadamente simple y determinista."""
    if len(tok) <= 4 or tok.isdigit():
        return tok
    for suf in ("aciones", "acion", "amiento", "amientos", "mente", "ing", "ings", "ness", "ed", "es", "s"):
        if tok.endswith(suf) and len(tok) - len(suf) >= 4:
            return tok[: -len(suf)]
    return tok


def tokenize(text: str, *, stop: bool = True, stemming: bool = True, accents: bool = True) -> list[str]:
    """Tokeniza. accents=False conserva el texto sin plegar tildes antes de tokenizar (solo ascii restante)."""
    s = fold(text) if accents else text.lower()
    toks = _TOKEN.findall(s)
    if stop:
        toks = [t for t in toks if t not in STOP and len(t) > 1]
    if stemming:
        toks = [stem(t) for t in toks]
    return toks
