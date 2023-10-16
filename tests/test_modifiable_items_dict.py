import contextlib
import copy
import ipaddress
import typing

import pytest

import modifiable_items_dictionary
import modifiable_items_dictionary.modifiable_items_dictionary


def _strip(_value: typing.Any):
    if isinstance(_value, str):
        _value = _value.strip()
        return _value
    return _value


def _case_fold(_value: typing.Any) -> typing.Any:
    if isinstance(_value, str):
        _case_folded_string: str = _value.casefold()
        return _case_folded_string
    return _value


def _strip_and_case_fold(_value: typing.Any) -> typing.Any:
    _value = _case_fold(_strip(_value))
    return _value


def _to_ipaddress(_value: typing.Any) -> typing.Any:
    if isinstance(_value, str):
        with contextlib.suppress(ValueError):
            _ip_address: typing.Union[
                ipaddress.IPv4Address, ipaddress.IPv6Address
            ] = ipaddress.ip_address(_value)
            return _ip_address

    return _value


@pytest.fixture(
    params=(
            {
                "CamelCase": 1,
                "lower": 2,
                "UPPER": 3,
                "snake_case": 4,
                5: "Five",
                True: "True",
            },
            {1: 2, ("hello", "Goodbye"): 2},
    )
)
def valid_mapping(request) -> typing.Mapping:
    inputs: typing.Mapping = request.param
    return inputs


class HostDict(modifiable_items_dictionary.ModifiableItemsDict):
    _key_modifiers = [_strip, _case_fold]
    _value_modifiers = staticmethod(_to_ipaddress)


class _TestingClass(typing.NamedTuple):
    cls: typing.Type[modifiable_items_dictionary.ModifiableItemsDict]
    modify_key: (modifiable_items_dictionary.modifiable_items_dictionary
                 .KeyCallable)
    modify_value: (modifiable_items_dictionary.modifiable_items_dictionary
                   .ValueCallable)


def host_dict_with_list_and_static_method_modifiers() -> typing.Type[
    modifiable_items_dictionary.ModifiableItemsDict
]:
    class HostDict(modifiable_items_dictionary.ModifiableItemsDict):
        _key_modifiers = [_strip, _case_fold]
        _value_modifiers = staticmethod(_to_ipaddress)

    return HostDict


def host_dict_with_list_and_method_modifiers() -> typing.Type[
    modifiable_items_dictionary.ModifiableItemsDict]:
    class HostDict(modifiable_items_dictionary.ModifiableItemsDict):
        _key_modifiers = [_strip, _case_fold]

        def _value_modifiers(self, _value: typing.Any) -> typing.Any:
            if isinstance(_value, str):
                with contextlib.suppress(ValueError):
                    _ip_address: typing.Union[
                        ipaddress.IPv4Address, ipaddress.IPv6Address
                    ] = ipaddress.ip_address(_value)
                    return _ip_address

            return _value

    return HostDict


@pytest.fixture(
    params=(
            _TestingClass(
                host_dict_with_list_and_static_method_modifiers(),
                _strip_and_case_fold,
                _to_ipaddress,
            ),
            _TestingClass(
                host_dict_with_list_and_method_modifiers(),
                _strip_and_case_fold,
                _to_ipaddress,
            ),
            _TestingClass(
                modifiable_items_dictionary.ModifiableItemsDict,
                lambda x: x,
                lambda x: x
                )
    )
)
def class_under_test(request) -> _TestingClass:
    _modifiable_class: _TestingClass = request.param
    return _modifiable_class


@pytest.fixture(
    params=[
        {" GooGle.com ": "142.250.69.206", "CisCO": "72.163.4.185"},
        [(" GooGle.com ", "142.250.69.206"), ("CisCO", "72.163.4.185")],
    ]
)
def hosts(request) -> typing.Mapping:
    _hosts: typing.Mapping = request.param
    return _hosts


@pytest.fixture(params=(set(), list(), dict()))
def unhashable_type(request):
    unhashable_type = request.param
    return unhashable_type


class TestModifiableItemsDict:
    @pytest.mark.parametrize("bad_modifiers", [1, 7.62, "string"])
    def test_bad_modifiers(self, bad_modifiers):
        class BadModifierTest(modifiable_items_dictionary.ModifiableItemsDict):
            _key_modifiers = bad_modifiers

        with pytest.raises(TypeError):
            BadModifierTest(a=1)

    def test_modifiers_is_none(self, valid_mapping):
        class NoModifiersDict(modifiable_items_dictionary.ModifiableItemsDict):
            _key_modifiers = None
            _value_modifiers = None

        expected = valid_mapping
        actual = NoModifiersDict(valid_mapping)
        assert actual == expected

    def test__init__mapping(
            self,
            valid_mapping: typing.Mapping,
            class_under_test
    ):
        _class, _key_operation, _value_operation = class_under_test

        modifiable_dict = _class(valid_mapping)
        expected = {
            _key_operation(key): _value_operation(value)
            for key, value in valid_mapping.items()
        }
        assert modifiable_dict == expected

    @pytest.mark.parametrize(
        "valid_kwargs",
        ({"a": 1, "B": 2}, {"lower": 3, "UPPER": 4, "MiXeD": 5}),
    )
    def test__init__kwargs(
            self,
            valid_kwargs: typing.Mapping,
            class_under_test
    ):
        _class, _key_operation, _value_operation = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            **valid_kwargs
            )
        expected = {
            _key_operation(key): _value_operation(value)
            for key, value in valid_kwargs.items()
        }
        assert modifiable_items_dict == expected

    @pytest.mark.parametrize(
        "mapping_and_kwargs",
        [
            ({"a": 1, "B": 2}, {"lower": 3, "UPPER": 4, "MiXeD": 5}),
        ],
    )
    def test__init__iterable_and_kwargs(
            self,
            mapping_and_kwargs: typing.Tuple[typing.Mapping, typing.Mapping],
            class_under_test
    ):
        _class, _key_operation, _value_operation = class_under_test
        args, kwargs = mapping_and_kwargs
        expected = {
            _key_operation(key): _value_operation(value)
            for key, value in dict(**args, **kwargs).items()
        }
        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            args,
            **kwargs
            )
        assert modifiable_items_dict == expected

    @pytest.mark.parametrize(
        "iterables",
        [
            zip(["one", "TwO", "ThrEE"], [1, 2, 3]),
            [("TwO", 2), ("one", 1), ("ThrEE", 3), (4, "FouR")],
        ],
    )
    def test__init__iterable(
            self,
            iterables: typing.Iterable[
                typing.Tuple[typing.Hashable, typing.Any]],
            class_under_test
    ):
        _class, _key_operation, _value_operation = class_under_test
        iterables_copy = copy.deepcopy(iterables)
        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            iterables
            )
        expected: typing.Mapping = {
            _key_operation(key): _value_operation(value)
            for key, value in iterables_copy
        }
        assert modifiable_items_dict == expected
        assert repr(modifiable_items_dict) == repr(expected)

    @pytest.mark.parametrize("invalid_type", ([1], {2}, True, 1))
    def test__init__invalid_type(self, invalid_type, class_under_test):
        _class, _, _ = class_under_test

        with pytest.raises(TypeError):
            _class(invalid_type)

    @pytest.mark.parametrize("iterable", [[("1", 1), ("two", 2, 2)]])
    def test__init__bad_iterable_elements(self, iterable, class_under_test):
        _class, _, _ = class_under_test

        with pytest.raises(ValueError):
            _class(iterable)

    @pytest.mark.parametrize(
        "keys",
        (["lower", "Title", "UPPER", "CamelCase", "snake_case", object()],),
    )
    def test_fromkeys(self, keys: typing.Iterable, class_under_test):
        _class, _key_operation, _value_operation = class_under_test

        value = "Some Value"
        expected: typing.Mapping = {
            _key_operation(key): _value_operation(value) for key in keys
        }

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class.fromkeys(
            keys,
            value
            )
        assert modifiable_items_dict == expected
        assert isinstance(modifiable_items_dict, _class)

        for key in keys:
            assert key in modifiable_items_dict

    @pytest.mark.parametrize(
        "keys",
        (["lower", "Title", "UPPER", "CamelCase", "snake_case", object()],),
    )
    def test_fromkeys_none_value(
            self,
            keys: typing.Iterable,
            class_under_test
    ):
        _class, _key_operation, _value_operation = class_under_test

        expected: typing.Mapping = {
            _key_operation(key): _value_operation(None) for key in keys
        }

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class.fromkeys(
            keys
            )
        assert modifiable_items_dict == expected
        assert isinstance(modifiable_items_dict, _class)

        for key in keys:
            assert key in modifiable_items_dict

    @pytest.mark.parametrize("invalid_type", (True, 1))
    def test_fromkeys_with_invalid_type(self, invalid_type, class_under_test):
        _class, _, _ = class_under_test

        with pytest.raises(TypeError):
            _class.fromkeys(invalid_type)

    def test__setitem__(self, valid_mapping, class_under_test):
        _class, _key_operation, _value_operation = class_under_test

        modifiable_dict: _class = _class()
        expected: dict = dict()
        for key, item in valid_mapping.items():
            expected[_key_operation(key)] = _value_operation(item)
            modifiable_dict[key] = item
        assert modifiable_dict == expected
        assert repr(modifiable_dict) == repr(expected)

    def test___setitem__bad_key_type(self, unhashable_type, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()
        with pytest.raises(TypeError):
            modifiable_items_dict[unhashable_type] = 0

    def test__getitem__(self, valid_mapping, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            valid_mapping
            )
        for key, value in valid_mapping.items():
            assert modifiable_items_dict[key] == value

    def test__getitem__missing_key(self, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()
        assert modifiable_items_dict == dict()

        # make unique __key which will not be in dict
        _missing_key = object()

        with pytest.raises(KeyError):
            _ = modifiable_items_dict[_missing_key]

    def test__delitem__(self, valid_mapping, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            valid_mapping
            )
        for key, value in valid_mapping.items():
            del modifiable_items_dict[key]
            assert key not in modifiable_items_dict

    def test__delitem__missing_key(self, valid_mapping, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            valid_mapping
            )
        with contextlib.suppress(KeyError):
            del modifiable_items_dict["missing_key"]

    def test_get(self, valid_mapping, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            valid_mapping
            )
        for key, value in valid_mapping.items():
            assert modifiable_items_dict.get(key) == value
            assert modifiable_items_dict.get(key, None) == value

    def test_get_missing_key(self, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        # make unique __key which will not be in dict
        _missing_key = object()
        _default = "__default v"

        assert modifiable_items_dict.get(_missing_key) is None
        assert (
                modifiable_items_dict.get(_missing_key, _default)
                == _default
        )

    def test_get_unhashable_key(self, unhashable_type, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        _default = "__default v"

        with pytest.raises(TypeError):
            modifiable_items_dict.get(unhashable_type)
            modifiable_items_dict.get(unhashable_type, _default)

    def test_pop(self, valid_mapping, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            valid_mapping
            )
        for key, value in valid_mapping.items():
            assert modifiable_items_dict.pop(key) == value
            assert key not in modifiable_items_dict

    def test_pop_default(self, valid_mapping, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            valid_mapping
            )
        _missing_key = object()
        _default = "default value"

        assert modifiable_items_dict.pop(_missing_key, _default) == _default

    def test_pop_missing_key(self, class_under_test):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        # make unique __key which will not be in dict
        _missing_key = object()

        with pytest.raises(KeyError):
            modifiable_items_dict.pop(_missing_key)

    def test_pop_unhashable_type(self, class_under_test, unhashable_type):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        with pytest.raises(KeyError):
            modifiable_items_dict.pop(unhashable_type)

    def test_setdefault(self, valid_mapping, class_under_test):
        _class, _key_operation, _value_operation = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()
        expected: dict = dict()
        for key, item in valid_mapping.items():
            expected.setdefault(_key_operation(key), _value_operation(item))
            modifiable_items_dict.setdefault(key, item)
        assert modifiable_items_dict == expected
        assert repr(modifiable_items_dict) == repr(expected)

    def test_setdefault_unhashable_type(
            self, class_under_test, unhashable_type
    ):
        _class, _, _ = class_under_test

        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        with pytest.raises(TypeError):
            modifiable_items_dict.setdefault(unhashable_type)

    @pytest.mark.parametrize(
        "starting_data", ({"start_lower": 1, "START_UPPER": 2, "__key": 1},)
    )
    @pytest.mark.parametrize(
        "args", ({"UPPER": 1, "lower": 2, "CamelCase": 3, "Key": 2},)
    )
    @pytest.mark.parametrize("kwargs", ({"UP": 1, "down": 2, "__key": 3},))
    def test_update_using_mapping(
            self, class_under_test, starting_data, args, kwargs
    ):
        _class, _key_operation, _value_operation = class_under_test
        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            starting_data
            )

        expected = dict(
            {
                _key_operation(key): _value_operation(value)
                for key, value in starting_data.items()
            }
        )

        assert modifiable_items_dict == expected

        expected.update(
            {
                _key_operation(key): _value_operation(value)
                for key, value in args.items()
            },
            **{
                _key_operation(key): _value_operation(value)
                for key, value in kwargs.items()
            }
        )

        modifiable_items_dict.update(args, **kwargs)

        assert modifiable_items_dict == expected

    @pytest.mark.parametrize(
        "starting_data", ({"start_lower": 1, "START_UPPER": 2, "__key": 1},)
    )
    @pytest.mark.parametrize(
        "args",
        ([("UPPER", 1), ("lower", 2), ("CamelCase", 3), ("__key", 2)],),
    )
    @pytest.mark.parametrize("kwargs", ({"UP": 1, "down": 2, "__key": 3},))
    def test_update_using_sequence(
            self, class_under_test, starting_data, args, kwargs
    ):
        _class, _key_operation, _value_operation = class_under_test
        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class(
            starting_data
            )

        expected = dict(
            {
                _key_operation(key): _value_operation(value)
                for key, value in starting_data.items()
            }
        )

        assert modifiable_items_dict == expected

        expected.update(
            {
                _key_operation(key): _value_operation(value)
                for key, value in args
            },
            **{
                _key_operation(key): _value_operation(value)
                for key, value in kwargs.items()
            }
        )

        modifiable_items_dict.update(args, **kwargs)

        assert modifiable_items_dict == expected

    def test_update_unhashable_key(self, class_under_test, unhashable_type):
        _class, _, _ = class_under_test
        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        iterable = [(unhashable_type, 1)]

        with pytest.raises(TypeError):
            modifiable_items_dict.update(iterable)

    @pytest.mark.parametrize("iterable", [[("1", 1), ("two", 2, 2)]])
    def test_update_bad_iterable_value(self, class_under_test, iterable):
        _class, _, _ = class_under_test
        modifiable_items_dict: (
            modifiable_items_dictionary.ModifiableItemsDict) = _class()

        with pytest.raises(ValueError):
            modifiable_items_dict.update(iterable)
