# python-pytest-check\_mk

[![Build Status](https://travis-ci.org/tom-mi/python-pytest-check_mk.svg?branch=master)](https://travis-ci.org/tom-mi/python-pytest-check_mk)

Plugin for [py.test](http://pytest.org/) to test [Check_MK](https://mathias-kettner.de/check_mk.html) checks.

## Usage

The following example contains a test suite for the `foobar` check contained in the Check\_mk installation (see `share/doc/check_mk/skeleton_check`).
The check file needs to be named after its agent section, i.e. `foobar`.

### Directory layout

    ├── agents
    │   └── plugins
    │       └── foobar_linux
    ├── checks
    │   └── foobar
    └── test
        └── test_foobar.py

### Test agent

All executable files in the `agents` directory can be executed with the `agents` fixture:

    def test_agent_plugin(agent):
        assert agents['plugins/foobar_linux'].run() == '<<<foobar>>>\nFOO BAR\n'

It is also possible to pass commandline arguments to the agent or agent plugin:

    def test_fritzbox_agent(agents):
        assert '<<<fritz>>>' in agents['special/agent_fritzbox'].run('--timeout', '20', 'fritz.box')

### Test check

Within a single test file one check file can be tested. The name of the check file is set with the `test_for` module-level variable.

    from pytest_check_mk import OK, WARNING, CRITICAL, UNKNOWN


    test_for = 'foobar'


    sample_plugin_output = '''
    <<<foobar>>>
    FOO BAR
    '''


    def test_inventory(checks):
        assert checks['foobar'].inventory(sample_plugin_output) == []


    def test_check(checks):
        item = None
        params = None
        assert checks['foobar'].check(item, params, sample_plugin_output) == (UNKNOWN, 'UNKNOWN - Check not implemented')


    def test_settings(checks):
        assert checks['foobar'].service_description == 'FOOBAR'
        assert not checks['foobar'].has_perfdata

### Test check with agent data

There is a sort of 'ensure everything works together' assertion. It calls both inventory and check function with a given agent output and checks that the return values match the expected format.

    from pytest_check_mk.assertions import assert_inventory_and_check_works_with_check_output


    test_for = 'foobar'


    def test_check_with_agent_output(agent, checks):
        output = agents['plugins/foobar_linux'].run()
        assert_inventory_and_check_works_with_check_output(checks['foobar'], output)

## License

This software is licensed under GPLv2.
