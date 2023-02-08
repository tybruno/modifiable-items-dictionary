"""
Modifiable Items Dictionary and related objects.

Objects provided by this module:
   `ModifiableItemsDict` - Adds the ability to modify key's and value's on creation, insertion, and retrieval
"""
import contextlib
from multiprocessing.pool import ThreadPool
from typing import (
    Any,
    Callable,
    Hashable,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
    ItemsView,
)

# Sentinel
_OPTIONAL = object()

# Typing
_SELF = TypeVar("_SELF", bound="ModifiableItemsDict")

_TYPE = TypeVar("_TYPE")

_MAP_FUNCTION = Union[
    map, ThreadPool.map, ThreadPool.imap, ThreadPool.imap_unordered
]

_KEY = Hashable
_VALUE = Any

_KEY_CALLABLE = Callable[[Any], _KEY]
_VALUE_CALLABLE = Callable[[Any], _VALUE]

_KEY_MODIFIERS = Optional[
    Union[_SELF, _KEY_CALLABLE, Iterable[_KEY_CALLABLE], None]
]
_VALUE_MODIFIERS = Optional[
    Union[_SELF, _VALUE_CALLABLE, Iterable[_VALUE_CALLABLE], None]
]


class ModifiableItemsDict(dict):
    """Dictionary class that can modify __key and v at runtime.

    ModifiableItemsDict() -> new empty modifiable __item's dictionary
    ModifiableItemsDict(mapping) -> new modifiable __item's dictionary initialized from a mapping object's
        (__key, v) pairs
    ModifiableItemsDict(__m) -> new modifiable __item's dictionary initialized as if via:
        d = ModifiableItemsDict()
        for k, v in __m:
            d[k] = v
    ModifiableItemsDict(**kwargs) -> new modifiable __item's dictionary initialized with the name=v pairs
        in the keyword argument list.  For example:  ModifiableItemsDict(one=1, two=2)

    Note: multithreading.pool.Pool doesn't work because a dict is not pickable but multhreading.pool.ThreadPool
    is because it doesn't need to pickle
    """

    __slots__ = ()

    # TODO: Add validators
    _key_modifiers: _KEY_MODIFIERS = None
    _value_modifiers: _VALUE_MODIFIERS = None
    _map_function: _MAP_FUNCTION = map

    @staticmethod
    def _modify_item(
        item: Any,
        modifiers: Union[
            Iterable[Callable[[Any], Hashable]],
            Iterable[Callable[[Any], Any]],
            Callable[[Any], Hashable],
            Callable[[Any], Any],
            None,
        ],
    ) -> Any:
        """Modifies an *__item* with the *modifiers*

        Args:
            item: The __item that will be modified by the *modifiers*.
            modifiers: Modifiers that will modify the *__item*.

        Returns:
            The modified Item. If the modifiers are *None* return the *__item* unchanged.
        """
        if not modifiers:
            return item

        # Defensive Programming
        if isinstance(modifiers, str):
            _error: TypeError = TypeError(
                "Invalid Modifiers:",
                modifiers,
                "Can not be of types",
                (str,),
            )
            raise _error

        if isinstance(modifiers, Iterable):
            for modifier in modifiers:
                item = modifier(item)
            return item
        if callable(modifiers):
            item = modifiers(item)
            return item

        _error = TypeError(
            "Invalid Modifiers:",
            modifiers,
            "must be of types:",
            (Iterable, Callable),
        )
        raise _error

    def _modify_key(self, key: _KEY) -> _KEY:
        """Modify the *__key* with the __key modifiers.

        Args:
            key: Which will be modified by *self._key_modifiers*

        Returns:
            The modified *__key*.
        """
        _modified_key: _KEY = self._modify_item(key, self._key_modifiers)
        return _modified_key

    def _modify_value(self, value: _VALUE) -> _VALUE:
        """Modify the *v* with the v modifiers.

        Args:
            value: Which will be modified by *self._value_modifiers*

        Returns:
            The modified *v*
        """
        _modified_value: _VALUE = self._modify_item(
            value, self._value_modifiers
        )
        return _modified_value

    def _modify_key_and_item(
        self, key_and_value: Tuple[_KEY, _VALUE]
    ) -> Tuple[_KEY, _VALUE]:
        _key, _value = key_and_value
        if self._key_modifiers:
            _key = self._modify_key(_key)
        if self._value_modifiers:
            _value = self._modify_value(_value)
        return _key, _value

    @overload
    def _create_modified_mapping(
        self, items_view: ItemsView[_KEY, _VALUE]
    ) -> Mapping[_KEY, _VALUE]:
        ...

    @overload
    def _create_modified_mapping(
        self, iterable: Iterable[Tuple[_KEY, _VALUE]]
    ) -> Mapping[_KEY, _VALUE]:
        ...

    def _create_modified_mapping(self, iterable):
        """Create the modified mapping from the *Iterable*.

        Args:
            iterable: Which will be converted to a new mapping which has had it's keys and values modified.

        Returns:
            Dictionary with the modified keys and values.
        """

        new_mapping: Mapping[_KEY, _VALUE] = {
            key: value
            for key, value in self._map_function(
                self._modify_key_and_item, iterable
            )
        }

        return new_mapping

    def _iterable_to_modified_dict(
        self, iterable: Iterable
    ) -> Mapping[_KEY, _VALUE]:
        """Convert an *iterable* to a *Mapping* that has had it's keys and values modified.

        Args:
            iterable: *Iterable* that will be converted to a *Mapping* which has had it's items modified.

        Returns:
            Modified Mapping of the items.
        """
        if isinstance(iterable, Mapping):
            iterable = self._create_modified_mapping(iterable.items())
        elif isinstance(iterable, Iterable):
            iterable = self._create_modified_mapping(iterable)

        return iterable

    @classmethod
    def fromkeys(
        cls,
        __iterable: Iterable[_KEY],
        __value: Optional[Union[_VALUE, None]] = None,
    ) -> _SELF:
        return cls(dict.fromkeys(__iterable, __value))

    @overload
    def __init__(self, **kwargs: _VALUE) -> None:
        ...

    @overload
    def __init__(
        self, mapping: Mapping[_KEY, _VALUE], **kwargs: _VALUE
    ) -> None:
        ...

    @overload
    def __init__(
        self, iterable: Iterable[Tuple[str, Any]], **kwargs: _VALUE
    ) -> None:
        ...

    def __init__(
        self,
        iterable=None,
        **kwargs,
    ):
        # If there is a ValueError have the inherited class deal with it.
        with contextlib.suppress(ValueError):
            if iterable:
                iterable = self._iterable_to_modified_dict(iterable)
            if kwargs:
                kwargs = self._iterable_to_modified_dict(kwargs)

        dict.__init__(self, iterable or dict(), **kwargs)

    def __getitem__(self, k: _KEY) -> Any:
        k = self._modify_key(k)
        return dict.__getitem__(self, k)

    def __setitem__(self, k: _KEY, v: _VALUE) -> None:
        k = self._modify_key(k)
        v = self._modify_value(v)
        dict.__setitem__(self, k, v)

    def __delitem__(self, v: _KEY) -> None:
        v = self._modify_key(v)
        dict.__delitem__(self, v)

    def __contains__(self, __item: _VALUE) -> bool:
        __item = self._modify_key(__item)
        _is_in: bool = dict.__contains__(self, __item)
        return _is_in

    def setdefault(self, __key: _KEY, __default: _VALUE = None) -> None:
        __key = self._modify_key(__key)
        __default = self._modify_value(__default)
        dict.setdefault(self, __key, __default)

    @overload
    def pop(self, __key: _KEY) -> _VALUE:
        ...

    @overload
    def pop(self, __key: _KEY, default: _VALUE = ...) -> _VALUE:
        ...

    def pop(self, __key, default=_OPTIONAL) -> _VALUE:
        __key = self._modify_key(__key)

        if default is _OPTIONAL:
            value: _VALUE = dict.pop(self, __key)
        else:
            value: _VALUE = dict.pop(self, __key, default)

        return value

    @overload
    def get(self, __key: _KEY) -> Union[_VALUE, None]:
        ...

    @overload
    def get(self, __key: _KEY, default: _VALUE = None) -> _VALUE:
        ...

    def get(self, __key: _KEY, default=None):
        __key = self._modify_key(__key)
        value: Union[_VALUE, None] = dict.get(self, __key, default)
        return value

    @overload
    def update(self, __m: Mapping[_KEY, _VALUE], **kwargs: _VALUE) -> None:
        ...

    @overload
    def update(
        self, __m: Iterable[Tuple[str, Any]], **kwargs: _VALUE
    ) -> None:
        ...

    @overload
    def update(self, **kwargs: _VALUE) -> None:
        ...

    def update(
        self,
        __m=None,
        **kwargs,
    ):
        # If there is a ValueError have the inherited class deal with it.
        with contextlib.suppress(ValueError):
            if __m:
                __m = self._iterable_to_modified_dict(__m)
            if kwargs:
                kwargs = self._iterable_to_modified_dict(kwargs)

        dict.update(self, __m or dict(), **kwargs)
