import json
import re
from collections.abc import MutableMapping
from copy import deepcopy
from typing import Union, Tuple, Callable, Type, Iterable, Dict

import click
import yaml
from click import echo


def key_nest(keys: Iterable) -> Dict:
    """
    creates key nest from provided values

    >>> key_nest('1234')
    {'1': {'2': {'3': '4'}}}
    """
    v = None
    for c in keys[::-1]:
        if not v:
            v = c
        else:
            v = {c: v}
    return v


def object_hook(dict_, func: Callable, types: Union[Tuple[Type], Type] = dict):
    """
    object hook for python dictionary - applies function to every object of type recursively
    note: dictionary keys are not considered to be objects and will be type matched,
    for processing dictionary keys you should process whole dict type.
    example:
    >>> object_hook({'foo': 'bar'}, str.upper, str)
    {'foo': 'BAR'}
    >>> object_hook({'foo': {'nested': 10}}, lambda v: v+1, int)
    {'foo': {'nested': 11}}
    """
    new = deepcopy(dict_)
    if isinstance(dict_, types):  # hook self as well
        new = func(new)

    if not isinstance(new, MutableMapping):
        return new

    for key in new:
        # recursive object_hook for dicts
        if isinstance(new[key], MutableMapping):
            new[key] = object_hook(new[key], func, types)
        # for lists either apply function if type matched or recursive object_hook if dict
        elif isinstance(new[key], (list, tuple)):
            new[key] = type(new[key])(
                object_hook(v, func, types) if
                isinstance(v, MutableMapping) else func(v)
                if isinstance(v, types) else v
                for v in new[key]
            )

        if isinstance(new[key], types):
            new[key] = func(new[key])

    return new


@click.command()
@click.argument('mappings', type=click.File(), nargs=-1)
@click.option('--key', default='§', show_default=True, help='key to use as compose key')
@click.option('-r', '--raw', is_flag=True, help='just keymap without prefix')
def main(mappings, raw, key):
    """Generate macos rebind file from compose json mapping"""
    all_maps = {}
    for mapping in mappings:
        yamldata = yaml.load(mapping.read(), Loader=yaml.Loader)
        all_maps.update(**{str(k): str(v) for k, v in yamldata.items()})
    all_maps = read_paths(all_maps)
    text = data_to_mac_dict(all_maps)
    if raw:
        echo(text)
    else:
        based = '{{"' + key + '" = {}}}'
        echo(based.format(text))


def merge(source, destination):
    """
    deepmerge dictionaries

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    """
    if isinstance(destination, str):
        return source
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value
    return destination


def read_paths(data):
    """
    Unpack first key of a dictionary as nested dictionary path

    >>> read_paths({'cat': '>-.-<'})
    {'c': {'a': {'t': '>-.-<'}}}
    """
    parsed = {}
    for k, v in data.items():
        parsed = merge(parsed, key_nest(list(k) + [v]))
    return parsed


def data_to_mac_dict(data):
    """
    converts dictionary data to macos keymap.dict format

    >>> data_to_mac_dict({'c': {'a': {'t': '(^≗ω≗^)'}}})
    {
      "c" = {
        "a" = {
          "t" = ("insertText:", "(^≗ω≗^)");
        };
      };
    };
    """
    updated = object_hook(data, lambda value: f'INSERT:{value}', str)
    text = json.dumps(updated, indent=2, ensure_ascii=False)
    repl = lambda value: f'("insertText:", "{value.groups()[0]}");'
    text = re.sub('"INSERT:(.+)",*', repl, text)
    text = re.sub('},*', '};', text)
    text = re.sub('": ', '" = ', text)
    return text


if __name__ == '__main__':
    main()
