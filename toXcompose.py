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
        xval += f"<{kval}>"
    return xval

def get_xcompose_val(val):
    return f'"{val}"'

@click.command()
@click.argument('yamlfile', type=click.File())
def main(yamlfile):
    """
    Export .yaml config file back to XCompose file
    i.e. this is reverse of gen-compose-convert
    """
    yamldata = yaml.load(yamlfile.read(), Loader=yaml.Loader)
    for k, v in yamldata.items():
        xkey = get_xcompose_key(k)
        xval = get_xcompose_val(v)
        echo(f"{xkey}:{xval}")

if __name__ == '__main__':
    main()

