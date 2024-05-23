"""This module contains examples of how to use the
`modifiable_items_dictionary` module.

The `modifiable_items_dictionary` module provides two classes:
    - `ModifiableItemsDict`: A dictionary class that can modify keys and
        values at runtime.
    - `ModifiableItemsAttrDict`: A dictionary class that allows
        attribute-style access to its items.

This module contains examples of how to use these classes.
"""
import ipaddress
import multiprocessing.pool
import string
import time

import modifiable_items_dictionary


def simple_example():
    import modifiable_items_dictionary

    def _add_1(_value):
        if isinstance(_value, int):
            _value += 1
        return _value

    def _case_fold_string(_value):
        if isinstance(_value, str):
            _value = _value.casefold()
        return _value

    modifiable_items_dictionary.ModifiableItemsDict._key_modifiers = [
        str.casefold
    ]
    modifiable_items_dictionary.ModifiableItemsDict._value_modifiers = (
        _add_1,
        _case_fold_string,
    )
    # Or
    # modifiable_items_dict.ModifiableItemsDict._key_modifiers = staticmethod(_lower)
    # modifiable_items_dict.ModifiableItemsDict._value_modifiers = [_lower, _add_1]

    modifiable_items_dict = modifiable_items_dictionary.ModifiableItemsDict(
        {'lower': 1, 'UPPER': 2}, CamelCase=3, snake_case='FoUR'
    )

    print(
        modifiable_items_dict
    )  # {'lower': 2, 'upper': 3, 'camelcase': 4, 'snake_case': 'four'}

    del modifiable_items_dictionary['LOWER']
    del modifiable_items_dictionary['UPPER']
    modifiable_items_dict.pop('SNAKE_CAse')

    modifiable_items_dict['HeLLO'] = 5

    print(modifiable_items_dict)  # {'camelcase': 4, 'hello': 6}


def modifiable_items_attr_dict_example():
    """This example shows how to use `ModifiableItemsAttrDict`."""
    import modifiable_items_dictionary

    def _add_1(_value):
        if isinstance(_value, int):
            _value += 1
        return _value

    def _case_fold_string(_value):
        if isinstance(_value, str):
            _value = _value.casefold()
        return _value

    modifiable_items_dictionary.ModifiableItemsAttrDict._key_modifiers = [
        str.casefold
    ]
    modifiable_items_dictionary.ModifiableItemsAttrDict._value_modifiers = (
        _add_1,
        _case_fold_string,
    )

    modifiable_items_attr_dict = (
        modifiable_items_dictionary.ModifiableItemsAttrDict(
            {'lower': 1, 'UPPER': 2}, CamelCase=3, snake_case='FoUR'
        )
    )

    print(
        modifiable_items_attr_dict
    )  # {'lower': 2, 'upper': 3, 'camelcase': 4, 'snake_case': 'four'}

    # Key-based access
    del modifiable_items_attr_dict['LOWER']
    modifiable_items_attr_dict['HeLLO'] = 5

    # Attribute-based access
    del modifiable_items_attr_dict.UPPER
    modifiable_items_attr_dict.HeLLO = 6
    print(modifiable_items_attr_dict.hELlo)   # 6
    print(modifiable_items_attr_dict)  # {'camelcase': 4, 'hello': 6}


def simple_inheritance_example():
    """This example shows how to create a Host Dictionary that will casefold keys, strip keys, and convert values to ip addresses"""

    # Inherit from `ModifiableItemsDict` and set the `_key_modifiers` and `_value_modifiers` class variables.
    class HostDict(modifiable_items_dictionary.ModifiableItemsDict):
        _key_modifiers = [str.casefold, str.strip]
        _value_modifiers = [ipaddress.ip_address]
        # Or
        # _value_modifiers = @staticmethod(ipaddress.ip_address)

    browsers = HostDict(
        {
            '  GooGle.com    ': '142.250.69.206',
            ' duckDUCKGo.cOM   ': '52.250.42.157',
        }
    )

    print(
        browsers
    )  # {'google.com': IPv4Address('142.250.69.206'), 'duckduckgo.com': IPv4Address('52.250.42.157')}

    _old_browser = browsers.pop('  gOOgle.com  ')
    # or
    # del host_dict["   GooGle.com  "]

    browsers['   BrAvE.com   '] = '2600:9000:234c:5a00:6:d0d2:780:93a1'

    print(browsers)
    # {'duckduckgo.com': IPv4Address('52.250.42.157'), 'brave.com': IPv6Address('2600:9000:234c:5a00:6:d0d2:780:93a1')}


def threading_example():
    """This example shows how to use Threading with `ModifiableItemsDict`."""

    pool = multiprocessing.pool.ThreadPool(10)

    def _slow_function(x):
        time.sleep(0.05)
        return x

    class TimeDictWithThreading(
        modifiable_items_dictionary.ModifiableItemsDict
    ):
        _key_modifiers = (_slow_function,)
        _value_modifiers = (_slow_function,)
        _map_function = pool.imap_unordered
        # or if order matters
        # _map_function = pool.imap

    class TimeDict(modifiable_items_dictionary.ModifiableItemsDict):
        _key_modifiers = (_slow_function,)
        _value_modifiers = (_slow_function,)

    iterable = {
        _letter: _index for _index, _letter in enumerate(string.ascii_letters)
    }

    # Without Threading
    start = time.perf_counter()
    TimeDict(iterable)
    end = time.perf_counter()
    print(f'{end - start:.2f} seconds')  # 5.54 seconds

    # With Threading
    start = time.perf_counter()
    TimeDictWithThreading(iterable)
    end = time.perf_counter()
    print(f'{end - start:.2f} seconds')  # 0.64 seconds


def main():
    simple_example()
    simple_inheritance_example()
    threading_example()


if __name__ == '__main__':
    main()
