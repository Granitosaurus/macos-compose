import yaml
import click
from click import echo
from convcompose import KEY_MAP

mapping_dict = {v: k for k, v in KEY_MAP.items()} 

def get_xcompose_key(key):
    xval = "<Multi_key> " # might be another unique value
    for i in key:
        kval = i
        if i in mapping_dict:
            kval = mapping_dict[i]
        xval += "<" + kval +"> "
    return xval

def get_xcompose_val(val):
    return '"' + val + '"' 

@click.command()
@click.argument('yamlfile', type=click.File())
def main(yamlfile):
    yamldata = yaml.load(yamlfile.read(), Loader=yaml.Loader)
    for k, v in yamldata.items():
        xkey = get_xcompose_key(k)
        xval = get_xcompose_val(v)
        echo(xkey + ":" + xval)

if __name__ == '__main__':
    main()

