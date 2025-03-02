# Website Visit Counter Assignment

This project implements a scalable Website Visit Counter system as part of an assignment. It tracks page visits using Flask, Redis, application-layer caching, write batching, and sharding, all within a single file (`main.py`).

## Overview
The system includes:
- **Basic Visit Counter**: Tracks page visits (initially in-memory, evolved to Redis).
- **Redis Integration**: Persists visit counts using Redis.
- **Application Caching**: Uses a 5-second TTL in-memory cache to reduce Redis queries.
- **Write Batching**: Buffers writes and flushes to Redis every 30 seconds.
- **Sharding**: Distributes data across two Redis instances (ports 7070 and 7071) using consistent hashing.

## Requirements
- Python 3.x
- Flask (`pip install flask`)
- Redis Python client (`pip install redis`)
- Redis server (running on ports 7070 and 7071)

## Setup Instructions
1. **Install Python Dependencies**:
   - Ensure Python 3.x is installed.
   - Install required libraries:
     ```bash
     pip install flask redis
     ```

2. **Start Redis Instances**:
   - Run two Redis servers for sharding:
     ```bash
     redis-server --port 7070 &  # Shard 1
     redis-server --port 7071 &  # Shard 2
     ```

3. **Run the Application**:
   - Save the code in `main.py`.
   - Start the Flask app:
     ```bash
     python main.py
     ```
   - The API will be available at `http://localhost:5000`.

## API Endpoints
- **POST /visits/{page_id}**: Increments the visit count for a given page ID.
  - Example: `curl -X POST http://localhost:5000/visits/page1`
  - Response: `{"message": "Visit to page1 recorded"}`
- **GET /visits/{page_id}**: Retrieves the total visit count for a page ID.
  - Example: `curl http://localhost:5000/visits/page1`
  - Possible Responses:
    - Cache hit: `{"visits": 1, "served_via": "in_memory"}` (within 5 seconds)
    - Redis hit: `{"visits": 1, "served_via": "redis_7070"}` or `{"visits": 1, "served_via": "redis_7071"}`

## Testing
- **Task 1**: Verify initial in-memory counting (commented logic in `main.py`).
- **Task 2**: Ensure counts persist after restarting `main.py` (via Redis).
- **Task 3**: Test cache by sending multiple GET requests within 5 seconds (should return `"served_via": "in_memory"`).
- **Task 4**: Send POST requests and wait 30 seconds to confirm batch flushing to Redis.
- **Task 5**: Use different `page_id` values (e.g., `page1`, `page2`) to see sharding across `redis_7070` and `redis_7071`.

## Notes
- All functionality is implemented in `main.py` for simplicity.
- The application uses two Redis instances (ports 7070 and 7071) for sharding.
- Ensure Redis servers are running before starting the app.

## Submission
To push to GitHub:
```bash
git add main.py README.md
git commit -m "Completed visit counter assignment"
git push origin main





---

### How to Use
1. **Save the README**:
   - Create a file named `README.md` in your `visit_counter_assignment` directory.
   - Copy and paste the content above into it.

2. **Verify Setup**:
   - Follow the instructions in the README to install dependencies, start Redis, and run `main.py`.
   - Test the endpoints as described to ensure all tasks are working.

3. **Push to GitHub**:
   - Add both files to your repository:
     ```bash
     git add main.py README.md
     git commit -m "Completed visit counter assignment with README"
     git push origin main
     ```

