# Backend Tests

This directory contains comprehensive tests for the Django REST API backend of the Chemical Equipment Parameter Visualizer.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_auth.py             # Authentication API tests
├── test_upload.py           # CSV upload API tests
├── test_datasets.py         # Dataset retrieval API tests
├── test_pdf.py              # PDF generation API tests
├── test_models.py           # Model tests
├── test_serializers.py      # Serializer tests
├── test_utils.py            # Utility function tests
├── test_integration.py     # Integration tests
└── README.md                # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Running All Tests

```bash
# Run all tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run tests with HTML coverage report
pytest --cov=equipment --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test class
pytest tests/test_auth.py::TestAuthenticationAPI

# Run specific test method
pytest tests/test_auth.py::TestAuthenticationAPI::test_login_success
```

### Test Configuration

The test suite uses the following configuration:

- **Database**: Uses Django's test database (automatically created/destroyed)
- **Authentication**: Token-based authentication
- **Fixtures**: Reusable test data and clients
- **Coverage**: HTML and terminal coverage reports

## Test Coverage

### Authentication Tests (`test_auth.py`)
- ✅ Login success with valid credentials
- ✅ Login failure with invalid credentials
- ✅ Login with missing fields
- ✅ Token creation and validation
- ✅ Unauthenticated access protection
- ✅ Invalid token handling

### CSV Upload Tests (`test_upload.py`)
- ✅ Successful CSV upload
- ✅ File validation (type, format, size)
- ✅ Missing file handling
- ✅ Invalid CSV format detection
- ✅ Large file handling
- ✅ Special character handling
- ✅ Duplicate dataset naming

### Dataset Tests (`test_datasets.py`)
- ✅ Dataset list retrieval
- ✅ Dataset detail retrieval
- ✅ Pagination functionality
- ✅ Search and ordering
- ✅ Empty dataset handling
- ✅ Statistics accuracy
- ✅ Preview row formatting

### PDF Generation Tests (`test_pdf.py`)
- ✅ PDF download success
- ✅ PDF content validation
- ✅ Large dataset PDF generation
- ✅ Special character handling
- ✅ Filename formatting
- ✅ Response headers
- ✅ Multiple request consistency

### Model Tests (`test_models.py`)
- ✅ Dataset creation and validation
- ✅ String representation
- ✅ Ordering behavior
- ✅ JSON field handling
- ✅ CSV content storage
- ✅ Bulk operations

### Serializer Tests (`test_serializers.py`)
- ✅ List serializer behavior
- ✅ Detail serializer behavior
- ✅ Field validation
- ✅ Data type validation
- ✅ Create and update operations
- ✅ Readonly field protection

### Utility Tests (`test_utils.py`)
- ✅ CSV processing functions
- ✅ Statistics calculation
- ✅ CSV format validation
- ✅ Error handling
- ✅ Large dataset processing
- ✅ Precision handling

### Integration Tests (`test_integration.py`)
- ✅ Complete workflow testing
- ✅ Multi-user isolation
- ✅ Concurrent uploads
- ✅ Large dataset workflows
- ✅ Error handling workflows
- ✅ Data consistency validation

## Test Fixtures

The test suite provides reusable fixtures in `conftest.py`:

- `api_client`: Unauthenticated API client
- `user`: Test user instance
- `auth_client`: Authenticated API client
- `sample_csv_content`: Sample CSV data as string
- `sample_csv_file`: Temporary CSV file
- `equipment_dataset`: Test dataset instance
- `multiple_datasets`: Multiple test datasets

## Test Data

Sample CSV data used in tests:
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Pump,150.5,2.5,85.2
Valve-A12,Valve,75.3,1.8,45.7
Reactor-R1,Reactor,200.8,3.2,120.5
Column-C3,Column,180.2,2.8,95.3
Pump-002,Pump,165.7,2.7,88.9
```

## Best Practices

### Test Organization
- Group related tests in separate test classes
- Use descriptive test method names
- Follow arrange-act-assert pattern
- Use fixtures for reusable test data

### Test Data Management
- Use factory pattern for complex test data
- Clean up temporary files and resources
- Use transactions for database isolation
- Mock external dependencies when needed

### Coverage Goals
- Aim for >90% code coverage
- Focus on critical API endpoints
- Test both success and error scenarios
- Include edge cases and boundary conditions

### Performance Considerations
- Use `--reuse-db` flag for faster test runs
- Limit expensive operations in tests
- Use appropriate test data sizes
- Profile slow tests regularly

## Troubleshooting

### Common Issues

1. **Database Errors**
   - Ensure test database is properly configured
   - Run migrations: `python manage.py migrate`
   - Check `pytest.ini` Django settings

2. **Import Errors**
   - Verify Python path includes project root
   - Check `PYTHONPATH` environment variable
   - Ensure virtual environment is activated

3. **Fixture Issues**
   - Check fixture dependencies
   - Verify fixture scope (session vs function)
   - Ensure proper cleanup in fixtures

4. **Coverage Issues**
   - Install coverage dependencies
   - Check `.coveragerc` configuration
   - Verify source path settings

### Debugging Tests

```bash
# Run with debugging
pytest --pdb

# Stop on first failure
pytest -x

# Run specific test with debugging
pytest tests/test_auth.py::TestAuthenticationAPI::test_login_success --pdb
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=equipment --cov-report=xml
```

## Contributing

When adding new features:

1. Write tests before or alongside implementation
2. Ensure all tests pass before submitting PR
3. Maintain or improve test coverage
4. Add integration tests for new workflows
5. Update this README if adding new test files

## Test Metrics

Current test coverage and statistics can be viewed in the HTML coverage report generated at `htmlcov/index.html` after running:

```bash
pytest --cov=equipment --cov-report=html
```
