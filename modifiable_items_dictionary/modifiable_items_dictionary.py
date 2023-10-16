"""
Modifiable Items Dictionary and related objects.

Objects provided by this module:
   `ModifiableItemsDict` - Adds the ability to modify key's and value's on
   creation, insertion, and retrieval

Reference:
This module was heavily inspired by Raymond Hettinger's class.
    [1] Hettinger, R. (2023). (Advanced) Python For Engineers: Part 3.
"""
import contextlib
import multiprocessing.pool
from typing import (
    Any,
    Callable,
    Hashable,
    ItemsView,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

# Sentinel
NO_DEFAULT = object()

# Typing
# For python 3.6 compatibility
Self = TypeVar("Self", bound="ModifiableItemsDict")

Key = Hashable
Value = Any
MappingCallable = Union[
    map, multiprocessing.pool.ThreadPool.map,
    multiprocessing.pool.ThreadPool.imap,
    multiprocessing.pool.ThreadPool.imap_unordered
]
KeyCallable = Callable[[Any], Key]
ValueCallable = Callable[[Any], Value]
KeyModifiers = Optional[
    Union[Self, KeyCallable, Iterable[KeyCallable], None]
]
ValueModifiers = Optional[
    Union[Self, ValueCallable, Iterable[ValueCallable], None]
]


class ModifiableItemsDict(dict):
    """Dictionary class that can modify __key and v at runtime.

    ModifiableItemsDict() -> new empty modifiable __item's dictionary
    ModifiableItemsDict(mapping) -> new modifiable __item's dictionary
    initialized from a mapping object's
        (__key, v) pairs
    ModifiableItemsDict(__m) -> new modifiable __item's dictionary
    initialized as if via:
        d = ModifiableItemsDict()
        for k, v in __m:
            d[k] = v
    ModifiableItemsDict(**kwargs) -> new modifiable __item's dictionary
    initialized with the name=v pairs
        in the keyword argument list.  For example:  ModifiableItemsDict(
        one=1, two=2)

    Note: `multiprocessing.pool.Pool` multiprocessing doesn't work because a
    dict is not picklable but `multiprocessing.pool.ThreadPool`
    does work since it doesn't need to pickle the object.

    Reference:
        [1] Hettinger, R. (2023). (Advanced) Python For Engineers: Part 3.
    """

    __slots__ = ()

    # TODO: Add validators
    _key_modifiers: KeyModifiers = None
    _value_modifiers: ValueModifiers = None
    _map_function: MappingCallable = map

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
            The modified Item. If the modifiers are *None* return the
            *__item* unchanged.
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

    def _modify_key(self, key: Key) -> Key:
        """Modify the *__key* with the __key modifiers.

        Args:
            key: Which will be modified by *self._key_modifiers*

        Returns:
            The modified *__key*.
        """
        _modified_key: Key = self._modify_item(key, self._key_modifiers)
        return _modified_key

    def _modify_value(self, value: Value) -> Value:
        """Modify the *v* with the v modifiers.

        Args:
            value: Which will be modified by *self._value_modifiers*

        Returns:
            The modified *v*
        """
        _modified_value: Value = self._modify_item(
            value, self._value_modifiers
        )
        return _modified_value

    def _modify_key_and_item(
            self, key_and_value: Tuple[Key, Value]
    ) -> Tuple[Key, Value]:
        _key, _value = key_and_value
        if self._key_modifiers:
            _key = self._modify_key(_key)
        if self._value_modifiers:
            _value = self._modify_value(_value)
        return _key, _value

    @overload
    def _create_modified_mapping(
            self, items_view: ItemsView[Key, Value]
    ) -> Mapping[Key, Value]:
        ...

    @overload
    def _create_modified_mapping(
            self, iterable: Iterable[Tuple[Key, Value]]
    ) -> Mapping[Key, Value]:
        ...

    def _create_modified_mapping(self, iterable):
        """Create the modified mapping from the *Iterable*.

        Args:
            iterable: Which will be converted to a new mapping which has had
            it's keys and values modified.

        Returns:
            Dictionary with the modified keys and values.
        """

        new_mapping: Mapping[Key, Value] = {
            key: value
            for key, value in self._map_function(
                self._modify_key_and_item, iterable
            )
        }

        return new_mapping

    def _iterable_to_modified_dict(
            self, iterable: Iterable
    ) -> Mapping[Key, Value]:
        """Convert an *iterable* to a *Mapping* that has had it's keys and
        values modified.

        Args:
            iterable: *Iterable* that will be converted to a *Mapping* which
            has had it's items modified.

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
            __iterable: Iterable[Key],
            __value: Optional[Union[Value, None]] = None,
    ) -> Self:
        return cls(dict.fromkeys(__iterable, __value))

    @overload
    def __init__(self, **kwargs: Value) -> None:
        ...

    @overload
    def __init__(
            self, mapping: Mapping[Key, Value], **kwargs: Value
    ) -> None:
        ...

    @overload
    def __init__(
            self, iterable: Iterable[Tuple[str, Any]], **kwargs: Value
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

    def __getitem__(self, k: Key) -> Any:
        k = self._modify_key(k)
        return dict.__getitem__(self, k)

    def __setitem__(self, k: Key, v: Value) -> None:
        k = self._modify_key(k)
        v = self._modify_value(v)
        dict.__setitem__(self, k, v)

    def __delitem__(self, v: Key) -> None:
        v = self._modify_key(v)
        dict.__delitem__(self, v)

    def __contains__(self, __item: Value) -> bool:
        __item = self._modify_key(__item)
        _is_in: bool = dict.__contains__(self, __item)
        return _is_in

    def setdefault(self, __key: Key, __default: Value = None) -> None:
        __key = self._modify_key(__key)
        __default = self._modify_value(__default)
        dict.setdefault(self, __key, __default)

    @overload
    def pop(self, __key: Key) -> Value:
        ...

    @overload
    def pop(self, __key: Key, default: Value = ...) -> Value:
        ...

    def pop(self, __key, default=NO_DEFAULT) -> Value:
        __key = self._modify_key(__key)

        if default is NO_DEFAULT:
            value: Value = dict.pop(self, __key)
        else:
            value: Value = dict.pop(self, __key, default)

        return value

    @overload
    def get(self, __key: Key) -> Union[Value, None]:
        ...

    @overload
    def get(self, __key: Key, default: Value = None) -> Value:
        ...

    def get(self, __key: Key, default=None):
        __key = self._modify_key(__key)
        value: Union[Value, None] = dict.get(self, __key, default)
        return value

    @overload
    def update(self, __m: Mapping[Key, Value], **kwargs: Value) -> None:
        ...

    @overload
    def update(
            self, __m: Iterable[Tuple[str, Any]], **kwargs: Value
    ) -> None:
        ...

    @overload
    def update(self, **kwargs: Value) -> None:
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
