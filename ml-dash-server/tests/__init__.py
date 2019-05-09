from collections import OrderedDict

from termcolor import cprint


def setup_yaml():
    """ https://stackoverflow.com/a/8661021 """
    import yaml

    def represent_dict_order(self, data):
        return self.represent_mapping('tag:yaml.org,2002:map', data.items())

    yaml.add_representer(OrderedDict, represent_dict_order)

    cprint('yaml is setup', 'green')


setup_yaml()


def show(obj):
    import yaml
    print(yaml.dump(obj))


def shows(obj):
    import yaml
    return yaml.dump(obj)
