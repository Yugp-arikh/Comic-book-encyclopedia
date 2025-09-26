# encyclopedia/repositories.py
from .models import Comic
from django.db import transaction

class ComicRepository:
    # SOLID: Single Responsibility Principle - repository only handles data access
    @staticmethod
    def get_by_bl_id(bl_id: str):
        return Comic.objects.filter(bl_record_id=bl_id).first()

    @staticmethod
    def upsert_from_parsed(parsed: dict):
        obj = Comic.objects.filter(bl_record_id=parsed["bl_record_id"]).first()
        if obj is None:
            obj = Comic(bl_record_id=parsed["bl_record_id"])
        # merge lists: union
        obj.title = parsed["title"] or obj.title or parsed["title"]
        obj.variant_titles = list({*obj.variant_titles, *parsed.get("variant_titles", [])}) if obj.pk else parsed.get("variant_titles", [])
        obj.authors = list({*obj.authors, *parsed.get("authors", [])}) if obj.pk else parsed.get("authors", [])
        obj.publication_years = list({*obj.publication_years, *parsed.get("publication_years", [])}) if obj.pk else parsed.get("publication_years", [])
        obj.genres = list({*obj.genres, *parsed.get("genres", [])}) if obj.pk else parsed.get("genres", [])
        obj.languages = list({*obj.languages, *parsed.get("languages", [])}) if obj.pk else parsed.get("languages", [])
        obj.isbn = parsed.get("isbn", ["missing"])
        obj.other_fields = {**(obj.other_fields or {}), **parsed.get("other_fields", {})}
        obj.save()
        return obj

    @staticmethod
    def filter_by_genre(genre):
        """
        Returns comics filtered by genre.
        SOLID: Open/Closed - can add new filters without changing callers.
        """
        return Comic.objects.filter(genres__contains=[genre])

    @staticmethod
    def group_by_author(comics):
        """
        Groups comics by author.
        """
        from collections import defaultdict
        grouped = defaultdict(list)
        for comic in comics:
            for author in comic.authors:
                grouped[author].append(comic)
        return grouped

    @staticmethod
    def group_by_year(comics):
        """
        Groups comics by year of publication.
        """
        from collections import defaultdict
        grouped = defaultdict(list)
        for comic in comics:
            for year in comic.publication_years:
                grouped[year].append(comic)
        return grouped

    @staticmethod
    def sort_by_title(comics, order="asc"):
        """
        Sorts comics by title alphabetically.
        """
        return sorted(comics, key=lambda c: c.title, reverse=(order=="desc"))

    @staticmethod
    def search_by_title(title):
        """
        Returns comics matching title (case-insensitive, partial).
        """
        return Comic.objects.filter(title__icontains=title)

    @staticmethod
    def get_comics_with_missing_isbn():
        """
        Returns comics missing ISBN.
        """
        return Comic.objects.filter(isbn__contains=["missing"])

    @staticmethod
    def aggregate_variants(title):
        """
        Returns all comics with the same title as variants.
        """
        return Comic.objects.filter(title=title)

    @staticmethod
    def get_top_search_queries():
        """
        Returns top 10 search queries from SearchLog.
        """
        from .models import SearchLog
        from django.db.models import Count
        return SearchLog.objects.values('query_text').annotate(count=Count('id')).order_by('-count')[:10]

    @staticmethod
    def get_top_search_results():
        """
        Returns top 10 comics by number of times in search results.
        """
        from .models import SearchLog
        from collections import Counter
        all_ids = []
        for log in SearchLog.objects.all():
            all_ids.extend(log.result_ids)
        top_ids = [item for item, _ in Counter(all_ids).most_common(10)]
        return Comic.objects.filter(bl_record_id__in=top_ids)

    @staticmethod
    def get_comics_in_many_searches(threshold=100):
        """
        Returns comics included in more than threshold search results.
        """
        from .models import SearchLog
        from collections import Counter
        all_ids = []
        for log in SearchLog.objects.all():
            all_ids.extend(log.result_ids)
        counter = Counter(all_ids)
        ids = [item for item, count in counter.items() if count > threshold]
        return Comic.objects.filter(bl_record_id__in=ids)
