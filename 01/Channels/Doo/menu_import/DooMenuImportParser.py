from collections import defaultdict
from enum import Enum
from typing import Dict, List, Optional, Union

from bson import ObjectId
from dacite import Config, from_dict

from Channels.BaseChannel.BaseChannelMenuImportParser import BaseChannelMenuImportParser
from Channels.Doo.constants import MOST_POPULAR
from Channels.Doo.menu_import.models import ALLERGEN_LOOKUP_DICT
from Channels.Doo.menu_import.models import (
    DooMenu,
    DooMenuCategory,
    DooMenuItem,
    DooMenuModifierGroup,
    DooRestaurant,
)
from Middleware.DectModel import ItemType
from Model.enums import Channel
from Model.menu import ChannelCategory, ChannelMenu
from Model.menu.importer import MenuImportDC
from Model.product import ChannelProduct, ProductTag


class DooMenuImportParser(BaseChannelMenuImportParser):
    channel = Channel.DOO

    def toDectMenus(self, rawChannelMenus: Dict) -> List[MenuImportDC]:
        dooRestaurant: DooRestaurant = from_dict(
            DooRestaurant, rawChannelMenus, Config(cast=[Enum], check_types=False)
        )
        dooMenu: DooMenu = dooRestaurant.menu
        dooLookups = {
            "categories": {c.id: c for c in dooMenu.menu_categories},
            "tags": {t.id: t for t in dooMenu.menu_tags},
            "modgroups": {m.id: m for m in dooMenu.menu_modifier_groups},
            "items": {i.id: i for i in dooMenu.menu_items},
        }
        menuImportData: MenuImportDC = self._processMenu(dooMenu, dooRestaurant, dooLookups)

        return [menuImportData]

    def _processMenu(
        self,
        dooMenu: DooMenu,
        dooRestaurant: DooRestaurant,
        dooLookups: Dict[
            str,
            Dict[int, Union[DooMenuCategory, DooMenuItem, DooMenuModifierGroup]],
        ],
    ) -> MenuImportDC:
        menuImportData = MenuImportDC()

        menu = ChannelMenu(
            {
                "_id": ObjectId(),
                "name": f"{dooRestaurant.name} Menu",
                "description": dooRestaurant.description,
                "headerImageURL": dooRestaurant.image_url,
                "account": "",  # Explicitly set here in order to pass ValueError, will be updated in butler
                "externalMenuId": f"{dooMenu.menu_id}",
                "editedWithV2": True,
            }
        )

        menuImportData.menu = menu

        itemsByCategoryIds: Dict[int, List[DooMenuItem]] = defaultdict(list)
        for item in dooMenu.menu_items:
            itemsByCategoryIds[item.category_id].append(item)

        for category in dooMenu.menu_categories:
            dooCategoryItems: List[DooMenuItem] = itemsByCategoryIds.get(category.id, [])
            self._processCategory(category, dooCategoryItems, menuImportData, dooLookups)
        return menuImportData

    def _processCategory(
        self,
        dooCategory: DooMenuCategory,
        dooCategoryItems: List[DooMenuItem],
        menuImportData: MenuImportDC,
        dooLookups: Dict[
            str,
            Dict[int, Union[DooMenuCategory, DooMenuItem, DooMenuModifierGroup]],
        ],
    ):
        dooCategory: DooMenuCategory = dooLookups["categories"].get(dooCategory.id)
        # exclude categories with top_level = False and name == "Most popular"
        if dooCategory and dooCategory.top_level and dooCategory.name != MOST_POPULAR:
            dbCategoryId = ObjectId()
            category = ChannelCategory(
                {
                    "_id": dbCategoryId,
                    "menu": menuImportData.menu.oid,
                    "name": dooCategory.name,
                    "description": dooCategory.description if dooCategory.description else "",
                }
            )

            menuImportData.menu.channelCategories.append(dbCategoryId)

            for item in dooCategoryItems:
                channelProduct = self._processItem(item, menuImportData, dooLookups)
                if channelProduct:
                    category.subProductSortOrder.append(channelProduct)

            menuImportData.categories.append(category)

    def _processItem(
        self,
        dooItem: DooMenuItem,
        menuImportData: MenuImportDC,
        dooLookups: Dict[
            str,
            Dict[int, Union[DooMenuCategory, DooMenuItem, DooMenuModifierGroup]],
        ],
    ) -> Optional[ChannelProduct]:
        product = self._prepareDectChannelProductFromDooItem(dooItem, menuImportData.menu.oid)
        if dooItem.modifier_group_ids:
            for mgId in dooItem.modifier_group_ids:
                channelProduct = self._processModifierGroup(mgId, menuImportData, dooLookups)
                if channelProduct:
                    product.subProductSortOrder.append(channelProduct)

        menuImportData.products.append(product)
        return product

    def _processModifierGroup(
        self,
        mgId: int,
        menuImportData: MenuImportDC,
        dooLookups: Dict[
            str,
            Dict[int, Union[DooMenuCategory, DooMenuItem, DooMenuModifierGroup]],
        ],
    ) -> Optional[ChannelProduct]:
        dooMG: DooMenuModifierGroup = dooLookups["modgroups"].get(mgId)
        if not dooMG:
            return None

        mg = ChannelProduct(
            {
                "_id": ObjectId(),
                "menu": menuImportData.menu.oid,
                "plu": str(dooMG.id),
                "productType": ItemType.MODIFIER_GROUP,
                "name": dooMG.name,
                "max": dooMG.max_selection_points,
                "min": dooMG.min_selection_points,
                "multiMax": dooMG.max_selection_points
                if dooMG.allow_multiple_same_item and dooMG.max_selection_points > 1
                else None,
            }
        )

        for modId in dooMG.modifier_item_ids:
            channelProduct = self._processModifier(modId, menuImportData, dooLookups)
            if channelProduct:
                mg.subProductSortOrder.append(channelProduct)

        menuImportData.products.append(mg)
        return mg

    def _processModifier(
        self,
        modId: int,
        menuImportData: MenuImportDC,
        dooLookups: Dict[
            str,
            Dict[int, Union[DooMenuCategory, DooMenuItem, DooMenuModifierGroup]],
        ],
    ) -> Optional[ChannelProduct]:
        dooModifier: Optional[DooMenuItem] = dooLookups["items"].get(modId)
        if not dooModifier:
            return None

        modifier = self._prepareDectChannelProductFromDooItem(
            dooModifier,
            menuImportData.menu.oid,
            productType=ItemType.MODIFIER,
        )

        menuImportData.products.append(modifier)
        return modifier

    def _prepareDectChannelProductFromDooItem(
        self,
        dooItem: DooMenuItem,
        dbMenuId: ObjectId,
        productType: ItemType = ItemType.PRODUCT,
    ):
        product = ChannelProduct(
            {
                "_id": ObjectId(),
                "menu": dbMenuId,
                "plu": str(dooItem.id),
                "productType": productType,
                "name": dooItem.name,
                "description": dooItem.description,
                "price": self._priceToDect(float(dooItem.price)),
                "imageUrl": dooItem.image_url,
            }
        )

        if getattr(dooItem, "alcohol", None):
            product.productTags = [ProductTag.ALCOHOL]

        # get allergens (product_information field)
        # - in most stores the allergens are written with the format "Contains Allergen1. Allergen2, ..."

        info: str = dooItem.product_information or ""
        if info.startswith("Contains "):
            allergens = info.replace(".", "").replace("Contains ", "").split(", ")
            for allergen in allergens:
                if tag := ALLERGEN_LOOKUP_DICT.get(allergen.strip()):
                    product.productTags.append(tag)
        elif info.startswith("No known allergens"):
            product.productTags.append(ProductTag.NO_ALLERGENS)

        return product
