



.. _utilities-ref:

Utilities
==========
set settings on config.ini

Conversion tools
----------------

For converting between btco/nano/xrb/rai amounts.

The :meth:`btco.conversion.convert` function takes ``int``, ``Decimal`` or ``string`` arguments (no ``float``):

.. code-block:: python

    >>> from modules.btco import convert
    >>> convert(12, from_unit='NANO', to_unit='raw')
    Decimal('1.2E+31')

    >>> convert(0.4, from_unit='knano', to_unit='NANO')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: float values can lead to unexpected
    precision loss, please use a Decimal or string
    eg. convert('0.4', 'knano', 'NANO')

    >>> convert('0.4', from_unit='knano', to_unit='NANO')
    Decimal('0.0004')



.. WARNING::
   Careful not to mix up ``'NANO'`` and ``'nano'`` as they are different units

    >>> convert(2000000000000000000000000, 'raw', 'NANO')
    Decimal('0.000002')
    >>> convert(2000000000000000000000000, 'raw', 'nano')
    Decimal('2')

For a dict of all available units and their amount in raw:

    >>> from modules.btco import UNITS_TO_RAW
    >>> UNITS_TO_RAW
    {'Gnano': Decimal('1000000000000000000000000000000000'),
     'Grai': Decimal('1000000000000000000000000000000000'),
     'Gxrb': Decimal('1000000000000000000000000000000000'),
     'Mnano': Decimal('1000000000000000000000000000000'),
     'Mrai': Decimal('1000000000000000000000000000000'),
     'Mxrb': Decimal('1000000000000000000000000000000'),
     'NANO': Decimal('1000000000000000000000000000000'),
     'XRB': Decimal('1000000000000000000000000000000'),
     'knano': Decimal('1000000000000000000000000000'),
     'krai': Decimal('1000000000000000000000000000'),
     'kxrb': Decimal('1000000000000000000000000000'),
     'mnano': Decimal('1000000000000000000000'),
     'mrai': Decimal('1000000000000000000000'),
     'mxrb': Decimal('1000000000000000000000'),
     'nano': Decimal('1000000000000000000000000'),
     'rai': Decimal('1000000000000000000000000'),
     'raw': Decimal('1'),
     'unano': Decimal('1000000000000000000'),
     'urai': Decimal('1000000000000000000'),
     'uxrb': Decimal('1000000000000000000'),
     'xrb': Decimal('1000000000000000000000000')}

.. code-block:: python