import os


EXAMPLE_REPO = 'c:/github/azure-rest-api-specs-examples/specification/'


def update_markdown(filepath: str):
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    code_start = None
    for index, line in enumerate(lines):
        if line.startswith(r'```'):
            code_start = index
            break

    if code_start:
        out_lines = lines[code_start:]
        out_lines.append('\n')
        out_lines.extend(lines[:code_start])
        assert out_lines[-1].strip() == ''
        out_lines = out_lines[:-1]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(out_lines))


def main():
    for subdir, dirs, files in os.walk(EXAMPLE_REPO):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith('.md'):
                update_markdown(filepath)


main()
