import click
import re

from click import echo

KEY_MAP = {
    'bracketleft': '[',
    'bracketright': ']',
    'parenleft': '(',
    'parenright': ')',
    'Multi_key': '',
    'period': '.',
    'minus': '-',
    'plus': '+',
    'dollar': '$',
    'at': '@',
    'exclam': '!',
    'less': '<',
    'greater': '>',
    'slash': '/',
    'backslash': '\\',
    'question': '?',
    'space': ' ',
    'equal': '=',
    'asciitilde': '~',
    'numbersign': '#',
    'asterisk': '*',
    'colon': ':',
    'semicolon': ';',
    'percent': '%',
    'underscore': '_',
    'asciicircum': '^',
    'comma': ',',
    'apostrophe': "'",
    'quotedbl': '"',
    'bar': "|",
    'grave': "`",
    'ampersand': "&",
    'braceright': "}",
    'braceleft': "{",
    'KP_Multiply': "*",
    'exclamdown': "¡",
    'questiondown': "¿",
}


def quote(char):
    """
    quote yaml key
    - replaces `\` to `\\`
    - replace `"` to `\"`
    """
    char = char.replace('\\', '\\\\')
    char = char.replace('"', '\\"')
    return char


def remap_keys(keys):
    """remap xcompose keys to unicode characters"""
    result = []
    for key in keys:
        key = key.strip('<>')
        if len(key) > 1:
            # convert unicode hexes to unicode characters
            # e.g. U220B == ∋
            if key.startswith('U') and any(c.isdigit() for c in key):
                key = key.split('U', 1)[1]
                key = chr(int(key, 16))
            elif key not in KEY_MAP:
                raise ValueError(f'unsupported keymap: {key}')
        result.append(KEY_MAP.get(key, key))
    return result


@click.group()
def main():
    """convert alternative formats to yaml key: value format"""
    pass


@main.command()
@click.argument('files', type=click.File(), nargs=-1)
@click.option('-c', '--keep-comments', is_flag=True, help='keep inline comments')
def xcompose(files, keep_comments):
    """
    Convert xcompose file, that follows format like:
    <Multi_key> <parenleft> <period> <1> <parenright>: "⑴"
    """
    # e.g. < Multi_key > < parenleft > < period > < 1 > < parenright >: "⑴"
    for file in files:
        for row in file:
            row = row.strip()
            if not row:
                continue
            if row.startswith('#') or row.startswith('include'):
                continue
            if '#' in row:
                row, comment = row.split('#', 1)
            else:
                comment = ''
            try:
                from_, to = row.split(':', 1)
            except ValueError:
                echo(f'malformed line:\n{row}', err=True)
                continue
            from_ = re.split(r'\s+', from_)
            try:
                from_ = ''.join(remap_keys(from_))
            except ValueError as e:
                echo(f'{e}; skipping:\n  {row}', err=True)
                continue
            to = to.split('"')[1]
            value = f'"{quote(from_)}": "{quote(to)}"'
            if keep_comments and comment:
                value += f'  #{comment}'
            echo(value)


if __name__ == '__main__':
    main()
