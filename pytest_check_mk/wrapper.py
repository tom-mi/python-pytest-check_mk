import os.path
import re
import subprocess

from pytest import UsageError

from pytest_check_mk import MissingFileError
from pytest_check_mk.file_loader import check_module_from_source


def create_check_file_wrapper(name):
    path = os.path.join('checks', name)

    module = check_module_from_source(name, path)
    return CheckFileWrapper(name, module)


class CheckFileWrapper(object):

    def __init__(self, name, module):
        self.name = name
        self.module = module

    @property
    def check_info(self):
        return self.module.check_info

    def __getitem__(self, key):
        return CheckWrapper(self, key)


class CheckWrapper(object):

    def __init__(self, check_file, name):
        __tracebackhide__ = True
        section = name.split('.')[0]

        if not section == check_file.name:
            raise UsageError('Cannot create CheckWrapper for section {} with CheckFileWrapper for section {}'
                             .format(section, check_file.name))

        self.check_file = check_file
        self.name = name
        self.section = section

    @property
    def check_info(self):
        return self.check_file.check_info[self.name]

    @property
    def has_perfdata(self):
        return self.check_info.get('has_perfdata', False)

    @property
    def service_description(self):
        return self.check_info['service_description']

    def inventory(self, check_output):
        __tracebackhide__ = True
        section, info = parse_info(check_output.strip())
        if section != self.section:
            raise ValueError('Wrong section name in test data: expected "{}", got "{}"'.format(self.section, section))

        inventory_function = self.check_info['inventory_function']
        return inventory_function(info)

    def check(self, item, params, check_output):
        __tracebackhide__ = True
        section, info = parse_info(check_output.strip())
        if section != self.section:
            raise ValueError('Wrong section name in test data: expected "{}", got "{}"'.format(self.section, section))

        check_function = self.check_info['check_function']
        return check_function(item, params, info)


def parse_info(check_output):
    __tracebackhide__ = True
    lines = check_output.splitlines(True)

    section_name, section_options = parse_header(lines[0].strip())

    try:
        separator = chr(int(section_options['sep']))
    except:
        separator = None

    output = []
    for line in lines[1:]:
        if is_header(line.strip()):
            raise ValueError('Test data contains a second section header: {}'.format(line.strip()))
        if 'nostrip' not in section_options:
            line = line.strip()
        output.append(line.split(separator))

    return section_name, output


def parse_header(header):
    __tracebackhide__ = True

    if not is_header(header):
        raise ValueError('Invalid header in test data: {}'.format(header))

    header_items = header[3:-3].split(':')
    name = header_items[0]
    section_options = {}
    for option in header_items[1:]:
        match = re.match('^([^\(]+)(?:\((.*)\))$', option)
        if match:
            key, value = match.groups()
            section_options[key] = value
        else:
            raise ValueError('Invalid section option {}'.format(option))

    return name, section_options


def is_header(line):
    __tracebackhide__ = True
    return line.strip()[:3] == '<<<' and line.strip()[-3:] == '>>>'


class AgentDirectoryWrapper(object):

    def __getitem__(self, key):
        return AgentWrapper(key)


class AgentWrapper(object):

    def __init__(self, relpath):
        path = os.path.join('agents', relpath)

        if not os.path.exists(path):
            raise MissingFileError(path)

        self.path = path

    def run(self, *extra_args):

        cmd = [self.path] + list(extra_args)

        return subprocess.check_output(cmd)
