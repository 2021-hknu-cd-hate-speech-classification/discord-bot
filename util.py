import re


def clean_discord_markdown(txt: str) -> str:
    pattern = re.compile(r"[*_~]+([^*_~]+)[*_~]+")
    codeblock_pattern = re.compile(r"`{1,3}[^`]+`{1,3}")
    quote_pattern = re.compile(r"^>{1,3}\s?", re.MULTILINE)

    txt = pattern.sub(r"\1", txt)
    txt = codeblock_pattern.sub("", txt)
    txt = quote_pattern.sub("", txt)

    return " ".join([x.strip() for x in txt.split("\n") if x != ""]).strip()
