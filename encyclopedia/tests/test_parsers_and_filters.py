from django.test import TestCase
from encyclopedia.parsers import parse_isbn
from encyclopedia.services import GenreFilter, AuthorFilter
from encyclopedia.models import Comic

class TestParseISBN(TestCase):
    def test_valid_isbn(self):
        self.assertEqual(parse_isbn('978-1234567890'), ['978-1234567890'])
        self.assertEqual(parse_isbn('978-1234567890,978-0987654321'), ['978-1234567890', '978-0987654321'])
        self.assertEqual(parse_isbn(' 978-1234567890 , 978-0987654321 '), ['978-1234567890', '978-0987654321'])

    def test_empty_isbn(self):
        self.assertEqual(parse_isbn(''), ['missing'])
        self.assertEqual(parse_isbn(None), ['missing'])

    def test_malformed_isbn(self):
        self.assertEqual(parse_isbn(' , , '), ['missing'])
        self.assertEqual(parse_isbn(' , 978-1234567890 , '), ['978-1234567890'])

class TestGenreFilter(TestCase):
    def setUp(self):
        Comic.objects.create(bl_record_id='1', title='A', genres=['Fantasy'])
        Comic.objects.create(bl_record_id='2', title='B', genres=['Horror'])
        self.qs = Comic.objects.all()
        self.filter = GenreFilter()

    def test_genre_filter(self):
        filtered = self.filter.apply_filter(self.qs, 'Fantasy')
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, 'A')
        filtered = self.filter.apply_filter(self.qs, 'Horror')
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, 'B')
        filtered = self.filter.apply_filter(self.qs, '')
        self.assertEqual(filtered.count(), 2)

class TestAuthorFilter(TestCase):
    def setUp(self):
        Comic.objects.create(bl_record_id='1', title='A', authors=['Alice'])
        Comic.objects.create(bl_record_id='2', title='B', authors=['Bob'])
        self.qs = Comic.objects.all()
        self.filter = AuthorFilter()

    def test_author_filter(self):
        filtered = self.filter.apply_filter(self.qs, 'Alice')
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, 'A')
        filtered = self.filter.apply_filter(self.qs, 'Bob')
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered.first().title, 'B')
        filtered = self.filter.apply_filter(self.qs, '')
        self.assertEqual(filtered.count(), 2)
