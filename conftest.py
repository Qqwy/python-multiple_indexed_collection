import pytest
@pytest.fixture(autouse=True)
def fill_doctests_namespace(doctest_namespace):
    """
    Common classes and objects used in doctests.
    """
    class User():
        def __init__(self, name, user_id):
            self.name = name
            self.user_id = user_id

    john = User('John', 1)
    pete = User('Pete', 2)
    lara = User('Lara', 3)
    doctest_namespace['User'] = User
    doctest_namespace['john'] = john
    doctest_namespace['pete'] = pete
    doctest_namespace['lara'] = lara
    print(doctest_namespace)
