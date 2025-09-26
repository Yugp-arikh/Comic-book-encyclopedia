# Comics Encyclopedia

A Django-based web application for searching and managing a comics database with advanced filtering, grouping, and reporting capabilities.

## Features

### Core Search Functionality
- **Genre Filtering**: Filter comics by Fantasy, Horror, Science Fiction, and other genres
- **Grouping**: Group search results by Author or Year of Publication
- **Alphabetical Sorting**: Sort results A-Z or Z-A by title
- **Title Search**: Search by comic title or variant titles with partial matching
- **Advanced Search**: Multi-parameter search with author, year, genre, edition, languages, and name type

### Data Handling
- **Special Character Processing**: Properly handles and displays special characters in titles and descriptions
- **Multi-value Fields**: Displays semicolon-separated values as formatted lists (e.g., "First;Second;Third" → "First, Second, Third")
- **Missing ISBN Handling**: Clearly marks comics with missing ISBN information
- **Variant Title Aggregation**: Multiple titles for the same comic are displayed as a single record with variant information

### User Experience
- **Search List Management**: Save comics to a temporary search list during your session
- **Session-based Storage**: No account required - search lists are cleared when you exit
- **Responsive Design**: Modern, mobile-friendly interface
- **Detailed Comic Views**: Comprehensive information display with proper formatting

### Reporting & Analytics
- **Top Search Queries**: Track the most frequently searched terms
- **Popular Results**: Identify comics that appear most often in search results
- **High-frequency Comics**: Find comics appearing in more than 100 search results

## Technical Architecture

### SOLID Principles Implementation

The application follows SOLID design principles throughout:

#### Single Responsibility Principle (SRP)
- **Models**: Only handle data representation and basic formatting
- **Services**: Handle business logic and search operations
- **Views**: Only manage HTTP request/response
- **Repositories**: Handle data access patterns
- **Filters**: Each filter class handles one type of search criteria

#### Open/Closed Principle (OCP)
- **Search Filters**: New search criteria can be added without modifying existing code
- **Sort Strategies**: New sorting methods can be added via strategy pattern
- **Group Strategies**: New grouping methods can be added without changing callers

#### Liskov Substitution Principle (LSP)
- **Filter Interfaces**: All filters implement the same interface and can be substituted
- **Strategy Patterns**: Sort and group strategies are interchangeable

#### Interface Segregation Principle (ISP)
- **Separate Interfaces**: SearchFilterInterface, SortStrategyInterface, GroupStrategyInterface
- **Focused Responsibilities**: Each interface has a single, focused purpose

#### Dependency Inversion Principle (DIP)
- **Service Dependencies**: ComicSearchService depends on abstractions, not concrete implementations
- **Strategy Injection**: Strategies are injected rather than hard-coded

### Key Components

#### Services Layer (`encyclopedia/services.py`)
- `ComicSearchService`: Main search orchestration with strategy pattern implementation
- Filter classes: `GenreFilter`, `AuthorFilter`, `YearFilter`, `TitleFilter`, `LanguageFilter`
- Sort strategies: `AlphabeticalSortStrategy`
- Group strategies: `AuthorGroupStrategy`, `YearGroupStrategy`

#### Models (`encyclopedia/models.py`)
- `Comic`: Main comic data model with helper methods for display formatting
- `SearchLog`: Tracks search queries for reporting
- Special character handling and multi-value field processing

#### Views (`encyclopedia/views.py`)
- Thin controllers that delegate to services
- Session management for search lists
- Proper separation of concerns

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd comicsencyclopedia
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Import comic data**
   ```bash
   # Basic import
   python manage.py import_comics
   
   # Import with special character cleaning
   python manage.py import_comics --clean-special-chars
   
   # Verbose import with progress details
   python manage.py import_comics --verbose --clean-special-chars
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Start searching and exploring comics!

## Usage Guide

### Basic Search
1. Go to the home page
2. Enter a comic title in the search box
3. Optionally select a genre filter
4. Choose grouping and sorting options
5. Click "Search Comics"

### Advanced Search
1. Click "Advanced Search" from the home page
2. Fill in any combination of search criteria:
   - Author name
   - Publication year
   - Genre
   - Edition/format
   - Languages (comma-separated)
   - Name type
3. Click "Search Comics"

### Managing Your Search List
1. From search results or comic detail pages, click "Add to Search List"
2. View your saved comics by clicking "My Search List" in the navigation
3. Remove individual items or clear the entire list
4. Lists are automatically cleared when you close your browser

### Viewing Reports
1. Click "Reports" in the navigation
2. View analytics on:
   - Most popular search queries
   - Most frequently found comics
   - Comics appearing in many search results

## Data Format

The system expects CSV files with the following columns:
- `BL record ID`: Unique identifier
- `Title`: Main comic title
- `Variant titles`: Alternative titles (semicolon-separated)
- `Name`: Author names (semicolon-separated)
- `Date of publication`: Publication years (semicolon-separated)
- `Genre`: Comic genres (semicolon-separated)
- `Languages`: Available languages (semicolon-separated)
- `ISBN`: ISBN numbers (semicolon-separated)
- Additional fields: `Publisher`, `Place of publication`, `Topics`, `Physical description`, `Notes`

## Testing

Run the test suite to verify functionality:

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test encyclopedia.tests.test_search
python manage.py test encyclopedia.tests.test_integration

# Run with verbose output
python manage.py test --verbosity=2
```

## Requirements Compliance

This system fully implements all specified requirements:

✅ **Genre Filtering**: Three available genres with filtering capability  
✅ **Grouping**: By Author or Year of Publication  
✅ **Alphabetical Sorting**: A-Z and Z-A sorting options  
✅ **Manual Title Search**: Full-text search with partial matching  
✅ **Special Character Handling**: Proper display and processing  
✅ **Multi-value Display**: Semicolon-separated fields shown as key:value pairs  
✅ **Missing ISBN Display**: Clear "missing" indication  
✅ **Variant Title Aggregation**: Single records with multiple title variants  
✅ **Session Management**: In-memory results cleared on exit  
✅ **Search List**: Temporary storage without account creation  
✅ **Advanced Search**: Multi-parameter search capability  
✅ **Reporting**: Top queries, results, and high-frequency comics  

## Contributing

When contributing to this project, please:

1. Follow SOLID principles in all new code
2. Add appropriate tests for new functionality
3. Update documentation for any new features
4. Ensure special character handling is maintained
5. Test with various CSV data formats

## License

[Add your license information here]