# encyclopedia/tests/test_integration.py
from django.test import TestCase, Client
from django.urls import reverse
from encyclopedia.models import Comic, SearchLog
from encyclopedia.services import ComicSearchService

class IntegrationTests(TestCase):
    """
    Integration tests to verify the complete system works according to requirements.
    SOLID: Single Responsibility - tests only integration scenarios.
    """
    
    def setUp(self):
        """Set up test data with special characters and multi-value fields."""
        # Create test comics with various scenarios
        Comic.objects.create(
            bl_record_id="001",
            title="Spider-Man & The X-Men",  # Special character
            authors=["Stan Lee", "Jack Kirby"],  # Multiple authors
            publication_years=["1963", "1964"],  # Multiple years
            genres=["Fantasy", "Adventure"],  # Multiple genres
            languages=["English"],
            isbn=["978-0123456789"],
            other_fields={
                "publisher": "Marvel Comics",
                "editions": "First;Second;Third",  # Semicolon-separated
                "physical_description": "Color illustrations"
            }
        )
        
        Comic.objects.create(
            bl_record_id="002",
            title="Batman: The Dark Knight Returns",
            variant_titles=["Dark Knight Returns", "Batman DKR"],
            authors=["Frank Miller"],
            publication_years=["1986"],
            genres=["Horror", "Drama"],
            languages=["English", "French"],
            isbn=["missing"],  # Missing ISBN
            other_fields={
                "publisher": "DC Comics",
                "notes": "Limited edition"
            }
        )
        
        Comic.objects.create(
            bl_record_id="003",
            title="Watchmen",
            authors=["Alan Moore", "Dave Gibbons"],
            publication_years=["1987"],
            genres=["Science fiction", "Drama"],
            languages=["English"],
            isbn=["978-1401245252"],
            other_fields={}
        )
        
        self.client = Client()
        self.search_service = ComicSearchService()

    def test_genre_filtering(self):
        """Test requirement: allow dataset to be filtered by genre."""
        # Test Fantasy genre filter
        results = self.search_service.search(genre="Fantasy")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "001")
        
        # Test Horror genre filter
        results = self.search_service.search(genre="Horror")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "002")

    def test_grouping_by_author_and_year(self):
        """Test requirement: comics can be grouped by Author or Year of Publication."""
        results = self.search_service.search()
        
        # Group by author
        author_groups = self.search_service.group(results, by="author")
        self.assertIn("Stan Lee", author_groups)
        self.assertIn("Frank Miller", author_groups)
        self.assertEqual(len(author_groups["Stan Lee"]), 1)
        
        # Group by year
        year_groups = self.search_service.group(results, by="year")
        self.assertIn("1963", year_groups)
        self.assertIn("1986", year_groups)
        self.assertIn("1987", year_groups)

    def test_alphabetical_sorting(self):
        """Test requirement: sort list by title alphabetically A-Z and Z-A."""
        results = self.search_service.search()
        
        # Sort A-Z
        sorted_asc = self.search_service.sort_results(results, order="asc")
        titles_asc = [comic.title for comic in sorted_asc]
        self.assertEqual(titles_asc, sorted(titles_asc))
        
        # Sort Z-A
        sorted_desc = self.search_service.sort_results(results, order="desc")
        titles_desc = [comic.title for comic in sorted_desc]
        self.assertEqual(titles_desc, sorted(titles_desc, reverse=True))

    def test_title_search(self):
        """Test requirement: user can enter a title manually and matching comics displayed."""
        # Search for partial title
        results = self.search_service.search(title_query="Spider")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "001")
        
        # Search for variant title
        results = self.search_service.search(title_query="Dark Knight")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "002")

    def test_special_character_handling(self):
        """Test requirement: program deals with special characters appropriately."""
        comic = Comic.objects.get(bl_record_id="001")
        clean_title = comic.get_clean_title()
        
        # Should handle & character appropriately
        self.assertIn("and", clean_title.lower())
        # Should not contain the original & character
        self.assertNotIn("&", clean_title)

    def test_multi_value_field_display(self):
        """Test requirement: multi-value fields displayed as description:value pairs."""
        comic = Comic.objects.get(bl_record_id="001")
        multi_fields = comic.get_multi_value_fields()
        
        # Check that semicolon-separated field is properly parsed
        self.assertIn("editions", multi_fields)
        self.assertEqual(multi_fields["editions"], ["First", "Second", "Third"])

    def test_missing_isbn_display(self):
        """Test requirement: missing ISBN must display 'missing'."""
        comic = Comic.objects.get(bl_record_id="002")
        isbn = comic.get_isbn()
        self.assertEqual(isbn, ["missing"])

    def test_variant_titles_aggregation(self):
        """Test requirement: multiple titles displayed as single record with variants."""
        comic = Comic.objects.get(bl_record_id="002")
        aggregated = comic.aggregate_variants()
        
        self.assertEqual(aggregated["title"], "Batman: The Dark Knight Returns")
        self.assertIn("Dark Knight Returns", aggregated["variant_titles"])
        self.assertIn("Batman DKR", aggregated["variant_titles"])

    def test_search_list_management(self):
        """Test requirement: user can save items to search list, cleared on exit."""
        session = self.client.session
        
        # Add comic to search list
        self.search_service.add_to_search_list(session, "001")
        search_list = session.get('search_list', [])
        self.assertIn("001", search_list)
        
        # Clear search list
        self.search_service.clear_search_list(session)
        search_list = session.get('search_list', [])
        self.assertEqual(search_list, [])

    def test_advanced_search(self):
        """Test requirement: advanced search with multiple parameters."""
        # Search with multiple criteria
        results = self.search_service.search(
            author="Alan Moore",
            year="1987",
            genre="Science fiction"
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].bl_record_id, "003")

    def test_search_logging_and_reports(self):
        """Test requirement: report on search queries and results."""
        # Perform some searches to generate logs
        self.search_service.search(title_query="Batman")
        self.search_service.search(genre="Fantasy")
        
        # Check that searches were logged
        logs = SearchLog.objects.all()
        self.assertGreater(len(logs), 0)
        
        # Test report generation
        top_queries = self.search_service.top_queries()
        self.assertGreater(len(top_queries), 0)
        
        top_results = self.search_service.top_results()
        self.assertGreater(len(top_results), 0)

    def test_web_interface_integration(self):
        """Test that web interface properly integrates with services."""
        # Test main search page
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        
        # Test search functionality
        response = self.client.get(reverse('search'), {'q': 'Batman'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Batman')
        
        # Test comic detail page
        response = self.client.get(reverse('comic_detail', args=['002']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Batman: The Dark Knight Returns')
        
        # Test advanced search
        response = self.client.get(reverse('advanced_search'))
        self.assertEqual(response.status_code, 200)
        
        # Test reports page
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)

    def test_session_persistence(self):
        """Test that search results are cleared and program restored to initial state."""
        # Add items to session
        session = self.client.session
        self.search_service.add_to_search_list(session, "001")
        session["last_search_results"] = ["001", "002"]
        session.save()
        
        # Clear search results
        response = self.client.get(reverse('clear_search_results'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Check that session is cleared
        updated_session = self.client.session
        self.assertEqual(updated_session.get('search_list', []), [])
        self.assertNotIn('last_search_results', updated_session)