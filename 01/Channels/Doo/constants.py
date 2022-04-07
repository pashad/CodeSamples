import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Final

from Channels.BaseChannel.Constants import PRODUCTION, STAGING
from Middleware.DectModel import OrderStatus, RemakeFault
from Model.enums import DeliveryType
from Utilities.parseBool import parseBool

# PLU Prefixes
PLU_BOGOF_PREFIX: str = "-BOGOF-"
PLU_ACCOUNT_LEVEL_PREFIX: str = "-A-"

WEBHOOK_SECRETS = {
    PRODUCTION: os.getenv("DOO_PRODUCTION_WEBHOOK_SECRET", ""),
    STAGING: os.getenv("DOO_STAGING_WEBHOOK_SECRET", ""),
}

BASE_URL = "https://restaurant-partner-api.doo.net/"

PARTNER_BASE_URL = "https://partners.doo.com/api/v1/brands/"

DOO_RH_URL = "https://restaurant-hub.doo.net/"
DOO_RS_URL = "https://client-api.doo.net/"
AUTO_OPEN_MARGIN = 10  # in minutes

# RH stands for Doo's Restaurant Hub
REDIS_DOO_RH_ACCOUNT_ID_KEY = "DOO_RH_ACCOUNT_ID_FOR_{oid}"
REDIS_DOO_RH_BRANCH_SESSION_KEY = "REDIS_DOO_RH_BRANCH_SESSION_{oid}"
REDIS_DOO_RH_ACCESS_TOKEN_KEY = "DOO_RH_ACCESS_TOKEN_FOR_{rhAccountId}"
REDIS_DOO_RH_SESSION_KEY = "DOO_RH_SESSION_FOR_{rhAccountId}"
REDIS_DOO_RH_AO_TOKEN_KEY = "DOO_RH_AO_TOKEN_FOR_{siteId}"
DOO_PROXY_CREDS = os.getenv("DOO_PROXY_CREDS", "")
DOO_PROXY_FOR_RH_REQUESTS = os.getenv(
    "DOO_PROXY_FOR_RH_REQUESTS",
    f"https://{DOO_PROXY_CREDS}@zproxy.lum-superproxy.io:22225",
)


DOO_MENU_IMAGE_GRAVITY = os.getenv("DOO_MENU_IMAGE_GRAVITY", "sm")
DOO_MENU_IMAGE_WIDTH = int(os.getenv("DOO_MENU_IMAGE_WIDTH", 1920))
DOO_MENU_IMAGE_HEIGHT = int(os.getenv("DOO_MENU_IMAGE_HEIGHT", 1080))
DOO_MENU_IMAGE_ENLARGE = parseBool(os.getenv("DOO_MENU_IMAGE_ENLARGE", True))
DOO_MENU_IMAGE_FORMAT = os.getenv("DOO_MENU_IMAGE_FORMAT", "jpg")
DOO_PRODUCT_IMAGE_GRAVITY = os.getenv("DOO_PRODUCT_IMAGE_GRAVITY", "sm")
DOO_PRODUCT_IMAGE_WIDTH = int(os.getenv("DOO_PRODUCT_IMAGE_WIDTH", 1024))
DOO_PRODUCT_IMAGE_HEIGHT = int(os.getenv("DOO_PRODUCT_IMAGE_HEIGHT", 1024))
DOO_PRODUCT_IMAGE_ENLARGE = parseBool(os.getenv("DOO_PRODUCT_IMAGE_ENLARGE", False))
DOO_PRODUCT_IMAGE_MIN_WIDTH = int(os.getenv("DOO_PRODUCT_IMAGE_MIN_WIDTH", 0))
DOO_PRODUCT_IMAGE_MIN_HEIGHT = int(os.getenv("DOO_PRODUCT_IMAGE_MIN_HEIGHT", 0))
DOO_PRODUCT_IMAGE_FORMAT = os.getenv("DOO_PRODUCT_IMAGE_FORMAT", "jpg")
MOST_POPULAR: str = "Most popular"
KWD = "KWD"
DOO_MULTI_MENUS_IDENTIFIER = "#DMM"


class DooTerms:
    reason_price_mismatched = "price_mismatched"
    reason_pos_item_id_mismatched = "pos_item_id_mismatched"
    reason_items_out_of_stock = "items_out_of_stock"
    reason_location_offline = "location_offline"
    reason_location_not_supported = "location_not_supported"
    reason_unsupported_order_type = "unsupported_order_type"
    reason_other = "other"

    FAILED = "failed"
    SUCCEEDED = "succeeded"

    FINALIZED = "This sync status has already been finalized"

    DELIVERY_DOO = "doo"
    DELIVERY_RESTAURANT = "restaurant"
    DELIVERY_IS_PICKUP = "customer"
    DELIVERY_IS_TABLE_SERVICE = "table_service"
    DELIVERY = "delivery"
    ORDER_FULFILLMENT_TYPE = "fulfillment_type"

    # Delivery Coordinates
    LOCATION = "location"
    LONGITUDE = "longitude"
    LATITUDE = "latitude"
    CITY = "city"
    POSTCODE = "postcode"
    LINE = "line"
    NOTE = "note"

    # Customer Data.
    CONTACT_NUMBER = "contact_number"
    CUSTOMER_NAME = "customer_name"

    # Delivery Fee
    DELIVERY_FEE = "delivery_fee"
    FRACTIONAL = "fractional"

    CANCEL_ORDER = "cancel_order"
    NEW_ORDER = "new_order"

    # Prep Stage
    IN_KITCHEN = "in_kitchen"
    READY_FOR_COLLECTION = "ready_for_collection"
    COLLECTED = "collected"


DeliveryTypeMap: Dict = {
    DooTerms.DELIVERY_IS_PICKUP: DeliveryType.PICKUP,
    DooTerms.DELIVERY_IS_TABLE_SERVICE: DeliveryType.EAT_IN,
}

DooEventMap = {
    DooTerms.CANCEL_ORDER: OrderStatus.CANCEL,
    DooTerms.NEW_ORDER: OrderStatus.DECT_PARSED,
}

DooPrepStageMap = {
    OrderStatus.PREPARING: DooTerms.IN_KITCHEN,
    OrderStatus.READY_FOR_PICKUP: DooTerms.READY_FOR_COLLECTION,
    OrderStatus.IN_DELIVERY: DooTerms.COLLECTED,
}

DooRemakeFaultMap = {
    DooTerms.DELIVERY_DOO: RemakeFault.CHANNEL,
    DooTerms.DELIVERY_RESTAURANT: RemakeFault.RESTAURANT,
}


class DooWebhookEvents:
    """Marks what event type is this request.
    Currently, supported values are:
     * event/order.new
     * event/order.status_update
     * event/rider.status_update
     https://partners.doo.com/docs/#ordeapi-event-webhook-payloads
    """

    NEW_ORDER: Final[str] = "event/order.new"
    ORDER_STATUS_UPDATE: Final[str] = "event/order.status_update"
    RIDER_STATUS_UPDATE: Final[str] = "event/rider.status_update"


@dataclass
class BusyModeWorkload:
    QUIET = "QUIET"
    BUSY = "BUSY"


@dataclass
class BusyMode:
    mode: BusyModeWorkload


@dataclass
class BusyModeParams:
    busy: int
    quiet: int


class Status(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    READY_TO_OPEN = "READY_TO_OPEN"


class ExternalOrderStatus(Enum):
    NEW = "new"
    ACCEPTED = "accepted"


ERROR_MESSAGE_TO_SKIP = "unavailabilities not applicable to the requested menu: site or menu id are invalid"
ALREADY_CLOSED_MESSAGE = "site status is already CLOSED"
ALREADY_OPEN_MESSAGE = "site status is already OPEN"

DooNoCutleryTranslations = [
    "NO CUTLERY",
    "NO POSATE",
    "GEEN BESTEK",
    "PAS DE COUVERTS",
    "SIN CUBIERTOS",
]

COUNTRY_CODES = [
    "AE",
    "AU",
    "BE",
    "ES",
    "FR",
    "HK",
    "IE",
    "IT",
    "KW",
    "NL",
    "SG",
    "TW",
    "GB",
]
