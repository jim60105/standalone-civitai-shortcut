"""
Gallery Navigation Handlers - Page navigation functionality.

This module handles all navigation-related events for gallery pagination.
"""

from typing import Dict, Optional

from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import NetworkError, ValidationError

logger = get_logger(__name__)


def get_current_page(paging_information: Optional[Dict], current_url: str) -> int:
    """Get current page number from paging information."""
    if not paging_information or not paging_information.get("totalPageUrls"):
        return 1

    total_page_urls = paging_information["totalPageUrls"]
    try:
        return total_page_urls.index(current_url) + 1
    except (ValueError, TypeError):
        return 1


@with_error_handling()
def on_page_slider_release(
    usergal_page_url: str, page_slider: int, paging_information: Optional[Dict]
) -> str:
    """Handle page slider release event."""
    page_url = usergal_page_url

    if paging_information and paging_information.get("totalPageUrls"):
        total_page_urls = paging_information["totalPageUrls"]
        if 1 <= page_slider <= len(total_page_urls):
            page_url = total_page_urls[page_slider - 1]

    return page_url


@with_error_handling()
def on_first_btn_click(usergal_page_url: str, paging_information: Optional[Dict]) -> str:
    """Handle first page button click."""
    page_url = usergal_page_url

    if paging_information and paging_information.get("totalPageUrls"):
        total_page_urls = paging_information["totalPageUrls"]
        if total_page_urls:
            page_url = total_page_urls[0]

    return page_url


@with_error_handling()
def on_end_btn_click(usergal_page_url: str, paging_information: Optional[Dict]) -> str:
    """Handle last page button click."""
    page_url = usergal_page_url

    if paging_information and paging_information.get("totalPageUrls"):
        total_page_urls = paging_information["totalPageUrls"]
        if total_page_urls:
            page_url = total_page_urls[-1]

    return page_url


@with_error_handling(
    fallback_value="",
    exception_types=(NetworkError, ValidationError),
    user_message="Failed to navigate to next page",
)
def on_next_btn_click(usergal_page_url: str, paging_information: Optional[Dict]) -> str:
    """Handle next page button click."""
    page_url = usergal_page_url

    current_page = get_current_page(paging_information, usergal_page_url)
    if paging_information and paging_information.get("totalPageUrls"):
        total_page_urls = paging_information["totalPageUrls"]
        if len(total_page_urls) > current_page:
            page_url = total_page_urls[current_page]

    return page_url


@with_error_handling(
    fallback_value="",
    exception_types=(NetworkError, ValidationError),
    user_message="Failed to navigate to previous page",
)
def on_prev_btn_click(usergal_page_url: str, paging_information: Optional[Dict]) -> str:
    """Handle previous page button click."""
    page_url = usergal_page_url

    current_page = get_current_page(paging_information, usergal_page_url)
    if paging_information and paging_information.get("totalPageUrls"):
        total_page_urls = paging_information["totalPageUrls"]
        if current_page > 1:
            page_url = total_page_urls[current_page - 2]

    return page_url
