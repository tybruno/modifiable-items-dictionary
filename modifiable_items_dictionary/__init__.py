"""modifiable_items_dictionary package

Subpackages:
    - modifiable_items_dictionary: Contains the ModifiableItemsDict and
        ModifiableItemsAttrDict classes.
    - modifiable_items_attribute_dictionary: Contains the ModifiableItemsAttrDict
        class.
"""
from modifiable_items_dictionary.modifiable_items_dictionary import (
    ModifiableItemsDict,
)
from modifiable_items_dictionary.modifiable_items_attribute_dictionary import (
    ModifiableItemsAttrDict,
)

__all__ = (ModifiableItemsDict.__name__, ModifiableItemsAttrDict.__name__)
