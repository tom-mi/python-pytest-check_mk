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


def test_agents_fixture_fails_on_missing_agent_plugin_executable(testdir):
    testdir.makepyfile('''
        def test_foo(agents):
            agents['plugins/example']
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*MissingFileError*"agents/plugins/example" does not exist*
        *MissingFileError
    ''')


def test_agents_fixture_runs_agent_plugin(testdir, example_agent_plugin):
    testdir.makepyfile('''
        def test_foo(agents):
            result = agents['plugins/example'].run()

            assert result == b'<<<example>>>\\nfoo 42\\n'
    ''')

    result = testdir.runpytest()
    print(result.stdout)

    assert result.ret == 0
