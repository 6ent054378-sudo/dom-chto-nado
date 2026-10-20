"""Хелпер для правки HTML-секций (замены через lambda — без проблем с \\1)."""
import re


def apply(path, rules):
    """rules: список (pattern, repl|lambda). Возвращает список незаменённых паттернов."""
    c = open(path, encoding="utf-8").read()
    misses = []
    for pat, rep in rules:
        if callable(rep):
            new, n = re.subn(pat, rep, c, flags=re.S)
        else:
            new, n = re.subn(pat, rep.replace("\\", "\\\\"), c, flags=re.S)
        if n == 0:
            misses.append(pat[:100])
        c = new
    open(path, "w", encoding="utf-8").write(c)
    return misses


def T(pat, rep):
    """Паттерн с текстом-заменой (группы — через \\1 в rep, как в re)."""
    return (pat, rep)


def simple(pairs):
    """pairs: список (old_text, new_text) — прямая замена, как str.replace."""
    return [(re.escape(o), n.replace("\\", "\\\\")) for o, n in pairs]
