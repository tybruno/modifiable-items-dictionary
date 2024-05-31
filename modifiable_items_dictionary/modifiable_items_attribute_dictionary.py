"""
Modifiable Items Attribute Dictionary and related objects.

This module provides the `ModifiableItemsAttrDict` class which extends the
`ModifiableItemsDict` class from the `modifiable_items_dictionary` module.
This class allows for attribute-style access to dictionary items.

Objects provided by this module:
   `ModifiableItemsAttrDict` - Adds the ability to access dictionary items
   as attributes.

Reference:
This module was heavily inspired by Raymond Hettinger's class.
    [1] Hettinger, R. (2023). (Advanced) Python For Engineers: Part 3.
"""
from modifiable_items_dictionary.modifiable_items_dictionary import (
    ModifiableItemsDict,
)
from typing import Any


class ModifiableItemsAttrDict(ModifiableItemsDict):
    """
    Dictionary class that allows attribute-style access to its items.

    This class extends `ModifiableItemsDict` and overrides the `__getattr__`
    and `__setattr__` methods to provide attribute-style access to dictionary
    items. This means that in addition to the standard dictionary access
    syntax (dict["key"]), you can also use attribute syntax (dict.key).
    """
    __slots__ = ()

    def __getattr__(self, name: str) -> Any:
        """
        Return the value for a given attribute name.

        This method is called when an attribute lookup has not found the
        attribute in the usual places. It's overridden here to look for the
        attribute in the dictionary items.

        Args:
            name (str): The name of the attribute.

        Returns:
            The value of the attribute.

        Raises:
            AttributeError: If the attribute is not found in the dictionary
                items.
        """
        try:
            value = self[name]
        except KeyError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute "
                f"'{name}'."
            )
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set the value for a given attribute name.

        This method is called when an attribute assignment is attempted.
        It's overridden here to allow attribute-style assignments to
        dictionary items.

        Args:
            name (str): The name of the attribute.
            value: The value to set for the attribute.
        """
        self[name] = value

    def __delattr__(self, name: str) -> None:
        """
        Delete the attribute with a given name.

        This method is called when an attribute deletion is attempted.
        It's overridden here to allow attribute-style deletions of
        dictionary items.

        Args:
            name (str): The name of the attribute.

        Raises:
            AttributeError: If the attribute is not found in the
                dictionary items.
        """
        if name in self:
            del self[name]
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute "
                f"'{name}'."
            )
