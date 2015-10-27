import os.path
import re
import subprocess

from pytest_check_mk import MissingFileError


_HEADER = \
'''
import sys, os, time, socket

def regex(r):
    __tracebackhide__ = True
    import re

    try:
        rx = re.compile(r)
    except Exception, e:
        raise AssertionError("Invalid regular expression '%s': %s" % (r, e))
    return rx


# The following data structures will be filled by the checks
check_info                         = {} # all known checks
checkgroup_of                      = {} # groups of checks with compatible parametration
check_includes                     = {} # library files needed by checks
precompile_params                  = {} # optional functions for parameter precompilation, look at df for an example
check_default_levels               = {} # dictionary-configured checks declare their default level variables here
factory_settings                   = {} # factory settings for dictionary-configured checks
check_config_variables             = [] # variables (names) in checks/* needed for check itself
snmp_info                          = {} # whichs OIDs to fetch for which check (for tabular information)
snmp_scan_functions                = {} # SNMP autodetection
active_check_info                  = {} # definitions of active "legacy" checks
special_agent_info                 = {}
'''


class CheckWrapper(object):

    def __init__(self, name, path=None):
        __tracebackhide__ = True
        section = name.split('.')[0]
        if not path:
            path = os.path.join('checks', section)

        if not os.path.exists(path):
            raise MissingFileError(path)

        self.name = name
        self.section = section
        self.path = path
        self.module = check_module_from_source(name, path)

    @property
    def has_perfdata(self):
        return self.module.check_info[self.name].get('has_perfdata', False)

    @property
    def service_description(self):
        return self.module.check_info[self.name]['service_description']

    def inventory(self, check_output, ):
        __tracebackhide__ = True
        section, info = parse_info(check_output.strip())
        if section != self.section:
            raise ValueError('Wrong section name in test data: expected "{}", got "{}"'.format(self.section, section))

        inventory_function = self.module.check_info[self.name]['inventory_function']
        return inventory_function(info)

    def check(self, item, params, check_output):
        __tracebackhide__ = True
        section, info = parse_info(check_output.strip())
        if section != self.section:
            raise ValueError('Wrong section name in test data: expected "{}", got "{}"'.format(self.section, section))

        check_function = self.module.check_info[self.name]['check_function']
        return check_function(item, params, info)


    def assert_inventory_and_check_works_with_check_output(self, check_output):
        # inventory
        inventory = self.inventory(check_output)

        self.assert_well_formed_inventory(inventory)

        # run check for each item in inventory using default params
        for item, default_params in inventory:
            params = getattr(self.module, default_params)
            result = self.check(item, params, check_output)
            self.assert_well_formed_check_result(result)

    def assert_well_formed_check_result(self, result):
        status = result[0]
        message = result[1]

        assert isinstance(status, int)
        assert 0 <= status <= 3

        assert isinstance(message, str)

        if self.has_perfdata:
            assert len(result) == 3
            perfdata = result[2]

            for entry in perfdata:
                self.assert_well_formed_perfdata_entry(entry)
        else:
            assert len(result) == 2

    def assert_well_formed_perfdata_entry(self, entry):
        assert 2 <= len(entry) <= 6

        assert isinstance(entry[0], str)
        assert type(entry[1]) in (int, float)
        for value in entry[2:]:
            assert (type(value) in (int, float)) or value == ''


    def assert_well_formed_inventory(self, inventory):
        can_have_multiple_items = '%s' in self.service_description

        if not can_have_multiple_items:
            assert len(inventory) <= 1

        for item, default_params in inventory:
            assert (item is None) != can_have_multiple_items
            if default_params is not None:
                assert hasattr(self.module, default_params)


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
        if not 'nostrip' in section_options:
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


def check_module_from_source(name, path):
    __tracebackhide__ = True

    import sys, imp
    source = open(path, 'r').read()
    code = compile(source, path, 'exec')
    module = imp.new_module(name)

    exec _HEADER in module.__dict__
    exec code in module.__dict__

    return module


class AgentPluginWrapper(object):

    def __init__(self, name, path=None):
        section = name.split('.')[0]
        if not path:
            path = os.path.join('agents', 'plugins', section)

        if not os.path.exists(path):
            raise MissingFileError(path)

        self.name = name
        self.section = section
        self.path = path

    def run(self, *extra_args):

        cmd = [self.path] + list(extra_args)

        return subprocess.check_output(cmd)
