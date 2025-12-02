# Quick Guide: Run Test Inside Docker

## Step 1: Make sure Docker containers are running

```bash
cd cv-magic-app
docker compose ps
```

You should see containers like:
- `cv_backend` (backend)
- `cv_nginx` (nginx)
- `cv_postgres` (database)
- `cv_redis` (redis)

If not running, start them:
```bash
docker compose up -d
```

## Step 2: Copy test script into container (if needed)

The test script should already be in the backend folder, but if you need to copy it:

```bash
docker compose cp backend/test_initial_analysis.py cv_backend:/app/test_initial_analysis.py
```

## Step 3: Run the test inside the container

```bash
docker compose exec backend python test_initial_analysis.py
```

This will:
- Run inside the `cv_backend` container
- Access the API at `http://localhost:8000` (internal to container)
- Test the 3-section JD skills extraction
- Show results in the terminal

## Alternative: Run with explicit path

If the script isn't found:

```bash
docker compose exec backend python /app/test_initial_analysis.py
```

## What to expect

You should see output like:

```
🚀 Starting test...
   Backend URL: http://localhost:8000
   
================================================================================
🧪 Testing Initial Analysis API - 3-Section JD Skills Extraction
================================================================================
🌐 Backend URL: http://localhost:8000
📧 User: shivani@gmail.com
🔗 JD URL: https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst
🏢 Company: Australia_for_UNHCR

🔐 Step 1: Authenticating...
✅ Authentication successful

🚀 Step 2: Calling /initial-analysis endpoint...
📡 Response Status: 200

📊 Step 3: Analyzing Response
✅ jd_three_section_skills field found in response!

🔧 Technical Skills (X):
   - SQL
   - Power BI
   ...
```

## Troubleshooting

### "Container not found"
```bash
# Check if containers are running
docker compose ps

# Start containers if needed
docker compose up -d
```

### "Script not found"
```bash
# Copy script into container
docker compose cp backend/test_initial_analysis.py cv_backend:/app/

# Then run
docker compose exec backend python /app/test_initial_analysis.py
```

### "Permission denied"
```bash
# Make sure script is executable (if needed)
docker compose exec backend chmod +x /app/test_initial_analysis.py
```

### "Cannot connect to backend"
- Check backend logs: `docker compose logs backend`
- Verify backend is healthy: `docker compose exec backend curl http://localhost:8000/health`

