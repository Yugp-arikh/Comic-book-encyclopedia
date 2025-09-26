from django.test import TestCase
from encyclopedia.models import Comic
from encyclopedia.services import ComicSearchService

class SimpleSearchTests(TestCase):
    def setUp(self):
        Comic.objects.create(
            bl_record_id="A1",
            title="Gamma",
            authors=["Alice"],
            publication_years=["2010"],
            genres=["Adventure"],
            languages=["English"],
            isbn=["11111"],
            other_fields={"editions": "First;Second"}
        )
        Comic.objects.create(
            bl_record_id="A2",
            title="Delta",
            authors=["Bob"],
            publication_years=["2011"],
            genres=["Horror"],
            languages=["French"],
            isbn=["missing"],
            other_fields={"editions": "Special"}
        )
        self.search_service = ComicSearchService()

    def test_basic_search_by_title(self):
        results = self.search_service.search(title_query="Gamma")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "A1")

    def test_filter_by_genre(self):
        results = self.search_service.search(genre="Horror")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "A2")

    def test_multi_value_field_parsing(self):
        comic = Comic.objects.get(bl_record_id="A1")
        multi = comic.get_multi_value_fields()
        self.assertIn("editions", multi)
        self.assertEqual(multi["editions"], ["First", "Second"])
