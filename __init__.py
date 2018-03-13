class MultiIndexedDict():
    """
    """

    def __init__(self, properties, dict_type=dict):
        self._properties = properties
        # TODO Check correctness of properties here.
        self._dict_type = dict_type
        # TODO Check correctness of dict type here?

        # Per property, we have a collection
        self._dicts = dict([(prop, self._dict_type()) for prop in properties])

        # Contains for all objects a dict of (property->value)s,
        # so we can keep track of the per-object tracked properties (and their values).
        self._propdict = dict()

    def add(self, obj):
        # TODO return error if object already in propdict?
        prop_results = {prop: getattr(obj, prop) for prop in self._properties}
        # TODO Check for duplicate keys before altering here.
        for (prop, val) in prop_results.items():
            self._dicts[prop][val] = obj
        self._propdict[obj] = prop_results

    def find(self, prop, value):
        try:
            return self._dicts[prop][value]
        except KeyError as key_error:
            key_error.args = ('`{}`=`{}`'.format(prop, key_error.args[0]),)
            raise


    def __getitem__(self, propval_tuple):
        prop, val = propval_tuple
        return self.find(prop, val)

    def remove(self, obj):
        if not obj in self._propdict:
            raise KeyError(obj)
        # TODO return error if object not in propdict.
        prop_results = self._propdict[obj]
        for (prop, val) in prop_results.items():
            del self._dicts[prop][val]
        del self._propdict[obj]

    def __len__(self):
        return len(self._propdict)

    def __length_hint__(self):
        return self._propdict.__length_hint__()

    def __contains__(self, propval_tuple):
        prop, val = propval_tuple
        return val in self._dicts[prop]

    def update_item(self, obj):
        prop_results = {(prop, getattr(obj, prop)) for prop in self._properties}
        prev_prop_results = set(self._propdict[obj].items())
        for (prop, val) in (prev_prop_results - prop_results):
            del self._dicts[prop][val]
        for (prop, val) in (prop_results - prev_prop_results):
            self._dicts[prop][val] = obj
        self._propdict[obj] = prop_results

    def clear(self):
        self._dicts = dict([(prop, self._dict_type()) for prop in properties])
        self._propdict = dict()

    def copy(self):
        other = self.__class__(self._properties, dict_type=self._dict_type)
        other._propdict = self._propdict.copy()
        other._dicts = self.dicts.copy()

    def values(self, prop=None):
        if prop == None:
            return self._propdict.keys()
        else:
            return self._dicts[prop].keys()

    def items(self, prop):
        return self._dicts[prop].items()

    def keys(self, prop):
        return self._dicts[prop].keys()

    def items_props(self):
        return self._propdict.items()

    def properties(self):
        return self._properties

    def __iter__(self):
        """Maybe somewhat surprisingly, iterates over all objects inside the MultiIndexDict"""
        return self._propdict.keys()

    def __contains__(self, item):
        return item in self._propdict

    def get(self, prop, item, d=None):
        return self._dicts[prop].get(item, d=default)


    # TODO Per https://docs.python.org/3.6/reference/datamodel.html#emulating-container-types we should add(?):
    # -pop
    # -popitem
    # -update


if __name__ == "__main__":
    class User():
        def __init__(self, uid, name):
            self.uid = uid
            self.name = name

    mid = MultiIndexedDict({'uid', 'name'})
    qqwy = User(1, 'Qqwy')
    pete = User(2, 'Pete')
    john = User(3, 'John')
    mid.add(qqwy)
    mid.add(pete)
    mid.add(john)

    print(mid._propdict)
    print(mid._dicts)

    print(mid['uid', 1])
    print(mid['uid', 2])
    print(mid['name', 'Qqwy'])

    mid.remove(john)
    # mid.remove(john)
    # print(mid['name', 'John'])
