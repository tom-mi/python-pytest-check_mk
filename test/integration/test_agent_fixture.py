import pytest
import stat


@pytest.fixture
def example_agent(testdir):
    agent_file = testdir.mkdir('agents').mkdir('plugins').join('example')

    with agent_file.open('w') as f:
        f.write('''#!/bin/sh
echo '<<<example>>>'
echo 'foo 42'
''')

    agent_file.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def test_agent_fixture_fails_on_missing_check_specification(testdir):
    testdir.makepyfile('''
        def test_foo(agent):
            pass
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*UsageError: Please specify the check to test*
        *UsageError
    ''')


def test_agent_fixture_fails_on_missing_agent_executable(testdir):
    testdir.makepyfile('''
        test_for = 'example'


        def test_foo(agent):
            pass
    ''')

    result = testdir.runpytest()

    assert result.ret != 0
    result.stdout.fnmatch_lines('''
        E*MissingFileError*"agents/plugins/example" does not exist*
        *MissingFileError
    ''')


def test_agent_fixture_runs_agent(testdir, example_agent):
    testdir.makepyfile('''
        test_for = 'example'


        def test_foo(agent):
            result = agent.run()

            assert result == '<<<example>>>\\nfoo 42\\n'
    ''')

    result = testdir.runpytest()

    assert result.ret == 0
