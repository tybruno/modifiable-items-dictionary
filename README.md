[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Code Style: Blue](https://img.shields.io/badge/code%20style-blue-0000ff.svg)](https://github.com/psf/blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/tybruno/modifiable-items-dictionary/branch/main/graph/badge.svg?token=ZO94EJFI3G)](https://codecov.io/gh/tybruno/modifiable-items-dictionary)

# modifiable-items-dict

A simple, fast, typed, and tested implementation for a python3.6+ Modifiable Items dictionary. `ModifiableItemsDict`
extends `dict` with the ability to modify keys and values on creation, insertion, and retrieval. This class extends and
maintains the original functionality of the builtin `dict`.

In addition to `ModifiableItemsDict`, this implementation also includes `ModifiableItemsAttrDict`,
a class that inherits from `ModifiableItemsDict` and adds attribute-style access to dictionary items.
This means you can access dictionary items as if they were attributes of the object, providing an alternative,
often more readable way to access dictionary items.
Like `ModifiableItemsDict`, `ModifiableItemsAttrDict` also allows modification of keys and values on creation,
insertion, and retrieval, ensuring consistency and flexibility in handling dictionary items.

#### Key Features:

* **Easy**: Flexible and easy to add Key and/or Value modifiers to
  the `ModifiableItemsDict` and `ModifiableItemsAttrDict`.
* **Attribute Access**: `ModifiableItemsAttrDict` allows attribute-style access to dictionary items, providing an
  alternative, often more readable way to access dictionary items.
* **Great Developer Experience**: Being fully typed makes it great for editor
  support.
* **Fully Tested**: Our test suite fully tests the functionality to ensure
  that `ModifiableItemsDict` and `ModifiableItemsAttrDict` run as expected.
* **There is More!!!**:
    * [CaselessDict](https://github.com/tybruno/caseless-dictionary): `CaselessDict`
      extends `ModifiableItemsDict` and `ModifiableItemsAttrDict` which
      is a `CaselessDict`  and `CaselessAttrDict` that ignores the case of the keys.

## Installation

`pip install modifiable-items-dictionary`

## ModifiableItemsDict and ModifiableItemsAttrDict

The `ModifiableItemsDict` and `ModifiableItemsAttrDict` classes are part of the `modifiable_items_dictionary` module.
They provide advanced dictionary functionalities with additional features for modifying keys and values.

### ModifiableItemsDict

The `ModifiableItemsDict` class is a dictionary class that allows modification of keys and values during creation,
insertion, and retrieval. It provides the following features:

- **Key Modifiers**: This class allows you to specify functions that modify keys on creation, insertion, and retrieval.
  This can be useful for ensuring that all keys adhere to a certain format or standard.
- **Value Modifiers**: Similar to key modifiers, you can also specify functions that modify values. This can be useful
  for transforming or sanitizing data as it's added to the dictionary.
- **Thread Safety**: This class is designed to be thread-safe, making it suitable for use in multi-threaded
  applications.
- **Fully Tested**: The functionality of this class is fully tested to ensure reliable operation.

#### Example

```python
from modifiable_items_dictionary import ModifiableItemsDict


def _add_1(_value):
    if isinstance(_value, int):
        _value += 1
    return _value


def _case_fold_string(_value):
    if isinstance(_value, str):
        _value = _value.casefold()
    return _value


ModifiableItemsDict._key_modifiers = [str.casefold]
ModifiableItemsDict._value_modifiers = (
    _add_1, _case_fold_string)
# Or
# ModifiableItemsDict._key_modifiers = staticmethod(str.casefold)
# ModifiableItemsDict._value_modifiers = [_case_fold_string, _add_1]

modifiable_items_dictionary = ModifiableItemsDict(
    {"lower": 1, "UPPER": 2},
    CamelCase=3,
    snake_case="FoUR"
)

print(
    modifiable_items_dictionary
)  # {'lower': 2, 'upper': 3, 'camelcase': 4, 'snake_case': 'four'}

del modifiable_items_dictionary["LOWER"]
del modifiable_items_dictionary["UPPER"]
modifiable_items_dictionary.pop("SNAKE_CAse")

modifiable_items_dictionary["HeLLO"] = 5

print(modifiable_items_dictionary)  # {'camelcase': 4, 'hello': 6}
```

### ModifiableItemsAttrDict

The `ModifiableItemsAttrDict` class is an extension of the `ModifiableItemsDict` class, inheriting all its features
while adding attribute-style access to dictionary items. This class maintains the same key and value modifiers, ensuring
consistency and flexibility in handling dictionary items.

Like `ModifiableItemsDict`, `ModifiableItemsAttrDict` is designed with thread safety in mind, making it suitable for use
in multi-threaded applications. It is also fully tested to ensure reliable operation.

In addition to these features, `ModifiableItemsAttrDict` offers:

- **Attribute-style Access**: This feature allows you to access dictionary items as if they were attributes of the
  object. For example, you can use `dict.key` instead of `dict['key']`. This provides an alternative, often more
  readable way to access dictionary items, while still retaining the traditional dictionary access methods.

This combination of features makes `ModifiableItemsAttrDict` a powerful tool for managing dictionaries in a way that is
both flexible and intuitive, while maintaining the robustness and reliability of the `ModifiableItemsDict` class.

#### Example

```python
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
print(modifiable_items_attr_dict.hELlo)  # 6
print(modifiable_items_attr_dict)  # {'camelcase': 4, 'hello': 6}
```

## Use Case Example

Let's say that there is a `.json` file that has Url hosts and their IP address.
Our Goal is to load the json data into a dictionary like structure that will
have it's items modified during creation,
insertion, and retrieval.
This example highlights how to inherit from `ModifiableItemsDict` and had key
and value modifiers.

```python
import ipaddress

from modifiable_items_dictionary import ModifiableItemsDict


class HostDict(ModifiableItemsDict):
    _key_modifiers = [str.casefold, str.strip]
    _value_modifiers = [ipaddress.ip_address]
    # Or
    # _value_modifiers = @staticmethod(ipaddress.ip_address)


browsers = HostDict(
    {
        "  GooGle.com    ": "142.250.69.206",
        " duckDUCKGo.cOM   ": "52.250.42.157",
    }
)

print(browsers)
# {'google.com': IPv4Address('142.250.69.206'), 'duckduckgo.com': IPv4Address('52.250.42.157')}

_old_browser = browsers.pop("  gOOgle.com  ")
# or 
# del host_dict["   GooGle.com  "]

browsers["   BrAvE.com   "] = "2600:9000:234c:5a00:6:d0d2:780:93a1"

print(browsers)
# {'duckduckgo.com': IPv4Address('52.250.42.157'), 'brave.com': IPv6Address('2600:9000:234c:5a00:6:d0d2:780:93a1')}
```

### Threading Example

It is easy to add Threading to a `ModifiableItemsDict`.

*NOTE: Since `ModifiableItemsDict` is not pickable it does not work with
Multiprocessing. It only works with Multithreading.*

```python
import multiprocessing.pool
import string
import time

from modifiable_items_dictionary import ModifiableItemsDict

pool = multiprocessing.pool.ThreadPool(10)


def _slow_function(x):
    time.sleep(.05)
    return x


class TimeDictWithThreading(ModifiableItemsDict):
    _key_modifiers = (_slow_function,)
    _value_modifiers = (_slow_function,)
    _map_function = pool.imap_unordered
    # or if order matters
    # _map_function = pool.imap


class TimeDict(ModifiableItemsDict):
    _key_modifiers = (_slow_function,)
    _value_modifiers = (_slow_function,)


iterable = {_letter: _index for _index, _letter in
            enumerate(string.ascii_letters)}

# Without Threading
start = time.perf_counter()
TimeDict(iterable)
end = time.perf_counter()
print(f"{end - start:.2f} seconds")  # 5.54 seconds

# With Threading
start = time.perf_counter()
TimeDictWithThreading(iterable)
end = time.perf_counter()
print(f"{end - start:.2f} seconds")  # 0.64 seconds
```

## Reference

This project was inspired by Raymond
Hettinger ([rhettinger](https://github.com/rhettinger)).

- Hettinger, R. (2023). (Advanced) Python For Engineers: Part 3.
