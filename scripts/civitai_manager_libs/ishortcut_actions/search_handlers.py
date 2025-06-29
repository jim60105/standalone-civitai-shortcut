"""
Search Handlers Module

Manages search operations, filters, and search result processing.
Handles search queries, result formatting, and search history.
"""

from typing import Any, Dict, List
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class SearchHandlers:
    """
    Manages search operations and result processing.
    Handles search queries, filters, and result formatting.
    """

    def __init__(self, ui_controllers=None):
        """
        Initialize search handlers.

        Args:
            ui_controllers: UI controllers instance
        """
        self.ui_controllers = ui_controllers
        self._search_history = []
        self._current_results = []
        self._search_filters = {}
        self._max_history = 50

    @with_error_handling("Failed to perform search")
    def perform_search(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Perform search operation.

        Args:
            query: Search query string
            filters: Optional search filters

        Returns:
            List[Dict[str, Any]]: Search results
        """
        if not query or not query.strip():
            logger.warning("Empty search query")
            return []

        # Add to search history
        self._add_to_history(query, filters)

        # Apply filters
        effective_filters = filters or {}
        effective_filters.update(self._search_filters)

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('search_query', query)
            self.ui_controllers.update_ui_state('search_filters', effective_filters)

        logger.info(f"Performing search: '{query}' with {len(effective_filters)} filters")

        # This would typically call the actual search implementation
        # For now, return empty results as this is just the handler structure
        results = []
        self._current_results = results

        return results

    @with_error_handling("Failed to apply search filter")
    def apply_filter(self, filter_name: str, filter_value: Any) -> bool:
        """
        Apply search filter.

        Args:
            filter_name: Name of the filter
            filter_value: Filter value

        Returns:
            bool: True if successful, False otherwise
        """
        self._search_filters[filter_name] = filter_value

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('search_filters', self._search_filters)

        logger.debug(f"Applied filter: {filter_name} = {filter_value}")
        return True

    def remove_filter(self, filter_name: str) -> bool:
        """
        Remove search filter.

        Args:
            filter_name: Name of filter to remove

        Returns:
            bool: True if removed, False if not found
        """
        if filter_name in self._search_filters:
            del self._search_filters[filter_name]

            # Update UI state
            if self.ui_controllers:
                self.ui_controllers.update_ui_state('search_filters', self._search_filters)

            logger.debug(f"Removed filter: {filter_name}")
            return True
        return False

    def clear_filters(self) -> None:
        """Clear all search filters."""
        self._search_filters.clear()

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('search_filters', {})

        logger.info("Cleared all search filters")

    def get_current_results(self) -> List[Dict[str, Any]]:
        """
        Get current search results.

        Returns:
            List[Dict[str, Any]]: Current results
        """
        return self._current_results.copy()

    def get_search_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get search history.

        Args:
            limit: Maximum number of items to return

        Returns:
            List[Dict[str, Any]]: Search history
        """
        history = self._search_history.copy()
        if limit is not None:
            history = history[-limit:]
        return history

    def clear_search_history(self) -> None:
        """Clear search history."""
        self._search_history.clear()
        logger.info("Search history cleared")

    def get_active_filters(self) -> Dict[str, Any]:
        """
        Get currently active filters.

        Returns:
            Dict[str, Any]: Active filters
        """
        return self._search_filters.copy()

    @with_error_handling("Failed to sort search results")
    def sort_results(self, sort_key: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort search results.

        Args:
            sort_key: Key to sort by
            reverse: Whether to reverse sort order

        Returns:
            List[Dict[str, Any]]: Sorted results
        """
        if not self._current_results:
            return []

        try:
            sorted_results = sorted(
                self._current_results, key=lambda x: x.get(sort_key, ''), reverse=reverse
            )
            self._current_results = sorted_results

            # Update UI state
            if self.ui_controllers:
                self.ui_controllers.update_ui_state('search_results', sorted_results)

            logger.debug(f"Sorted results by {sort_key} (reverse: {reverse})")
            return sorted_results
        except Exception as e:
            logger.error(f"Error sorting results: {e}")
            return self._current_results.copy()

    def _add_to_history(self, query: str, filters: Dict[str, Any] = None) -> None:
        """
        Add search to history.

        Args:
            query: Search query
            filters: Search filters
        """
        import time

        search_record = {
            'query': query,
            'filters': filters or {},
            'timestamp': time.time(),
            'result_count': 0,  # Will be updated when results are available
        }

        self._search_history.append(search_record)

        # Maintain history size limit
        if len(self._search_history) > self._max_history:
            self._search_history = self._search_history[-self._max_history :]


class SearchResultProcessor:
    """Processes and formats search results."""

    @staticmethod
    def format_results_for_display(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format search results for display.

        Args:
            results: Raw search results

        Returns:
            List[Dict[str, Any]]: Formatted results
        """
        formatted_results = []
        for result in results:
            formatted_result = {
                'id': result.get('id', ''),
                'title': result.get('name', 'Untitled'),
                'description': result.get('description', ''),
                'thumbnail': result.get('thumbnail_url', ''),
                'type': result.get('type', 'Unknown'),
                'rating': result.get('stats', {}).get('rating', 0),
                'download_count': result.get('stats', {}).get('downloadCount', 0),
                'created_at': result.get('createdAt', ''),
                'updated_at': result.get('updatedAt', ''),
                'tags': result.get('tags', []),
            }
            formatted_results.append(formatted_result)

        return formatted_results

    @staticmethod
    def filter_results(
        results: List[Dict[str, Any]], filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply filters to search results.

        Args:
            results: Results to filter
            filters: Filters to apply

        Returns:
            List[Dict[str, Any]]: Filtered results
        """
        filtered_results = results.copy()

        for filter_name, filter_value in filters.items():
            if filter_name == 'type' and filter_value:
                filtered_results = [r for r in filtered_results if r.get('type') == filter_value]
            elif filter_name == 'min_rating' and filter_value:
                filtered_results = [
                    r for r in filtered_results if r.get('rating', 0) >= filter_value
                ]
            elif filter_name == 'tags' and filter_value:
                if isinstance(filter_value, list):
                    for tag in filter_value:
                        filtered_results = [r for r in filtered_results if tag in r.get('tags', [])]
                else:
                    filtered_results = [
                        r for r in filtered_results if filter_value in r.get('tags', [])
                    ]
            elif filter_name == 'nsfw' and filter_value is False:
                filtered_results = [r for r in filtered_results if not r.get('nsfw', False)]

        return filtered_results

    @staticmethod
    def get_result_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about search results.

        Args:
            results: Search results

        Returns:
            Dict[str, Any]: Result statistics
        """
        if not results:
            return {'total_count': 0, 'type_counts': {}, 'average_rating': 0, 'total_downloads': 0}

        type_counts = {}
        total_rating = 0
        total_downloads = 0
        rating_count = 0

        for result in results:
            # Count types
            result_type = result.get('type', 'Unknown')
            type_counts[result_type] = type_counts.get(result_type, 0) + 1

            # Sum ratings
            rating = result.get('rating', 0)
            if rating > 0:
                total_rating += rating
                rating_count += 1

            # Sum downloads
            total_downloads += result.get('download_count', 0)

        return {
            'total_count': len(results),
            'type_counts': type_counts,
            'average_rating': total_rating / rating_count if rating_count > 0 else 0,
            'total_downloads': total_downloads,
        }


class SearchValidator:
    """Validates search queries and filters."""

    @staticmethod
    def validate_query(query: str) -> bool:
        """
        Validate search query.

        Args:
            query: Query to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(query and isinstance(query, str) and len(query.strip()) > 0)

    @staticmethod
    def validate_filters(filters: Dict[str, Any]) -> bool:
        """
        Validate search filters.

        Args:
            filters: Filters to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(filters, dict):
            return False

        # Validate specific filter types
        valid_filter_names = ['type', 'min_rating', 'tags', 'nsfw', 'sort', 'limit']
        for filter_name in filters.keys():
            if filter_name not in valid_filter_names:
                logger.warning(f"Unknown filter: {filter_name}")

        return True

    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize search query.

        Args:
            query: Query to sanitize

        Returns:
            str: Sanitized query
        """
        if not query:
            return ""

        # Remove excessive whitespace
        sanitized = " ".join(query.split())

        # Remove special characters that might cause issues
        import re

        sanitized = re.sub(r'[<>]', '', sanitized)

        return sanitized.strip()


class SearchSuggestions:
    """Provides search suggestions and auto-completion."""

    def __init__(self):
        """Initialize search suggestions."""
        self._suggestion_cache = {}
        self._popular_terms = []

    def get_suggestions(self, partial_query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions for partial query.

        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions

        Returns:
            List[str]: Search suggestions
        """
        if len(partial_query) < 2:
            return self._popular_terms[:limit]

        suggestions = []

        # Add cached suggestions
        for term in self._suggestion_cache.get(partial_query.lower(), []):
            if len(suggestions) < limit:
                suggestions.append(term)

        # Add popular terms that match
        for term in self._popular_terms:
            if partial_query.lower() in term.lower() and term not in suggestions:
                if len(suggestions) < limit:
                    suggestions.append(term)

        return suggestions

    def add_suggestion(self, term: str) -> None:
        """
        Add term to suggestions.

        Args:
            term: Term to add
        """
        if not term or len(term) < 2:
            return

        term_lower = term.lower()

        # Add to cache for various prefixes
        for i in range(2, len(term) + 1):
            prefix = term_lower[:i]
            if prefix not in self._suggestion_cache:
                self._suggestion_cache[prefix] = []
            if term not in self._suggestion_cache[prefix]:
                self._suggestion_cache[prefix].append(term)

    def update_popular_terms(self, terms: List[str]) -> None:
        """
        Update popular search terms.

        Args:
            terms: List of popular terms
        """
        self._popular_terms = terms[:50]  # Keep top 50
