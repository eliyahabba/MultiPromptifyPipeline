import re
from pathlib import Path
from src.multipromptify.template_keys import (
    INSTRUCTION_TEMPLATE_KEY, INSTRUCTION_KEY, QUESTION_KEY, GOLD_KEY, FEW_SHOT_KEY, OPTIONS_KEY, CONTEXT_KEY, PROBLEM_KEY,
    GOLD_FIELD, INSTRUCTION_TEMPLATE_FIELD,
    PARAPHRASE_WITH_LLM, REWORDING, CONTEXT_VARIATION, SHUFFLE_VARIATION, MULTIDOC_VARIATION, ENUMERATE_VARIATION
)

REPLACEMENTS = {
    # 'instruction_template': INSTRUCTION_TEMPLATE_KEY,
    # 'instruction': INSTRUCTION_KEY,
    # 'question': QUESTION_KEY,
    # 'gold': GOLD_KEY,
    # 'few_shot': FEW_SHOT_KEY,
    # 'options': OPTIONS_KEY,
    # 'context': CONTEXT_KEY,
    # 'problem': PROBLEM_KEY,
    # 'gold_field': GOLD_FIELD,
    # 'instruction_template_field': INSTRUCTION_TEMPLATE_FIELD,
    'paraphrase': PARAPHRASE_WITH_LLM,
    # 'surface': REWORDING,
    # 'context_variation': CONTEXT_VARIATION,
    # 'shuffle': SHUFFLE_VARIATION,
    # 'multidoc': MULTIDOC_VARIATION,
    # 'enumerate': ENUMERATE_VARIATION,
}

DOCS_ROOTS = [
    'README.md',
    'docs',
]

def update_docs():
    for root in DOCS_ROOTS:
        path = Path(root)
        if path.is_file():
            files = [path]
        elif path.is_dir():
            files = list(path.rglob('*.md'))
        else:
            print(f"Skipping {root} (not found)")
            continue
        for file in files:
            text = file.read_text(encoding='utf-8')
            for old, new in REPLACEMENTS.items():
                text = re.sub(rf"(['\"]){old}(['\"])", rf"\1{new}\2", text)
                text = re.sub(rf":{old}\b", f":{new}", text)
            file.write_text(text, encoding='utf-8')
            print(f"Updated {file}")

if __name__ == '__main__':
    update_docs() 