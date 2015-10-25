import pytest
import textwrap


HEADER = '''
        test_for = 'example'


'''

EMTPY_TEST = HEADER + '''
        def test_foo(check):
            pass
'''


@pytest.fixture
def example_check(testdir):
    check_file = testdir.mkdir('checks').join('example')

    def fill_file(content):
        check_file.open('w').write(textwrap.dedent(content))

    return fill_file


def test_check_fixture_fails_on_missing_check_specification(testdir):
    testdir.makepyfile('''
        def test_foo(check):
            pass
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*UsageError: Please specify the check to test*
        *UsageError
    ''')


def test_check_fixture_fails_on_missing_check(testdir):
    testdir.makepyfile(EMTPY_TEST)

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*MissingFileError*"checks/example" does not exist*
        *MissingFileError
    ''')


def test_check_fails_on_syntax_error(testdir, example_check):
    example_check('''print("blubb''')

    testdir.makepyfile(EMTPY_TEST)

    result = testdir.runpytest()
    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*SyntaxError*EOL while scanning string literal
        *SyntaxError
    ''')


def test_has_no_perfdata(testdir, example_check):
    example_check('''check_info['example'] = {}''')
    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            assert not check.has_perfdata
    ''')

    result = testdir.runpytest()

    assert result.ret == 0


def test_has_perfdata(testdir, example_check):
    example_check('''check_info['example'] = {'has_perfdata': True}''')
    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            assert check.has_perfdata
    ''')

    result = testdir.runpytest()

    assert result.ret == 0


def test_service_description(testdir, example_check):
    example_check('''check_info['example'] = {'service_description': 'foo %s'}''')
    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            assert check.service_description == 'foo %s'
    ''')

    result = testdir.runpytest()

    assert result.ret == 0


def test_inventory_fails_on_invalid_section_header(testdir, example_check):
    example_check('''
        check_info['example'] = {'inventory_function': lambda _: []}
    ''')

    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            check.inventory('<<foo')
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*ValueError: Invalid header in test data*
        *ValueError
    ''')


def test_inventory_fails_on_wrong_section_name(testdir, example_check):
    example_check('''
        check_info['example'] = {'inventory_function': lambda _: []}
    ''')

    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            check.inventory('<<<something_else>>>')
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*ValueError: Wrong section name*
        *ValueError
    ''')


def test_inventory_calls_parse_info(testdir, example_check, monkeypatch):
    import pytest_check_mk.wrapper

    calls = []
    def mockreturn(info):
        calls.append(info)
        return 'example', 'foobar'
    monkeypatch.setattr(pytest_check_mk.wrapper, 'parse_info', mockreturn)

    example_check('''
        check_info['example'] = {'inventory_function': lambda x: x}
    ''')

    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            assert check.inventory('<<<example>>>\\na b') == 'foobar'
    ''')

    result = testdir.runpytest()

    assert calls == ['<<<example>>>\na b']
    assert result.ret == 0


def test_inventory_parses_input_and_calls_inventory_function(testdir, example_check):
    example_check('''
        def inventory(info):
            return [int(line[0]) * 2 for line in info]

        check_info['example'] = {'inventory_function': inventory}
    ''')

    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            assert check.inventory('<<<example>>>\\n1 2\\n3 4') == [2, 6]
    ''')

    result = testdir.runpytest()

    assert result.ret == 0


def test_check_calls_parse_info(testdir, example_check, monkeypatch):
    import pytest_check_mk.wrapper

    calls = []
    def mockreturn(info):
        calls.append(info)
        return 'example', 'foobar'
    monkeypatch.setattr(pytest_check_mk.wrapper, 'parse_info', mockreturn)

    example_check('''
        check_info['example'] = {'check_function': lambda x, y, z: (x, y, z)}
    ''')

    testdir.makepyfile(HEADER + '''
        def test_foo(check):
            assert check.check('arg1', 'arg2', '<<<example>>>\\na b') == ('arg1', 'arg2', 'foobar')
    ''')

    result = testdir.runpytest()

    assert calls == ['<<<example>>>\na b']
    assert result.ret == 0
