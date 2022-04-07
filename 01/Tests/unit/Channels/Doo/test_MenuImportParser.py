import json
import os
from copy import deepcopy
from pathlib import Path
from typing import List

import pytest
from bson import ObjectId

from Channels.Doo.menu_import.DooMenuImportParser import DooMenuImportParser
from Middleware.DectModel import ItemType
from Model.menu.importer import MenuImportDC
from Model.product import ChannelProduct, ProductTag

current_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def parser():
    return DooMenuImportParser()


def test_menuImportParserTestWithModGroups(parser):
    with open(Path(current_path).joinpath("mockData", "dooMenu.json")) as f:
        rawMenu = json.load(f)

    dectMenus: List[MenuImportDC] = parser.toDectMenus(rawMenu)
    assert len(dectMenus) == 1
    dectMenuData = dectMenus[0]
    dectMenu = dectMenuData.menu
    assert dectMenu.name == "Chilli Pickle Menu"
    assert dectMenu.description == "Delicious Indian cuisine"
    assert (
        dectMenu.headerImageURL == (
            "https://menus-api.doocdn.com/images/eb5af225-bf5e-4811-8d6a-e1b2aa9c851f/image.jpeg"
            "?width={w}&height={h}&auto=webp&format=jpg&fit=crop&v={&quality}"
        )
    )
    assert len(dectMenuData.categories) == 11
    assert "Modifiers" not in [category.name for category in dectMenuData.categories]
    category = dectMenuData.categories[0]
    assert category.name == "Fast food"
    assert category.description == "Choose fast food, don't waste your time."
    assert len(category.subProductSortOrder) == 5
    assert len(dectMenuData.products) == 258
    product: ChannelProduct = category.subProductSortOrder[0]
    assert product.plu == "79273801"
    assert product.price == 500
    assert product.name == "Chilli Pickle Onion Bhaji (VG)(GF)"
    assert product.description == (
        "Crunchy onion fritter with toasted crushed spice, curry leaf, "
        "Bengal 5 spice with Mango Churtney & Curry Chat"
    )
    assert product.imageUrl == (
        "https://menus-api.doocdn.com/images/874fd056-ffc7-4ba8-89ff-53205ac38edf/image.jpeg"
        "?width={w}&height={h}&auto=webp&format=jpg&fit=crop&v={&quality}"
    )
    assert product.productTags == [ProductTag.ALCOHOL]
    products: List[ChannelProduct] = list(filter(lambda x: x.productType == ItemType.PRODUCT, dectMenuData.products))
    assert len(products) == 47
    modifierGroups: List[ChannelProduct] = list(
        filter(lambda x: x.productType == ItemType.MODIFIER_GROUP, dectMenuData.products)
    )
    assert len(modifierGroups) == 27
    modifierGroup: ChannelProduct = modifierGroups[0]
    assert modifierGroup.plu == "487326393"
    assert modifierGroup.menu == ObjectId(dectMenuData.menu.oid)
    assert modifierGroup.productType == ItemType.MODIFIER_GROUP
    assert modifierGroup.name == "Please Choose Drink"
    assert modifierGroup.max == 29
    assert modifierGroup.min == 0
    assert modifierGroup.multiMax == 29
    modifiers: List[ChannelProduct] = list(filter(lambda x: x.productType == ItemType.MODIFIER, dectMenuData.products))
    assert len(modifiers) == 184
    modifier: ChannelProduct = modifiers[0]
    assert modifier.plu == "68207791"
    assert modifier.menu == ObjectId(dectMenuData.menu.oid)
    assert modifier.productType == ItemType.MODIFIER
    assert modifier.name == "Coke (330ml)"
    assert modifier.price == 150
    assert modifier.imageUrl == (
        "https://menus-api.doocdn.com/images/fa57708b-05a9-40f0-9851-15a4267d1b84/image.jpeg"
        "?width={w}&height={h}&auto=webp&format=jpg&fit=crop&v={&quality}"
    )


def test_remove_most_popular_category(parser):
    with open(Path(current_path).joinpath("mockData", "dooMenu.json")) as f:
        loadedMenu = json.load(f)
    menuWithMostPopularCategory = deepcopy(loadedMenu)
    menuWithMostPopularCategory["menu"]["menu_categories"][0]["name"] = "Most popular"
    menu = parser.toDectMenus(menuWithMostPopularCategory)

    assert "Most popular" not in [category.name for category in menu[0].categories]
    assert len([category.name for category in menu[0].categories]) == 10


def test_allergens_import(parser):
    with open(Path(current_path).joinpath("mockData", "dooMenu.json")) as f:
        rawMenu = json.load(f)

    dectMenus: List[MenuImportDC] = parser.toDectMenus(rawMenu)
    category = dectMenus[0].categories[0]
    product1 = category.subProductSortOrder[1]

    assert product1.name == "Chilli Pickle Curry Combo"
    assert product1.productTags == [ProductTag.MILK]

    product2 = category.subProductSortOrder[2]

    assert product2.name == "The Chilli Pickle Chicken Biryani - Contains Nuts (GF)"
    assert product2.productTags == [
        ProductTag.MILK,
        ProductTag.NUTS,
        ProductTag.PEANUTS,
        ProductTag.SESAME,
    ]

    product3 = category.subProductSortOrder[0]

    assert product3.name == "Chilli Pickle Onion Bhaji (VG)(GF)"
    assert product3.productTags == [ProductTag.ALCOHOL]
