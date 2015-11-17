# python-pytest-check\_mk

[![Build Status](https://travis-ci.org/tom-mi/python-pytest-check_mk.svg?branch=master)](https://travis-ci.org/tom-mi/python-pytest-check_mk)

Plugin for [py.test](http://pytest.org/) to test [Check_MK](https://mathias-kettner.de/check_mk.html) checks.

## Usage

The following example contains a test suite for the `foobar` check contained in the Check\_mk installation (see `share/doc/check_mk/skeleton_check`).
The check file needs to be named after its agent section, i.e. `foobar`.

### Directory layout

    ├── checks
    │   └── foobar
    └── test
        └── test_foobar.py

### Test

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

## License

This software is licensed under GPLv2.
