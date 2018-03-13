# Multi Indexed Collection

A collection type for arbitrary objects, that indexes them based on (a subset of) their properties.
Which properties to look for is specified during the initialization of the MultiIndexedCollection;
any hashable objects can be stored inside.

removing/updating objects is also supported.
The MultiIndexedCollection will _not_ automatically know when an object is changed, so calling `update` manually is necessary in that case.

Optionally, custom dictionary-types can be used, which is nice if you have some special requirements for your dictionary types.
