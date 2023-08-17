import ipaddress
import multiprocessing.pool
import string
import time

import modifiable_items_dict


def simple_inheritance_example():
    """This example shows how to create a Host Dictionary that will casefold keys, strip keys, and convert values to ip addresses

    """

    # Inherit from `ModifiableItemsDict` and set the `_key_modifiers` and `_value_modifiers` class variables.
    class HostDict(modifiable_items_dict.ModifiableItemsDict):
        _key_modifiers = [str.casefold, str.strip]
        _value_modifiers = [ipaddress.ip_address]
        # Or
        # _value_modifiers = @staticmethod(ipaddress.ip_address)

    browsers = HostDict({"  GooGle.com    ": "142.250.69.206", " duckDUCKGo.cOM   ": "52.250.42.157"})

    print(browsers)  # {'google.com': IPv4Address('142.250.69.206'), 'duckduckgo.com': IPv4Address('52.250.42.157')}

    _old_browser = browsers.pop("  gOOgle.com  ")
    # or
    # del host_dict["   GooGle.com  "]

    browsers["   BrAvE.com   "] = "2600:9000:234c:5a00:6:d0d2:780:93a1"

    print(
        browsers)
    # {'duckduckgo.com': IPv4Address('52.250.42.157'), 'brave.com': IPv6Address('2600:9000:234c:5a00:6:d0d2:780:93a1')}


def threading_example():
    """This example shows how to use Threading with `ModifiableItemsDict`."""

    pool = multiprocessing.pool.ThreadPool(10)

    def _slow_function(x):
        time.sleep(.05)
        return x

    class TimeDictWithThreading(modifiable_items_dict.ModifiableItemsDict):
        _key_modifiers = (_slow_function,)
        _value_modifiers = (_slow_function,)
        _map_function = pool.imap_unordered
        # or if order matters
        # _map_function = pool.imap

    class TimeDict(modifiable_items_dict.ModifiableItemsDict):
        _key_modifiers = (_slow_function,)
        _value_modifiers = (_slow_function,)

    iterable = {_letter: _index for _index, _letter in enumerate(string.ascii_letters)}

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
