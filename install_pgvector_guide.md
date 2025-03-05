# Installing pgvector on PostgreSQL 16 (Windows)

## Recommended Solution: Docker (Easiest Approach)

Since building pgvector on Windows is complex and no pre-built binaries are readily available, using Docker is the simplest solution:

1. **Install Docker Desktop for Windows**:
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer if prompted

2. **Run a PostgreSQL container with pgvector**:
   ```powershell
   docker run -d --name postgres-pgvector -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg16
   ```

3. **Move your data to the Docker container**:
   
   Option A: Create a new database and import your data:
   ```powershell
   # Create the database
   docker exec postgres-pgvector psql -U postgres -c "CREATE DATABASE ifs_assistant;"
   
   # Then use pg_dump to export your current data and import it to the Docker container
   pg_dump -U postgres -h localhost -d ifs_assistant > backup.sql
   docker exec -i postgres-pgvector psql -U postgres -d ifs_assistant < backup.sql
   ```
   
   Option B: Update your application to point to the Docker container without migrating data:
   - Update your `.env` file with the new connection string:
     ```
     DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ifs_assistant
     ```
   - Run your application's database migration scripts to set up tables in the new database

4. **Verify pgvector is installed in the container**:
   ```powershell
   docker exec postgres-pgvector psql -U postgres -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
   ```

## Alternative Option: Build from Source (Complex)

If you prefer to install pgvector directly on your Windows PostgreSQL server:

### Prerequisites for Building
- Git installed
- Visual Studio (Community edition is free) with C++ development tools
- PostgreSQL 16 development files
- CMake (if not included in Visual Studio)

### Steps to Build:

1. Clone the repository:
   ```
   git clone https://github.com/pgvector/pgvector.git
   cd pgvector
   ```

2. Open the Developer Command Prompt for Visual Studio (not regular Command Prompt):
   - Click Start → Programs → Visual Studio 2022 → Visual Studio Tools → Developer Command Prompt for VS 2022

3. In the Developer Command Prompt, navigate to the pgvector directory and run:
   ```
   SET PG_HOME=C:\Program Files\PostgreSQL\16
   SET PATH=%PG_HOME%\bin;%PATH%
   SET PGROOT=%PG_HOME%
   nmake /f Makefile.win
   nmake /f Makefile.win install
   ```

## Setting Up After Installation

After installing pgvector (using either method), enable the extension in your database:

1. Connect to your database:
   ```sql
   -- If using local PostgreSQL
   CREATE EXTENSION IF NOT EXISTS vector;
   
   -- If using Docker container
   -- Extension is already installed, just create it in your database
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. Run the vector index setup script:
   ```
   python setup_vector_indexes.py
   ```

## Troubleshooting

- **Docker container issues**: 
  - Verify Docker is running with `docker ps`
  - Check container logs with `docker logs postgres-pgvector`
  
- **Build errors**: 
  - Make sure you're using the Developer Command Prompt
  - Verify PostgreSQL development files are installed
  - Check that Visual Studio with C++ tools is properly installed

- **Connection issues**:
  - Verify your connection string in `.env` is pointing to the correct host
  - Make sure the PostgreSQL server is running and accessible 