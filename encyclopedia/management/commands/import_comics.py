# encyclopedia/management/commands/import_comics.py
import csv
from django.core.management.base import BaseCommand
from pathlib import Path
from encyclopedia.parsers import parse_row_to_record
from encyclopedia.repositories import ComicRepository
import chardet
import re

CSV_FILES = [
    "names.csv",   # you provided these files. adjust paths if needed.
    "titles.csv",
    "records.csv"
]

class Command(BaseCommand):
    help = "Import comics from CSV files into the Comic model with proper special character handling"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean-special-chars',
            action='store_true',
            help='Clean special characters during import',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed import progress',
        )

    def clean_special_characters(self, text):
        """
        Clean special characters from text while preserving readability.
        SOLID: Single Responsibility - only handles character cleaning.
        """
        if not text:
            return text
            
        # Replace common problematic characters with readable alternatives
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
            text = text.replace(char, replacement)
        
        # Remove other problematic characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)]', ' ', text)
        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def handle(self, *args, **options):
        clean_chars = options['clean_special_chars']
        verbose = options['verbose']
        
        total_imported = 0
        total_errors = 0
        
        self.stdout.write(self.style.SUCCESS("Starting comic import process..."))
        
        base = Path.cwd()
        for fname in CSV_FILES:
            path = base / fname
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"File not found: {path}"))
                continue

            # Detect encoding to handle MARC8->UTF-8 issues
            raw = path.read_bytes()
            detected = chardet.detect(raw)
            enc = detected["encoding"] or "utf-8"
            confidence = detected.get("confidence", 0)
            
            self.stdout.write(f"Processing {fname}:")
            self.stdout.write(f"  - Detected encoding: {enc} (confidence: {confidence:.2f})")
            
            try:
                with path.open("r", encoding=enc, errors="replace") as fh:
                    reader = csv.DictReader(fh)
                    count = 0
                    errors = 0
                    
                    for row_num, row in enumerate(reader, 1):
                        try:
                            # Clean special characters if requested
                            if clean_chars:
                                cleaned_row = {}
                                for key, value in row.items():
                                    if isinstance(value, str):
                                        cleaned_row[key] = self.clean_special_characters(value)
                                    else:
                                        cleaned_row[key] = value
                                row = cleaned_row
                            
                            parsed = parse_row_to_record(row)
                            if parsed.get("bl_record_id"):
                                ComicRepository.upsert_from_parsed(parsed)
                                count += 1
                                
                                if verbose and count % 100 == 0:
                                    self.stdout.write(f"    Processed {count} records...")
                                    
                        except Exception as e:
                            errors += 1
                            if verbose:
                                self.stdout.write(
                                    self.style.WARNING(f"    Error on row {row_num}: {str(e)}")
                                )
                    
                    total_imported += count
                    total_errors += errors
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"  - Imported {count} records from {fname}")
                    )
                    if errors > 0:
                        self.stdout.write(
                            self.style.WARNING(f"  - {errors} errors encountered")
                        )
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to process {fname}: {str(e)}")
                )
                continue
        
        # Final summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*50))
        self.stdout.write(self.style.SUCCESS("IMPORT COMPLETE"))
        self.stdout.write(self.style.SUCCESS(f"Total records imported: {total_imported}"))
        if total_errors > 0:
            self.stdout.write(self.style.WARNING(f"Total errors: {total_errors}"))
        self.stdout.write(self.style.SUCCESS("="*50))
