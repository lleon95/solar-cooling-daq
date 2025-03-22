import re

# Customize these values
GITHUB_URL_PREFIX = (
    "https://github.com/lleon95/solar-cooling-daq/blob/develop/"
)
README_INPUT = "../README.md"
README_OUTPUT = "../README_pdoc.md"


def rewrite_links(md_text: str) -> str:
    # Match [text](relative_path)
    return re.sub(
        r"\[([^\]]+)\]\((?!http)([^)]+)\)",
        lambda m: f"[{m.group(1)}]({GITHUB_URL_PREFIX}{m.group(2)})",
        md_text,
    )


with open(README_INPUT, encoding="utf-8") as f:
    content = f.read()

updated = rewrite_links(content)

with open(README_OUTPUT, "w", encoding="utf-8") as f:
    f.write(updated)

print(f"Rewritten links saved to {README_OUTPUT}")
