[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/tybruno/modifiable-items-dictionary/branch/main/graph/badge.svg?token=ZO94EJFI3G)](https://codecov.io/gh/tybruno/modifiable-items-dictionary)

# modifiable-items-dict

A simple, fast, typed, and tested implementation for a python3.6+ Modifiable
Items dictionary. `ModifiableItemsDict`
extends `dict` with the ability to modify key's and value's on creation,
insertion, and retrieval.
This class extends and maintains the original functionality of the
builtin `dict`.

#### Key Features:

* **Easy**: Flexable and easy to add Key and/or Value modifiers to
  the `ModifiableItemsDict`
* **Great Developer Experience**: Being fully typed makes it great for editor
  support.
* **Fully Tested**: Our test suit fully tests the functionality to ensure
  that `ModifiableItemsDict` runs as expected.
* **There is More!!!**:
    * [CaselessDict](https://github.com/tybruno/caseless-dictionary): `CaselessDict`
      extends `ModifiableItemsDict` which
      is a `CaselessDict` which ignores the case of the keys.

## Installation

`pip install modifiable-items-dictionary`

## Simple Example

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

## Example

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
