





Utilities
==========
set settings on config.ini

Conversion tools
----------------

For converting between btco/btco/xrb/rai amounts.

The :meth:`btco.conversion.convert` function takes ``int``, ``Decimal`` or ``string`` arguments (no ``float``):

.. code-block:: python

    >>> from modules.btco import convert
    >>> convert(12, from_unit='BTCO', to_unit='raw')
    Decimal('1.2E+31')

    >>> convert(0.4, from_unit='kbtco', to_unit='BTCO')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: float values can lead to unexpected
    precision loss, please use a Decimal or string
    eg. convert('0.4', 'kbtco', 'BTCO')

    >>> convert('0.4', from_unit='kbtco', to_unit='BTCO')
    Decimal('0.0004')



.. WARNING::
   Careful not to mix up ``'BTCO'`` and ``'btco'`` as they are different units

    >>> convert(2000000000000000000000000, 'raw', 'BTCO')
    Decimal('0.000002')
    >>> convert(2000000000000000000000000, 'raw', 'btco')
    Decimal('2')

For a dict of all available units and their amount in raw:

    >>> from modules.btco import UNITS_TO_RAW
    >>> UNITS_TO_RAW
    {'Gbtco': Decimal('1000000000000000000000000000000000'),
     'Grai': Decimal('1000000000000000000000000000000000'),
     'Gxrb': Decimal('1000000000000000000000000000000000'),
     'Mbtco': Decimal('1000000000000000000000000000000'),
     'Mrai': Decimal('1000000000000000000000000000000'),
     'Mxrb': Decimal('1000000000000000000000000000000'),
     'BTCO': Decimal('1000000000000000000000000000000'),
     'XRB': Decimal('1000000000000000000000000000000'),
     'kbtco': Decimal('1000000000000000000000000000'),
     'krai': Decimal('1000000000000000000000000000'),
     'kxrb': Decimal('1000000000000000000000000000'),
     'mbtco': Decimal('1000000000000000000000'),
     'mrai': Decimal('1000000000000000000000'),
     'mxrb': Decimal('1000000000000000000000'),
     'btco': Decimal('1000000000000000000000000'),
     'rai': Decimal('1000000000000000000000000'),
     'raw': Decimal('1'),
     'ubtco': Decimal('1000000000000000000'),
     'urai': Decimal('1000000000000000000'),
     'uxrb': Decimal('1000000000000000000'),
     'xrb': Decimal('1000000000000000000000000')}

