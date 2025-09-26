# encyclopedia/models.py
from django.db import models
from django.utils import timezone

class Comic(models.Model):
    """
    SOLID SRP: Single Responsibility Principle - this model ONLY represents comic data
    It doesn't handle searching, filtering, or business logic - just data representation
    
    SOLID OCP: Open/Closed Principle - we can extend this model with new methods
    without modifying existing functionality
    """

    bl_record_id = models.CharField(max_length=50, unique=True)  # keep leading zeros
    title = models.CharField(max_length=1000)  # a canonical/display title
    variant_titles = models.JSONField(default=list)  # list of variant titles
    authors = models.JSONField(default=list)  # list of author names
    publication_years = models.JSONField(default=list)  # list of years (strings)
    genres = models.JSONField(default=list)
    languages = models.JSONField(default=list)
    isbn = models.JSONField(default=list)  # list or ["missing"]
    other_fields = models.JSONField(default=dict)  # any other cleaned fields
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """
        SOLID SRP: Single Responsibility - only handles string representation
        """
        return f"{self.title} ({self.bl_record_id})"

    def get_isbn(self):
        """
        Returns ISBN or 'missing' if not present.
        
        SOLID OCP: Open/Closed Principle - this method can be extended with new ISBN 
        validation logic without modifying code that calls it
        
        SOLID SRP: Single Responsibility - only handles ISBN retrieval and formatting
        """
        if not self.isbn or self.isbn == [""]:
            return ["missing"]
        return self.isbn

    def get_multi_value_fields(self):
        """
        Returns multi-value fields as key-value pairs for display.
        
        SOLID SRP: Single Responsibility - this method ONLY formats multi-value fields
        It doesn't handle searching, validation, or other concerns
        
        SOLID OCP: Open/Closed - we can extend this to handle new field formats
        without modifying existing functionality
        """
        multi_fields = {}
        for key, value in self.other_fields.items():
            if isinstance(value, str) and ";" in value:
                # Split by semicolon and clean each value
                values = [v.strip() for v in value.split(";") if v.strip()]
                multi_fields[key] = values
            elif isinstance(value, list):
                multi_fields[key] = value
            elif value:  # Single value, non-empty
                multi_fields[key] = [str(value)]
        return multi_fields
    
    def get_formatted_field_display(self, field_name, values):
        """
        Formats field values for display as key:value pairs.
        
        SOLID SRP: Single Responsibility - only handles field display formatting
        This method has one reason to change: if display format requirements change
        """
        if not values:
            return f"{field_name}: None"
        
        if isinstance(values, list) and len(values) > 1:
            formatted_values = ", ".join(str(v) for v in values)
            return f"{field_name}: {formatted_values}"
        elif isinstance(values, list) and len(values) == 1:
            return f"{field_name}: {values[0]}"
        else:
            return f"{field_name}: {values}"

    def get_clean_title(self):
        """
        Cleans special characters from title for display.
        
        SOLID SRP: Single Responsibility - only handles title cleaning
        SOLID OCP: Open/Closed - we can extend this with new character replacements
        without modifying existing cleaning logic
        """
        import re
        # Handle special characters properly - replace with appropriate text
        title = self.title or ""
        # Replace common special characters with readable text
        replacements = {
            '&': ' and ',
            '@': ' at ',
            '#': ' number ',
            '%': ' percent ',
            '$': ' dollar ',
            '©': ' copyright ',
            '®': ' registered ',
            '™': ' trademark ',
        }
        for char, replacement in replacements.items():
            title = title.replace(char, replacement)
        
        # Remove remaining problematic characters but keep basic punctuation
        title = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)]', ' ', title)
        # Clean up multiple spaces
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def aggregate_variants(self):
        """
        Aggregates variant titles and related fields into a single record.
        
        SOLID OCP: Open/Closed - this method can be extended with new aggregation 
        logic without modifying existing code that uses it
        
        SOLID SRP: Single Responsibility - only handles data aggregation for variants
        """
        return {
            "title": self.title,
            "variant_titles": self.variant_titles,
            "authors": self.authors,
            "publication_years": self.publication_years,
            "isbn": self.get_isbn(),
            "languages": self.languages,
            "genres": self.genres,
            "other_fields": self.get_multi_value_fields(),
        }


class SearchLog(models.Model):
    """
    SOLID SRP: Single Responsibility - this model ONLY handles search logging data
    It doesn't perform searches or handle business logic, just stores search history
    
    SOLID OCP: Open/Closed - we can extend this with new logging fields without
    modifying existing functionality
    """
    query_text = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    result_ids = models.JSONField(default=list)  # list of bl_record_id strings
    num_results = models.IntegerField()
