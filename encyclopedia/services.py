# encyclopedia/services.py
from .models import Comic, SearchLog
from django.db.models import Q
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import logging

# Set up logging for debugging
logger = logging.getLogger(__name__)

# SOLID PRINCIPLE: Interface Segregation Principle (ISP)
# We create separate, focused interfaces rather than one large interface
# Each interface has a single, specific responsibility
class SearchFilterInterface(ABC):
    """
    SOLID ISP: Interface for search filters - only contains filter-related methods
    This ensures classes only depend on methods they actually use
    """
    @abstractmethod
    def apply_filter(self, queryset, value) -> Any:
        pass
    
    @abstractmethod
    def get_filter_name(self) -> str:
        pass

class SortStrategyInterface(ABC):
    """
    SOLID ISP: Separate interface for sorting strategies
    Classes that only need sorting don't need to know about filtering or grouping
    """
    @abstractmethod
    def sort(self, results: List[Comic]) -> List[Comic]:
        pass

class GroupStrategyInterface(ABC):
    """
    SOLID ISP: Separate interface for grouping strategies
    Keeps grouping logic separate from filtering and sorting
    """
    @abstractmethod
    def group(self, results: List[Comic]) -> Dict:
        pass

# SOLID PRINCIPLE: Single Responsibility Principle (SRP)
# Each filter class has only ONE responsibility - filtering by a specific field
# If we need to change how genre filtering works, we only modify GenreFilter
class GenreFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by genre
    SOLID OCP: Can be extended for new genre logic without modifying existing code
    """
    def get_filter_name(self) -> str:
        return "Genre"
    
    def apply_filter(self, queryset, value):
        if not value or not value.strip():
            return queryset
        
        value = value.strip()
        # Use only icontains for SQLite compatibility
        filtered_qs = queryset.filter(genres__icontains=value)
        return filtered_qs

class AuthorFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by author
    SOLID LSP: Can be substituted for any SearchFilterInterface without breaking functionality
    """
    def get_filter_name(self) -> str:
        return "Author"
    
    def apply_filter(self, queryset, value):
        if not value or not value.strip():
            return queryset
        
        value = value.strip()
        # Use only icontains for SQLite compatibility
        filtered_qs = queryset.filter(authors__icontains=value)
        return filtered_qs

class YearFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by publication year
    SOLID OCP: Open for extension (new year logic) but closed for modification
    """
    def get_filter_name(self) -> str:
        return "Year"
    
    def apply_filter(self, queryset, value):
        if not value or not value.strip():
            return queryset
        
        value = value.strip()
        # Use only icontains for SQLite compatibility
        filtered_qs = queryset.filter(publication_years__icontains=value)
        return filtered_qs

class TitleFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by title (main and variant)
    SOLID ISP: Implements only the methods it needs from SearchFilterInterface
    """
    def get_filter_name(self) -> str:
        return "Title"
    
    def apply_filter(self, queryset, value):
        if not value or not value.strip():
            return queryset
        
        value = value.strip()
        filtered_qs = queryset.filter(
            Q(title__icontains=value) |
            Q(variant_titles__icontains=value)
        )
        return filtered_qs

class LanguageFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by language
    SOLID OCP: Can be extended to handle new language formats without changing existing code
    """
    def get_filter_name(self) -> str:
        return "Language"
    
    def apply_filter(self, queryset, value):
        if not value:
            return queryset
        
        # Handle both list and string inputs
        if isinstance(value, str):
            languages = [lang.strip() for lang in value.split(',') if lang.strip()]
        else:
            languages = [lang.strip() for lang in value if lang and lang.strip()]
        
        if not languages:
            return queryset
        
        q = Q()
        for lang in languages:
            q |= Q(languages__icontains=lang)
        
        filtered_qs = queryset.filter(q)
        return filtered_qs

class EditionFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by edition information
    SOLID LSP: Fully substitutable for any SearchFilterInterface
    """
    def get_filter_name(self) -> str:
        return "Edition"
    
    def apply_filter(self, queryset, value):
        if not value or not value.strip():
            return queryset
        
        value = value.strip()
        filtered_qs = queryset.filter(other_fields__icontains=value)
        return filtered_qs

class NameTypeFilter(SearchFilterInterface):
    """
    SOLID SRP: Only responsible for filtering comics by name type information
    SOLID DIP: Depends on the SearchFilterInterface abstraction, not concrete implementations
    """
    def get_filter_name(self) -> str:
        return "Name Type"
    
    def apply_filter(self, queryset, value):
        if not value or not value.strip():
            return queryset
        
        value = value.strip()
        filtered_qs = queryset.filter(other_fields__icontains=value)
        return filtered_qs

# SOLID PRINCIPLE: Strategy Pattern (part of Open/Closed Principle)
# We can add new sorting algorithms without modifying existing code
class AlphabeticalSortStrategy(SortStrategyInterface):
    """
    SOLID OCP: Open for extension (new sorting methods) but closed for modification
    SOLID SRP: Only responsible for alphabetical sorting logic
    """
    def __init__(self, reverse=False):
        self.reverse = reverse
    
    def sort(self, results: List[Comic]) -> List[Comic]:
        return sorted(results, key=lambda c: (c.title or "").lower(), reverse=self.reverse)

# SOLID PRINCIPLE: Strategy Pattern - interchangeable grouping algorithms
# Each grouping strategy can be swapped without affecting other parts of the system
class AuthorGroupStrategy(GroupStrategyInterface):
    """
    SOLID SRP: Only responsible for grouping comics by author
    SOLID LSP: Can be substituted for any GroupStrategyInterface
    """
    def group(self, results: List[Comic]) -> Dict:
        groups = {}
        for comic in results:
            authors = comic.authors or ["Unknown"]
            for author in authors:
                groups.setdefault(author, []).append(comic)
        return groups

class YearGroupStrategy(GroupStrategyInterface):
    """
    SOLID SRP: Only responsible for grouping comics by publication year
    SOLID OCP: Can be extended with new year grouping logic without modification
    """
    def group(self, results: List[Comic]) -> Dict:
        groups = {}
        for comic in results:
            years = comic.publication_years or ["Unknown"]
            for year in years:
                groups.setdefault(year, []).append(comic)
        return groups

# SOLID PRINCIPLE: Dependency Inversion Principle (DIP)
# This class depends on abstractions (interfaces) not concrete implementations
class ComicSearchService:
    """
    Main search service implementing ALL SOLID principles:
    
    SOLID SRP: Single Responsibility - only handles search orchestration and coordination
    SOLID OCP: Open for extension (new filters/strategies) but closed for modification
    SOLID LSP: All strategies can be substituted without breaking functionality
    SOLID ISP: Uses focused interfaces (SearchFilterInterface, SortStrategyInterface, etc.)
    SOLID DIP: Depends on abstractions (interfaces) not concrete classes
    """
    
    def __init__(self):
        # SOLID DIP: Dependency Injection - we inject strategy objects (abstractions)
        # rather than creating concrete classes directly
        # This makes the system flexible and testable
        self.filters = {
            'genre': GenreFilter(),
            'author': AuthorFilter(),
            'year': YearFilter(),
            'title': TitleFilter(),
            'languages': LanguageFilter(),
            'edition': EditionFilter(),
            'name_type': NameTypeFilter(),
        }
        # SOLID OCP: We can add new sorting strategies without modifying existing code
        self.sort_strategies = {
            'asc': AlphabeticalSortStrategy(reverse=False),
            'desc': AlphabeticalSortStrategy(reverse=True),
        }
        # SOLID LSP: All group strategies are interchangeable
        self.group_strategies = {
            'author': AuthorGroupStrategy(),
            'year': YearGroupStrategy(),
        }

    def _clean_search_params(self, **kwargs) -> Dict[str, Any]:
        """
        Clean and validate search parameters.
        
        SOLID SRP: Single Responsibility - this method ONLY handles parameter cleaning
        It doesn't search, filter, or do anything else - just cleans data
        """
        cleaned = {}
        
        for key, value in kwargs.items():
            if value is None:
                cleaned[key] = None
            elif isinstance(value, str):
                stripped = value.strip()
                cleaned[key] = stripped if stripped else None
            elif isinstance(value, list):
                # Handle list parameters (like languages)
                clean_list = [item.strip() for item in value if item and str(item).strip()]
                cleaned[key] = clean_list if clean_list else None
            else:
                cleaned[key] = value
        
        return cleaned

    def search(self, title_query: str = None, genre: str = None, author: str = None,
               year: str = None, edition: str = None, languages: List[str] = None,
               name_type: str = None) -> List[Comic]:
        """
        Advanced search supporting multiple parameters.
        
        SOLID OCP: Open/Closed Principle - we can add new search parameters 
        by creating new filter classes without modifying this method
        
        SOLID DIP: Dependency Inversion - this method depends on the 
        SearchFilterInterface abstraction, not concrete filter implementations
        """
        # SOLID SRP: Delegate parameter cleaning to a focused method
        params = self._clean_search_params(
            title_query=title_query,
            genre=genre,
            author=author,
            year=year,
            edition=edition,
            languages=languages,
            name_type=name_type
        )
        
        # Start with all comics
        qs = Comic.objects.all()
        
        # SOLID OCP & DIP: Apply filters using strategy pattern
        # We can add new filters without changing this code
        search_params = {
            'genre': params['genre'],
            'author': params['author'],
            'year': params['year'],
            'title': params['title_query'],
            'languages': params['languages'],
            'edition': params['edition'],
            'name_type': params['name_type'],
        }
        
        # Track which filters are applied for logging
        applied_filters = []
        
        # SOLID LSP: All filters implement the same interface and can be substituted
        for param_name, param_value in search_params.items():
            if param_value and param_name in self.filters:
                # SOLID DIP: We call the interface method, not knowing the concrete implementation
                qs = self.filters[param_name].apply_filter(qs, param_value)
                applied_filters.append(f"{param_name}={param_value}")
                
                # Early exit if no results
                if not qs.exists():
                    break
        
        # Convert to list and limit results
        results = list(qs.order_by("title")[:10000])
        
        # Log the search for analytics
        query_text = " AND ".join(applied_filters) if applied_filters else "empty_search"
        try:
            SearchLog.objects.create(
                query_text=query_text,
                result_ids=[c.bl_record_id for c in results],
                num_results=len(results)
            )
        except Exception:
            # Silently fail if logging doesn't work
            pass
        
        return results

    def group(self, results: List[Comic], by: str = "author") -> Dict:
        """
        Groups comics using strategy pattern.
        
        SOLID OCP: Open/Closed - we can add new grouping strategies without modifying this method
        SOLID LSP: Liskov Substitution - all group strategies are interchangeable
        SOLID DIP: Depends on GroupStrategyInterface abstraction, not concrete classes
        """
        if by in self.group_strategies:
            # SOLID DIP: We call the interface method without knowing the concrete implementation
            return self.group_strategies[by].group(results)
        return {}

    def sort_results(self, results: List[Comic], order: str = "asc") -> List[Comic]:
        """
        Sorts comics using strategy pattern.
        
        SOLID OCP: Open/Closed - we can add new sorting algorithms without changing this code
        SOLID LSP: All sort strategies implement the same interface and are substitutable
        SOLID SRP: This method only coordinates sorting, doesn't implement sorting logic
        """
        if order in self.sort_strategies:
            # SOLID DIP: We depend on the SortStrategyInterface, not concrete sorting classes
            return self.sort_strategies[order].sort(results)
        return results

    def top_queries(self, limit=10):
        """
        Returns top search queries.
        """
        qs = SearchLog.objects.order_by("-timestamp")
        aggregated = {}
        for s in SearchLog.objects.all():
            aggregated[s.query_text] = aggregated.get(s.query_text, 0) + 1
        items = sorted(aggregated.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        return items

    def top_results(self, limit=10):
        """
        Returns top search results.
        """
        counts = {}
        for log in SearchLog.objects.all():
            for rid in log.result_ids:
                counts[rid] = counts.get(rid, 0) + 1
        items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        comics = []
        for rid, cnt in items:
            comic = Comic.objects.filter(bl_record_id=rid).first()
            comics.append((comic, cnt))
        return comics

    def names_in_more_than_n_results(self, n=100):
        """
        Returns comic names included in more than n search results.
        """
        counts = {}
        for log in SearchLog.objects.all():
            for rid in log.result_ids:
                counts[rid] = counts.get(rid, 0) + 1
        out = []
        for rid, cnt in counts.items():
            if cnt > n:
                comic = Comic.objects.filter(bl_record_id=rid).first()
                if comic:
                    out.append((comic.title, cnt))
        return out

    # Search list management (in-memory, per session)
    def add_to_search_list(self, session, comic_id):
        """
        Adds a comic to the user's search list in session.
        SOLID: Single Responsibility - only manages search list.
        """
        search_list = session.get('search_list', [])
        if comic_id not in search_list:
            search_list.append(comic_id)
        session['search_list'] = search_list

    def clear_search_list(self, session):
        """
        Clears the user's search list in session.
        """
        session['search_list'] = []

    def get_search_list(self, session):
        """
        Returns the user's search list comics.
        """
        ids = session.get('search_list', [])
        return Comic.objects.filter(bl_record_id__in=ids)
