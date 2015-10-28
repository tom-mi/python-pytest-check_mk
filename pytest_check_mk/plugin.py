import pytest

from pytest_check_mk.wrapper import AgentPluginWrapper, create_check_file_wrapper


def _get_check_name(request):
    __tracebackhide__ = True
    try:
       return getattr(request.module, 'test_for')
    except AttributeError:
        raise pytest.UsageError('Please specify the check to test with "test_for = \'my_check\'" at module level.')


@pytest.fixture
def agent_plugin(request):
    return AgentPluginWrapper(_get_check_name(request))


@pytest.fixture
def checks(request):
    return create_check_file_wrapper(_get_check_name(request))
