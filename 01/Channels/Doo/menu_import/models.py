from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DooMenuCategory:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    sort_order: Optional[int] = None
    top_level: bool = False


@dataclass
class DooMenuTag:
    id: Optional[int] = None
    type: str = ""
    name: str = ""


@dataclass
class DooMenuModifierGroup:
    id: Optional[int] = None
    allow_multiple_same_item: bool = False
    display_price_as_delta: bool = False
    instruction: str = ""
    max_selection_points: int = 0
    min_selection_points: int = 0
    name: str = ""
    price_strategy: str = ""
    selection_cascades: bool = False
    sort_order: Optional[int] = None
    modifier_item_ids: List[int] = field(default_factory=list)
    default_item_ids: List[int] = field(default_factory=list)


@dataclass
class DooMenuItem:
    alcohol: bool = False
    description: str = ""
    id: Optional[int] = None
    name: str = ""
    omit_from_receipts: bool = False
    sort_order: Optional[int] = None
    product_information: str = ""
    available: bool = True
    popular: bool = True
    category_id: Optional[int] = None
    max_quantity: Optional[int] = None
    modifier_group_ids: List[int] = field(default_factory=list)
    image_url_preview: str = ""
    image_url_large: str = ""
    image_url: str = ""
    discount_tag: str = ""
    modifier_info_message: str = ""
    price: str = ""
    alt_mod_price: str = ""
    collection_price: str = ""
    collection_mod_price: str = ""
    discounted_price: str = ""
    discounted_alt_mod_price: str = ""
    discounted_collection_price: str = ""
    discounted_collection_mod_price: str = ""
    fulfillment_price: str = ""
    fulfillment_mod_price: str = ""
    discounted_fulfillment_price: str = ""
    discounted_fulfillment_alt_mod_price: str = ""


@dataclass
class DooMenu:
    menu_id: Optional[int] = None
    menu_has_dietary_info: bool = False
    menu_categories: List[DooMenuCategory] = field(default_factory=list)
    menu_tags: List[DooMenuTag] = field(default_factory=list)
    menu_modifier_groups: List[DooMenuModifierGroup] = field(default_factory=list)
    menu_items: List[DooMenuItem] = field(default_factory=list)
    promoted_items_carousel: Optional[Any] = None
    menu_headers: List[Dict[str, str]] = field(default_factory=list)
    menu_footnotes: List[Dict[str, str]] = field(default_factory=list)
    offers_visibility_information: Dict[Any, Any] = field(default_factory=dict)
    reward_card: Optional[Any] = None
    carousels: List[Any] = field(default_factory=list)
    hide_menu_category_ids: List[int] = field(default_factory=list)


@dataclass
class DooRestaurantAddress:
    address1: str
    post_code: str
    neighborhood: str
    city: str
    country: str
    coordinates: List[float]


@dataclass
class DooRestaurant:
    id: Optional[int] = None
    name: str = ""
    name_with_branch: str = ""
    currency_code: str = ""
    currency_symbol: str = ""
    primary_image_url: str = ""
    image_url: str = ""
    description: str = ""
    share_url: str = ""
    phone_number: str = ""
    menu_disabled: bool = False
    menu: Optional[DooMenu] = None
    address: Optional[DooRestaurantAddress] = None
