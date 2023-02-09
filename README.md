[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-blueviolet.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/tybruno/modifiable-items-dictionary/branch/main/graph/badge.svg?token=ZO94EJFI3G)](https://codecov.io/gh/tybruno/modifiable-items-dictionary)
# modifiable-items-dict
A simple, fast, typed, and tested implementation for a python3.6+ Modifiable Items dictionary. `ModifiableItemsDict` extends `dict` with the ability to modify key's and value's on creation, insertion, and retrieval. 
This class extends and maintains the original functionality of the builtin `dict`.

#### Key Features:
* **Easy**: Flexable and easy to add Key and/or Value modifiers to the `ModifiableItemsDict`
* **Great Developer Experience**: Being fully typed makes it great for editor support.
* **Fully Tested**: Our test suit fully tests the functionality to ensure that `ModifiableItemsDict` runs as expected.
* **There is More!!!**:
    * [CaselessDict](https://github.com/tybruno/caseless-dictionary): `CaselessDict` extends `ModifiableItemsDict` which is a `CaselessDict` which ignores the case of the keys.

## Installation
`pip install modifiable-items-dictionary`

## Simple Example
```python
from modifiable_items_dict import ModifiableItemsDict


def _lower(_key):
    if isinstance(_key, str):
        _key = _key.lower()
    return _key


def _add_1(_value):
    if isinstance(_value, int):
        _value += 1
    return _value


ModifiableItemsDict._key_modifiers = [_lower]
ModifiableItemsDict._value_modifiers = (_lower, _add_1)
# Or
# ModifiableItemsDict._key_modifiers = staticmethod(_lower)
# ModifiableItemsDict._value_modifiers = [_lower, _add_1]

modifiable_items_dict = ModifiableItemsDict({"lower":1, "UPPER":2 }, CamelCase=3, snake_case="FoUR")

print(modifiable_items_dict) # {'lower': 2, 'upper': 3, 'camelcase': 4, 'snake_case': 'four'}

del modifiable_items_dict["LOWER"]
del modifiable_items_dict["UPPER"]
modifiable_items_dict.pop("SNAKE_CAse")

modifiable_items_dict["HeLLO"] = 5

print(modifiable_items_dict) # {'camelcase': 4, 'hello': 6}

```
## Example
Let's say that there is a `.json` file that has Url hosts and their IP address. 
Our Goal is to load the json data into a dictionary like structure that will have it's items modified during creation, insertion, and retrieval. 
This example highlights how to inherit from `ModifiableItemsDict` and had key and value modifiers. 
```python
import contextlib
import ipaddress
import json
from typing import Any, Union

from modifiable_items_dict import ModifiableItemsDict

def _strip(_value: Any):
    if isinstance(_value, str):
        _value = _value.strip()
        return _value
    return _value


def _case_fold(_value: Any) -> Any:
    if isinstance(_value, str):
        _case_folded_string: str = _value.casefold()
        return _case_folded_string
    return _value

def _to_ipaddress(_value: Any) -> Any:
    if isinstance(_value, str):
        with contextlib.suppress(ValueError):
            _ip_address: Union[
                ipaddress.IPv4Address, ipaddress.IPv6Address
            ] = ipaddress.ip_address(_value)
            return _ip_address

    return _value

class HostDict(ModifiableItemsDict):
    _key_modifiers = [_strip, _case_fold]
    _value_modifiers = [_to_ipaddress]
    # Or
    # _value_modifiers = @staticmethod(_to_ipaddress)

_json: str = '{"  GooGle.com    ": "142.250.69.206", " duckDUCKGo.cOM   ": "52.250.42.157"}'

host_dict: HostDict = json.loads(_json, object_hook=HostDict)

print(host_dict) # {'google.com': IPv4Address('142.250.69.206'), 'duckduckgo.com': IPv4Address('52.250.42.157')}

_old_browser = host_dict.pop("  gOOgle.com  ")
# or 
# del host_dict["   GooGle.com  "]

host_dict["   BrAvE.com   "] = "2600:9000:234c:5a00:6:d0d2:780:93a1"

print(host_dict) # {'duckduckgo.com': IPv4Address('52.250.42.157'), 'brave.com': IPv6Address('2600:9000:234c:5a00:6:d0d2:780:93a1')}
```

### Threading Example
It is easy to add Threading to a `ModifiableItemsDict`. 

*NOTE: Since `ModifiableItemsDict` is not pickable it does not work with Multiprocessing.*
```python
from multiprocessing.pool import ThreadPool as Pool
from string import ascii_letters
from time import perf_counter, sleep

from modifiable_items_dict.modifiable_items_dict import ModifiableItemsDict

pool = Pool(10)


def _slow_function(x):
    sleep(.05)
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

iterable = {_letter: _index for _index, _letter in enumerate(ascii_letters)}

# Without Threading
start = perf_counter()
TimeDict(iterable)
end = perf_counter()
print(f"{end - start:.2f} seconds")  # 5.54 seconds

# With Threading
start = perf_counter()
TimeDictWithThreading(iterable)
end = perf_counter()
print(f"{end - start:.2f} seconds")  # 0.64 seconds
```