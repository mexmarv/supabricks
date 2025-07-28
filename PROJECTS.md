# Supabricks Project Roadmap

This document outlines the development roadmap and project tasks for Supabricks, a Supabase-style API layer for Databricks Unity Catalog.

## Current Version: v3.2

### Features Implemented

- ✅ RESTful API for Delta Tables
- ✅ PAT Authentication
- ✅ Dynamic Table Discovery (60-second polling)
- ✅ CRUD Operations with Delta
- ✅ Table Management (Create/Drop tables)
- ✅ System Catalog Filtering (Performance improvement)
- ✅ OpenAPI Documentation
- ✅ ClearTunnel Integration

## Project Boards

### Upcoming Features (v3.3)

- [ ] **Enhanced Filtering**
  - [ ] Support for complex filtering operations (AND, OR, NOT)
  - [ ] Range filters (>, <, >=, <=)
  - [ ] LIKE/ILIKE pattern matching
  - [ ] IN operator for multiple value matching
  - [ ] JSON path filtering for nested structures

- [ ] **Pagination and Result Management**
  - [ ] Implement offset/limit pagination
  - [ ] Add cursor-based pagination for large datasets
  - [ ] Support for sorting results (ASC/DESC)
  - [ ] Result count metadata

- [ ] **Performance Optimizations**
  - [ ] Authentication caching
  - [ ] Query optimization for large tables
  - [ ] Connection pooling
  - [ ] Async query execution

### Infrastructure Improvements

- [ ] **Testing and Quality**
  - [ ] Unit test suite with pytest
  - [x] API testing script for all endpoints
  - [ ] Integration tests with real Databricks instances
  - [ ] Performance benchmarking tools
  - [ ] CI/CD pipeline setup

- [ ] **Documentation**
  - [x] Comprehensive API reference
  - [x] Deployment guides for various environments
  - [ ] Troubleshooting guide
  - [ ] Video tutorials

- [ ] **Security Enhancements**
  - [ ] Row-level security implementation
  - [ ] Column-level access controls
  - [ ] Audit logging
  - [ ] Rate limiting

## Long-term Roadmap (v4.0+)

### Advanced Features

- [x] **Schema Management**
  - [x] Table creation API
  - [x] Table dropping API
  - [ ] Schema migration tools
  - [ ] Data validation rules

- [ ] **Real-time Capabilities**
  - [ ] WebSocket support for live updates
  - [ ] Change data capture integration
  - [ ] Event triggers

- [ ] **Integration Ecosystem**
  - [ ] Client libraries (Python, JavaScript, etc.)
  - [ ] Integration with popular frameworks
  - [ ] Plugin system for extensibility

### Enterprise Features

- [ ] **Multi-tenant Support**
  - [ ] Tenant isolation
  - [ ] Custom authentication providers
  - [ ] Resource quotas and limits

- [ ] **Advanced Analytics**
  - [ ] Aggregation endpoints
  - [ ] Materialized views
  - [ ] Scheduled queries

- [ ] **Governance and Compliance**
  - [ ] GDPR compliance tools
  - [ ] Data lineage tracking
  - [ ] Access policy management

## Getting Involved

### How to Contribute

1. **Pick a Task**: Choose an unassigned task from the project boards
2. **Create a Branch**: Fork the repository and create a branch for your work
3. **Implement**: Make your changes following the project's coding standards
4. **Test**: Ensure all tests pass and add new tests for your feature
5. **Submit PR**: Create a pull request with a clear description of your changes

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/supabricks.git
cd supabricks

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Databricks credentials
cat > .env << EOL
DATABRICKS_HOST=https://your-databricks-instance.cloud.databricks.com/
DATABRICKS_TOKEN=your-personal-access-token
ENABLE_CLEARTUNNEL=true
DATABRICKS_WAREHOUSE_ID=your-sql-warehouse-id
EOL

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Testing the API

You can test all API endpoints using curl commands or by creating a shell script. Here's a basic testing approach:

1. **Create a test script**:
   ```bash
   # Create a test script
   touch test_api.sh
   chmod +x test_api.sh
   ```

2. **Add test cases for all endpoints**:
   - Test API connection
   - List all tables
   - Create a test table
   - Insert test data
   - Query the data
   - Update the data
   - Delete the data
   - Drop the test table

3. **Run the tests and measure performance**:
   ```bash
   ./test_api.sh
   ```

### Communication Channels

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Pull Requests**: Submit code contributions via Pull Requests

## Release Schedule

- **v3.2**: Q2 2023 - Table management and system catalog filtering
- **v3.3**: Q3 2023 - Enhanced filtering and pagination
- **v3.4**: Q4 2023 - Performance optimizations and testing infrastructure
- **v4.0**: Q2 2024 - Schema management and real-time capabilities

## Project Maintainers

- [Your Name](https://github.com/yourusername) - Lead Developer

## License

This project is licensed under the MIT License - see the LICENSE file for details.