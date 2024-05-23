"""Tests for the ModifiableItemsAttrDict class.

The ModifiableItemsAttrDict class is a dictionary class that allows
attribute-style access to its items. This test suite tests the __getattr__,
 __setattr__, and __delattr__ methods of the ModifiableItemsAttrDict class.
"""
import pytest
from modifiable_items_dictionary.modifiable_items_attribute_dictionary import (
    ModifiableItemsAttrDict,
)


class TestModifiableItemsAttrDict:
    def test_getattr(self):
        """
        Test that the __getattr__ method correctly retrieves the value of an attribute.
        """
        attr_dict = ModifiableItemsAttrDict({'key': 'value'})
        assert attr_dict.key == 'value'

    def test_setattr(self):
        """
        Test that the __setattr__ method correctly sets the value of an
        attribute.
        """
        attr_dict = ModifiableItemsAttrDict()
        attr_dict.key = 'value'
        assert attr_dict['key'] == 'value'

    def test_delattr(self):
        """
        Test that the __delattr__ method correctly deletes an attribute.
        """
        attr_dict = ModifiableItemsAttrDict({'key': 'value'})
        del attr_dict.key
        assert 'key' not in attr_dict

    def test_delattr_not_found(self):
        """
        Test that the __delattr__ method raises an AttributeError when trying
        to delete a non-existent attribute.
        """
        attr_dict = ModifiableItemsAttrDict()
        with pytest.raises(AttributeError):
            del attr_dict.key

    def test_getattr_not_found(self):
        """
        Test that the __getattr__ method raises an AttributeError when trying
        to access a non-existent attribute.
        """
        attr_dict = ModifiableItemsAttrDict()
        with pytest.raises(AttributeError):
            _ = attr_dict.key

    def test_setattr_and_getattr(self):
        """
        Test that the __setattr__ and __getattr__ methods correctly set and
        retrieve the value of an attribute.
        """
        attr_dict = ModifiableItemsAttrDict()
        attr_dict.key = 'value'
        assert attr_dict.key == 'value'
