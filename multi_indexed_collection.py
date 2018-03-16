
# These names are skipped during __setattr__ wrapping; they do not cause the containers to be updated.
_RESTRICTED_NAMES = [
    '_multi_indexed_collections', '__setattr__',
    '__dict__', '__class__'
]
class AutoUpdatingItem():
    """When mixing in this class
    all changes to properties on the object cause the `MultiIndexedCollection`s it is contained in
    to automatically re-compute the keys of the object, so manually calling `collection.update(obj)` is no longer required.

    This is implemented by wrapping `__setattr__` with a custom implementation that calls `collection.update(obj)` every time a property changes.

    >>>
    >>> class AutoUser(AutoUpdatingItem):
    ...     def __init__(self, name, user_id):
    ...         self.name = name
    ...         self.user_id = user_id
    >>> autojohn = AutoUser('John', 1)
    >>> autopete = AutoUser('Pete', 2)
    >>> autolara = AutoUser('Lara', 3)
    >>>
    >>>
    >>> mic = MultiIndexedCollection({'user_id', 'name'})
    >>> mic.add(autojohn)
    >>> mic.add(autopete)
    >>> len(mic)
    2
    >>> mic.find('name', 'John') == autojohn
    True
    >>> autojohn.name = 'Johnny'
    >>> mic.get('name', 'Johnny', False) == autojohn
    True
    >>> mic.get('name', 'John', False)
    False
    """

    def __new__(cls, *args, **kwargs):
        inst = super(AutoUpdatingItem, cls).__new__(cls)
        # Skips below implementation of __setattr__ here.
        super(AutoUpdatingItem, inst).__setattr__('_multi_indexed_collections', [])
        return inst

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in _RESTRICTED_NAMES:
            for collection in self._multi_indexed_collections:
                collection.update_item(self)


class MultiIndexedCollection():
    """
    A collection type for arbitrary objects, that indexes them based on (a subset of) their properties.
    Which properties to look for is specified during the initialization of the MultiIndexedCollection;
    any hashable objects can be stored inside.

    removing/updating objects is also supported.
    The MultiIndexedCollection will _not_ automatically know when an object is changed, so calling `update` manually is necessary in that case.

    Optionally, custom dictionary-types can be used, which is nice if you have some special requirements for your dictionary types.


    >>> # Most example code uses the following class and data as example:
    >>> class User():
    ...     def __init__(self, name, user_id):
    ...         self.name = name
    ...         self.user_id = user_id
    >>>
    >>> john = User('John', 1)
    >>> pete = User('Pete', 2)
    >>> lara = User('Lara', 3)
    >>>
    >>>
    >>> mic = MultiIndexedCollection({'user_id', 'name'})
    >>> mic.add(john)
    >>> mic.add(pete)
    >>> len(mic)
    2
    >>> mic.find('name', 'John') == john
    True
    >>> mic['name', 'Pete'] == pete
    True
    >>> mic['name', 'NotInThere']
    Traceback (most recent call last):
        ...
    KeyError: '`name`=`NotInThere`'
    >>> ('name', 'John') in mic
    True
    >>> ('user_id', 2) in mic
    True
    >>> ('user_id', 42) in mic
    False
    """

    def __init__(self, properties, dict_type=dict, auto_update=False):
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
        self._auto_update = auto_update

    def add(self, obj):
        """
        Adds `obj` to the collection,
        so it can later be found under all its properties' values.


        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> mic.add(john)
        >>> mic.add(pete)
        >>> len(mic)
        2
        >>> mic.find('name', 'John') == john
        True
        """
        if obj in self._propdict:
            return

        if isinstance(obj, AutoUpdatingItem):
            obj._multi_indexed_collections.append(self)

        prop_results = {prop: getattr(obj, prop) for prop in self._properties if hasattr(obj, prop)}
        # TODO Check for duplicate keys before altering here.
        for (prop, val) in prop_results.items() :
            if val in self._dicts[prop].keys():
                raise KeyError("Collection already contains an element with `{}`=`{}`".format(prop, val))

        for (prop, val) in prop_results.items() :
            self._dicts[prop][val] = obj
        self._propdict[obj] = prop_results

    def find(self, prop, value):
        """Finds the object whose indexed property `prop` has value `value`.

        Returns `KeyError` if this cannot be found.


        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> mic.add(john)
        >>> mic.add(pete)
        >>> len(mic)
        2
        >>> mic.find('name', 'John') == john
        True
        >>> mic.find('name', 'NotInThere')
        Traceback (most recent call last):
            ...
        KeyError: '`name`=`NotInThere`'
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


        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> mic.add(john)
        >>> mic.add(pete)
        >>>
        >>> mic['name', 'John'] == john
        True
        >>> mic['user_id', 2] == pete
        True
        >>> mic['name', 'NotInThere']
        Traceback (most recent call last):
            ...
        KeyError: '`name`=`NotInThere`'
        """
        prop, val = propval_tuple
        return self.find(prop, val)

    def remove(self, obj):
        """Removes `obj` from this collection, so it will no longer be indexed or found.

        Raises `KeyError` if `obj` is not contained in the collection.


        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> mic.add(john)
        >>> mic.add(pete)
        >>>
        >>> mic['name', 'John'] == john
        True
        >>> mic['user_id', 2] == pete
        True
        >>> mic.remove(john)
        >>>
        >>> mic.get('name', 'John', False)
        False
        >>> mic.find('name', 'John')
        Traceback (most recent call last):
            ...
        KeyError: '`name`=`John`'
        """
        if not obj in self._propdict:
            raise KeyError(obj)

        if isinstance(obj, AutoUpdatingItem):
            obj._multi_indexed_collections.remove(self)

        prop_results = self._propdict[obj]
        for (prop, val) in prop_results.items():
            del self._dicts[prop][val]
        del self._propdict[obj]

    def discard(self, obj):
        """Removes `obj` from this collection, if it is present."""
        try:
            self.remove(obj)
        except KeyError:
            pass

    def __len__(self):
        """The amount of items in the collection.


        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> len(mic)
        0
        >>> mic.add(john)
        >>> mic.add(pete)
        >>> len(mic)
        2
        """
        return len(self._propdict)

    def __length_hint__(self):
        return self._propdict.__length_hint__()

    def __contains__(self, propval_tuple):
        """True if there exists an item under the key `value` for `prop`.

        `propval_tuple` -- a tuple (pair) whose first item identifies the `prop` and the second item the `value` to look for.

        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> len(mic)
        0
        >>> mic.add(john)
        >>> mic.add(pete)
        >>> ('name', 'John') in mic
        True
        >>> ('user_id', 2) in mic
        True
        """
        prop, val = propval_tuple
        return val in self._dicts[prop]

    def update_item(self, obj):
        """
        Updates `obj`'s property values, so it will be indexed using its current values.

        Needs to be called manually every time `obj` was altered.
        Alternatively, objects who inherit from `AutoUpdatingItem` will automatically call this function
        for each MultiIndexedCollection they are part of whenever one of their properties changes.


        >>> mic = MultiIndexedCollection({'user_id', 'name'})
        >>> mic.add(john)
        >>> mic.add(pete)
        >>>
        >>> mic['name', 'John'] == john
        True
        >>> john.name = 'Johnny'
        >>> mic['name', 'John'] == john
        True
        >>> mic.update_item(john)
        >>> mic['name', 'Johnny'] == john
        True
        >>> mic['name', 'John']
        Traceback (most recent call last):
            ...
        KeyError: '`name`=`John`'

        """
        prop_results = {(prop, getattr(obj, prop)) for prop in self._properties if hasattr(obj, prop)}
        prev_prop_results = set(self._propdict[obj].items())
        old_props = (prev_prop_results - prop_results)
        new_props = (prop_results - prev_prop_results)

        # Ensure no duplicate new keys.
        for (prop, val) in new_props :
            if val in self._dicts[prop].keys():
                raise KeyError("Collection already contains an element with `{}`=`{}`".format(prop, val))

        # Remove old/deleted properties.
        for (prop, val) in old_props:
            del self._dicts[prop][val]

        # insert updated properties
        for (prop, val) in new_props:
            self._dicts[prop][val] = obj

        # Extra indirection is necessary because not all dict types can create
        # a dict directly from a set of pairs:
        self._propdict[obj] = self._dict_type(dict(prop_results))

    def clear(self):
        """Completely empties the state of this MultiIndexedCollection"""
        self._dicts = self._dict_type({prop: self._dict_type() for prop in self._properties})
        self._propdict = self._dict_type()

    def __copy__(self):
        """Creates a shallow copy of this MultiIndexedCollection.

        (The items contained are not copied but instead referenced)"""
        other = self.__class__(self._properties, dict_type=self._dict_type)
        other._propdict = self._propdict.copy()
        other._dicts = self.dicts.copy()

    def copy(self):
        """Creates a shallow copy of this MultiIndexedCollection.

        (The items contained are not copied but instead referenced)"""
        self.__copy__()

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

    def get(self, prop, value, d=None):
        """Attempts to retrieve the item whose `prop` is `value`, but returns `d` as default if it could not be found."""
        return self._dicts[prop].get(value, d)


    # TODO Per https://docs.python.org/3.6/reference/datamodel.html#emulating-container-types we should add(?):
    # -pop
    # -popitem
    # -update



# if __name__ == "__main__":
#     run_doctests({})
#     # End example data.
#     doctest.testmod()
