import tests.fixtures.models as models
from sqlalchemy_to_json_schema.dictify import ModelLookup
from tests.fixtures.models import Group, User


def _getTarget():
    return ModelLookup


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


def test_root_model():
    target = _makeOne(models)
    result = target("Group")
    assert result == Group


def test_child__of__root_model():
    """
    Group.users -> [User]
    """
    target = _makeOne(models)
    target("Group")
    result = target("users")
    assert result == User


def test_child__of__child__of__root_model():
    """
    Group.users -> [User]
    User.group -> Group
    """
    target = _makeOne(models)
    target("Group")
    target("users")
    result = target("group")
    assert result == Group
