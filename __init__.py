class MultiIndexedCollection():
    """
    A collection type for arbitrary objects, that indexes them based on (a subset of) their properties.
    Which properties to look for is specified during the initialization of the MultiIndexedCollection;
    any hashable objects can be stored inside.

    removing/updating objects is also supported.
    The MultiIndexedCollection will _not_ automatically know when an object is changed, so calling `update` manually is necessary in that case.

    Optionally, custom dictionary-types can be used, which is nice if you have some special requirements for your dictionary types.
    """

    def __init__(self, properties, dict_type=dict):
        """Initializes the MultiIndexedCollection with the given `properties`.

        properties -- a set (or iteratable sequence convertable to one) of string names of properties to index.
        dict_type -- Optional; type to use under the hood to store objects in.
        """
        self._properties = set(properties)
        for property in self._properties:
            if not isinstance(property, str):
                raise ValueError("{} constructor expects `properties` argument to be a sequence of strings; `{}` is not a string property".format(self.__class__.__name__, property))
        self._dict_type = dict_type
        if (not hasattr(dict_type, '__getitem__')
            or not hasattr(dict_type, '__setitem__')
            or not hasattr(dict_type, '__len__')
            or not hasattr(dict_type, '__delitem__')
            or not hasattr(dict_type, '__iter__')
            or not hasattr(dict_type, '__contains__')
            or not hasattr(dict_type, 'get')
        ):
            raise Valueerror("{} constructor expects `dict_type` argument to be a mapping, but not all required mapping methods are implemented by {}.".format(self.__class_.__name__, dict_type))

        # Per property, we have a collection
        self._dicts = self._dict_type([(prop, self._dict_type()) for prop in properties])

        # Contains for all objects a dict of (property->value)s,
        # so we can keep track of the per-object tracked properties (and their values).
        self._propdict = self._dict_type()

    def add(self, obj):
        """
        Adds `obj` to the collection,
        so it can later be found under all its properties' values.
        """
        # TODO return error if object already in propdict?
        prop_results = {prop: getattr(obj, prop) for prop in self._properties}
        # TODO Check for duplicate keys before altering here.
        for (prop, val) in prop_results.items():
            self._dicts[prop][val] = obj
        self._propdict[obj] = prop_results

    def find(self, prop, value):
        """Finds the object whose indexed property `prop` has value `value`.

        Returns `KeyError` if this cannot be found.
        """
        try:
            return self._dicts[prop][value]
        except KeyError as key_error:
            key_error.args = ('`{}`=`{}`'.format(prop, key_error.args[0]),)
            raise


    def __getitem__(self, propval_tuple):
        """Finds the object whose indexed property `prop` has value `value`.

        Returns `KeyError` if this cannot be found.
        propval_tuple -- A tuple (pair) where `prop` is the first item and `value` the second.
        """
        prop, val = propval_tuple
        return self.find(prop, val)

    def remove(self, obj):
        """Removes `obj` from this collection, so it will no longer be indexed or found.
        """
        if not obj in self._propdict:
            raise KeyError(obj)
        # TODO return error if object not in propdict.
        prop_results = self._propdict[obj]
        for (prop, val) in prop_results.items():
            del self._dicts[prop][val]
        del self._propdict[obj]

    def __len__(self):
        """The amount of items in the collection.
        """
        return len(self._propdict)

    def __length_hint__(self):
        return self._propdict.__length_hint__()

    def __contains__(self, propval_tuple):
        """True if there exists an item under the key `value` for `prop`.

        `propval_tuple` -- a tuple (pair) whose first item identifies the `prop` and the second item the `value` to look for."""
        prop, val = propval_tuple
        return val in self._dicts[prop]

    def update_item(self, obj):
        """
        Updates `obj`'s property values, so it will be indexed using its current values.

        Needs to be called manually every time `obj` was altered.
        """
        prop_results = {(prop, getattr(obj, prop)) for prop in self._properties}
        prev_prop_results = set(self._propdict[obj].items())
        for (prop, val) in (prev_prop_results - prop_results):
            del self._dicts[prop][val]
        for (prop, val) in (prop_results - prev_prop_results):
            self._dicts[prop][val] = obj
        self._propdict[obj] = prop_results

    def clear(self):
        """Completely empties the state of this MultiIndexedCollection"""
        self._dicts = self._dict_type([(prop, self._dict_type()) for prop in properties])
        self._propdict = self._dict_type()

    def copy(self):
        """Creates a shallow copy of this MultiIndexedCollection.

        (The items contained are not copied but instead referenced)"""
        other = self.__class__(self._properties, dict_type=self._dict_type)
        other._propdict = self._propdict.copy()
        other._dicts = self.dicts.copy()

    def values(self, prop=None):
        """
        When the optional `prop` arguments is not given, it will return all contained objects.

        Otherwise, it will only return objects that have the property `prop`.
        """
        if prop:
            return self._dicts[prop].keys()
        else:
            return self._propdict.keys()

    def items(self, prop):
        """Returns an iterator of all items stored in this collection"""
        return self._dicts[prop].items()

    def keys(self, prop=None):
        """Returns an iterator of all values of the given property.

        When the optional `prop` is not given, it will return an iterator of all property names.
        """
        if prop:
            return self._propdict.keys()
        else:
            return self._dicts[prop].keys()

    def items_props(self):
        """An iterator of all contained items as tuples, where the key is the item, and the value is a dictionary of (property names->property values)"""
        return self._propdict.items()

    def properties(self):
        """Returns the property names that this MultiIndexedCollection was initialized with."""
        return self._properties

    def __iter__(self):
        """Maybe somewhat surprisingly, iterates over all objects inside the MultiIndexedCollection"""
        return self._propdict.keys()

    def __contains__(self, item):
        """True if `item` is contained in this collection."""
        return item in self._propdict

    def get(self, prop, value, d=None):
        """Attempts to retrieve the item whose `prop` is `value`, but returns `d` as default if it could not be found."""
        return self._dicts[prop].get(value, d=default)


    # TODO Per https://docs.python.org/3.6/reference/datamodel.html#emulating-container-types we should add(?):
    # -pop
    # -popitem
    # -update


if __name__ == "__main__":
    class User():
        def __init__(self, uid, name):
            self.uid = uid
            self.name = name

    mic = MultiIndexedCollection({'uid', 'name'})
    qqwy = User(1, 'Qqwy')
    pete = User(2, 'Pete')
    john = User(3, 'John')
    mic.add(qqwy)
    mic.add(pete)
    mic.add(john)

    print(mic._propdict)
    print(mic._dicts)

    print(mic['uid', 1])
    print(mic['uid', 2])
    print(mic['name', 'Qqwy'])

    mic.remove(john)
    # mic.remove(john)
    # print(mic['name', 'John'])
