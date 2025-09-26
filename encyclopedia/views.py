# encyclopedia/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .services import ComicSearchService
from .models import Comic
from django.views.decorators.http import require_POST

# SOLID PRINCIPLE: Dependency Injection (part of DIP)
# We create the service instance once and reuse it, rather than creating it in each view
# This makes testing easier and follows the DIP principle
search_service = ComicSearchService()

def index(request):
    """
    SOLID SRP: Single Responsibility Principle - this view ONLY handles 
    the HTTP request/response for the home page. It doesn't contain business logic.
    
    SOLID DIP: Dependency Inversion - if we needed search logic, we'd delegate 
    to the search_service rather than implementing it here
    """
    return render(request, "index.html", {})

def search(request):
    """
    SOLID SRP: Single Responsibility - this view only handles HTTP request/response
    All business logic is delegated to the search service
    
    SOLID DIP: Dependency Inversion - we depend on the ComicSearchService abstraction
    rather than implementing search logic directly in the view
    """
    # Extract request parameters (view responsibility)
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre")
    author = request.GET.get("author")
    year = request.GET.get("year")
    group_by = request.GET.get("group_by")
    order = request.GET.get("order", "asc")
    languages = request.GET.getlist("languages")
    
    # SOLID DIP: Delegate business logic to service layer
    results = search_service.search(title_query=q, genre=genre, author=author, year=year, languages=languages)
    if order:
        results = search_service.sort_results(results, order)
    groups = search_service.group(results, by=group_by) if group_by else None
    
    # Handle session management (view responsibility)
    request.session["last_search_results"] = [c.bl_record_id for c in results]
    context = {"results": results, "groups": groups, "query": q, "order": order, "group_by": group_by}
    return render(request, "search_results.html", context)

def comic_detail(request, bl_id):
    """
    SOLID SRP: Single Responsibility - this view only handles displaying a single comic
    It doesn't handle searching, filtering, or other unrelated functionality
    """
    comic = get_object_or_404(Comic, bl_record_id=bl_id)
    return render(request, "comic_details.html", {"comic": comic})

@require_POST
def save_to_search_list(request):
    """
    SOLID SRP: Single Responsibility - only handles adding comics to search list
    SOLID DIP: Dependency Inversion - delegates business logic to search service
    """
    bl_id = request.POST.get("bl_id")
    if bl_id:
        # SOLID DIP: We depend on the service interface, not implementation details
        search_service.add_to_search_list(request.session, bl_id)
    return redirect(request.POST.get("next", "/"))

def clear_search_results(request):
    """
    SOLID SRP: Single Responsibility - only handles clearing search data
    SOLID DIP: Delegates to service rather than implementing clearing logic here
    """
    # SOLID DIP: Use service for business logic
    search_service.clear_search_list(request.session)
    request.session.pop("last_search_results", None)
    return redirect("index")

def advanced_search(request):
    """
    Advanced search view with comprehensive form handling.
    
    SOLID SRP: Single Responsibility - this view only handles HTTP request/response
    for advanced search. All search logic is delegated to the service layer.
    
    SOLID DIP: Dependency Inversion - we depend on ComicSearchService abstraction
    rather than implementing search algorithms in the view
    """
    if request.method == "POST":
        # Extract and clean form data
        raw_data = {
            'author': request.POST.get("author", ""),
            'year': request.POST.get("year", ""),
            'genre': request.POST.get("genre", ""),
            'edition': request.POST.get("edition", ""),
            'name_type': request.POST.get("name_type", ""),
            'languages': request.POST.get("languages", ""),
        }
        
        # Clean the data
        author = raw_data['author'].strip() or None
        year = raw_data['year'].strip() or None
        genre = raw_data['genre'].strip() or None
        edition = raw_data['edition'].strip() or None
        name_type = raw_data['name_type'].strip() or None
        
        # Handle languages - split by comma and clean
        languages = None
        if raw_data['languages'].strip():
            languages = [l.strip() for l in raw_data['languages'].split(",") if l.strip()]
        
        cleaned_data = {
            'author': author,
            'year': year,
            'genre': genre,
            'edition': edition,
            'name_type': name_type,
            'languages': languages,
        }
        
        # Check if any search criteria provided
        has_criteria = any(v for v in cleaned_data.values())
        
        if not has_criteria:
            # No search criteria provided - return empty results with message
            context = {
                "results": [],
                "search_params": cleaned_data,
                "error_message": "Please provide at least one search criterion."
            }
            return render(request, "search_results.html", context)
        
        # Perform the search
        try:
            results = search_service.search(
                author=author, 
                year=year, 
                genre=genre, 
                edition=edition, 
                name_type=name_type, 
                languages=languages
            )
            

            
            # Store results in session
            request.session["last_search_results"] = [c.bl_record_id for c in results]
            
            # Prepare context for template
            context = {
                "results": results,
                "search_params": {
                    "author": author,
                    "year": year,
                    "genre": genre,
                    "edition": edition,
                    "name_type": name_type,
                    "languages": raw_data['languages'],  # Keep original for display
                },
                "debug_info": {
                    "total_comics": Comic.objects.count(),
                    "search_criteria_count": sum(1 for v in cleaned_data.values() if v),
                }
            }
            
            return render(request, "search_results.html", context)
            
        except Exception as e:
            
            context = {
                "results": [],
                "search_params": cleaned_data,
                "error_message": f"Search error: {str(e)}"
            }
            return render(request, "search_results.html", context)
    
    # GET request - show the form
    return render(request, "advanced_search.html")


def reports(request):
    """
    SOLID SRP: Single Responsibility - only handles displaying reports
    SOLID DIP: Dependency Inversion - delegates all reporting logic to service layer
    """
    # SOLID DIP: All business logic is handled by the service
    top_queries = search_service.top_queries()
    top_results = search_service.top_results()
    high_freq = search_service.names_in_more_than_n_results(100)
    return render(request, "reports.html", {"top_queries": top_queries, "top_results": top_results, "high_freq": high_freq})

def view_search_list(request):
    """
    SOLID SRP: Single Responsibility - only handles displaying the user's search list
    SOLID DIP: Delegates search list retrieval to service layer
    """
    # SOLID DIP: Service handles the business logic of retrieving search list
    comics = search_service.get_search_list(request.session)
    return render(request, "search_list.html", {"comics": comics})

def browse_comics(request):
    """
    Browse comics with pagination - helps users discover what's available.
    
    SOLID SRP: Single Responsibility - this view only handles the HTTP request/response
    for browsing comics. It doesn't handle searching or other unrelated functionality.
    
    SOLID OCP: Open/Closed - we could extend this with new browsing features
    without modifying the existing pagination logic
    """
    from django.core.paginator import Paginator
    
    # Get all comics ordered by title
    all_comics = Comic.objects.all().order_by('title')
    
    # Paginate results (50 per page)
    paginator = Paginator(all_comics, 50)
    page_number = request.GET.get('page', 1)
    comics = paginator.get_page(page_number)
    
    # Get some statistics for display
    total_comics = Comic.objects.count()
    sample_authors = Comic.objects.exclude(authors__exact=[]).values_list('authors', flat=True)[:100]
    unique_authors = set()
    for author_list in sample_authors:
        if author_list:
            unique_authors.update(author_list)
    
    sample_genres = Comic.objects.exclude(genres__exact=[]).values_list('genres', flat=True)[:100]
    unique_genres = set()
    for genre_list in sample_genres:
        if genre_list:
            unique_genres.update(genre_list)
    
    context = {
        'comics': comics,
        'total_comics': total_comics,
        'sample_authors': sorted(list(unique_authors))[:20],
        'sample_genres': sorted(list(unique_genres))[:15],
    }
    
    return render(request, "browse_comics.html", context)

from django.views.decorators.http import require_POST
@require_POST
def remove_from_search_list(request):
    bl_id = request.POST.get("bl_id")
    search_list = request.session.get("search_list", [])
    if bl_id in search_list:
        search_list.remove(bl_id)
        request.session["search_list"] = search_list
    return redirect("view_search_list")
