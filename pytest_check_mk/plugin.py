import pytest

from pytest_check_mk.wrapper import AgentWrapper, CheckWrapper


def _get_check_name(request):
    __tracebackhide__ = True
    try:
       return getattr(request.module, 'test_for')
    except AttributeError:
        raise pytest.UsageError('Please specify the check to test with "test_for = \'my_check\'" at module level.')


@pytest.fixture
def agent(request):
    return AgentWrapper(_get_check_name(request))


@pytest.fixture
def check(request):
    return CheckWrapper(_get_check_name(request))
