import pytest
import stat


@pytest.fixture
def example_agent_plugin(testdir):
    agent_plugin_file = testdir.mkdir('agents').mkdir('plugins').join('example')

    with agent_plugin_file.open('w') as f:
        f.write('''#!/bin/sh
echo '<<<example>>>'
echo 'foo 42'
''')

    agent_plugin_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def test_agent_plugin_fixture_fails_on_missing_check_specification(testdir):
    testdir.makepyfile('''
        def test_foo(agent_plugin):
            pass
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*UsageError: Please specify the check to test*
        *UsageError
    ''')


def test_agent_plugin_fixture_fails_on_missing_agent_plugin_executable(testdir):
    testdir.makepyfile('''
        test_for = 'example'


        def test_foo(agent_plugin):
            pass
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*MissingFileError*"agents/plugins/example" does not exist*
        *MissingFileError
    ''')


def test_agent_plugin_fixture_runs_agent_plugin(testdir, example_agent_plugin):
    testdir.makepyfile('''
        test_for = 'example'


        def test_foo(agent_plugin):
            result = agent_plugin.run()

            assert result == '<<<example>>>\\nfoo 42\\n'
    ''')

    result = testdir.runpytest()

    assert result.ret == 0
