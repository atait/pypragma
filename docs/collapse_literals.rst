Collapse Literals
=================

.. autofunction:: pragma.collapse_literals

Collapse literal operations in code to their results, e.g. ``x = 1 + 2`` gets converted to ``x = 3``.

For example::

    @pragma.collapse_literals
    def f(y):
        x = 3
        return x + 2 + y

    # ... Becomes ...

    def f(y):
        x = 3
        return 5 + y

This is capable of resolving expressions of numerous sorts:

- A variable with a known value is replaced by that value
- An iterable with known values (such as one that could be unrolled by :func:`pragma.unroll`), if indexed, is replaced with the value at that location
- A unary, binary, or logical operation on known values is replaced by the result of that operation on those values
- A `if/elif/else` block is trimmed of options that are known at decoration-time to be impossible. If it can be known which branch runs at decoration time, then the conditional is removed altogether and replaced with the body of that branch

If a branch is constant, and thus known at decoration time, then only the correct branch will be left::

    @pragma.collapse_literals
    def f():
        x = 1
        if x > 0:
            x = 2
        return x

    # ... Becomes ...

    def f():
        x = 1
        x = 2
        return 2

This decorator is actually very powerful, understanding any definition-time known collections, primitives, or even dictionaries. Subscripts are resolved if the list or dictionary, and the key into it, can be resolved. Names are replaced by their values if they are not containers (since re-writing a container, such as a tuple or list, could duplicate object references). Functions, such as ``len`` and ``sum`` can be computed and replaced with their value if their arguments are known.

.. todo:: Always commit changes within a block, and only mark values as non-deterministic outside of conditional blocks
.. todo:: Support list/set/dict comprehensions
.. todo:: Attributes are too iffy, since properties abound, but assignment to a known index of a known indexable should be remembered
