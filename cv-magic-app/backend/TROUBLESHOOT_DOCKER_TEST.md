# Troubleshooting: Running Test in Docker

## Step 1: Check if containers are running

```bash
cd ~/cv-new/cv-magic-app
docker compose ps
```

You should see containers listed. If nothing shows, start them:

```bash
docker compose up -d
```

Wait a few seconds, then check again:

```bash
docker compose ps
```

## Step 2: Check container names

List all running containers:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Look for a container with "backend" in the name (might be `cv_backend` or something else).

## Step 3: Copy the test file

**Option A: Use docker compose (service name)**

```bash
cd ~/cv-new/cv-magic-app
docker compose cp backend/test_initial_analysis.py backend:/app/test_initial_analysis.py
```

**Option B: Use docker directly (container name)**

```bash
cd ~/cv-new/cv-magic-app
docker cp backend/test_initial_analysis.py cv_backend:/app/test_initial_analysis.py
```

## Step 4: Run the test

**Option A: Use docker compose (service name)**

```bash
docker compose exec backend python /app/test_initial_analysis.py
```

**Option B: Use docker directly (container name)**

```bash
docker exec cv_backend python /app/test_initial_analysis.py
```

## Alternative: Run without copying (if file is already in backend folder)

The backend folder is mounted, so if the file exists in `backend/test_initial_analysis.py`, you might be able to run it directly:

```bash
docker compose exec backend python test_initial_analysis.py
```

But this depends on volume mounts. Check what's mounted:

```bash
docker inspect cv_backend | grep -A 10 Mounts
```

## Quick One-Liner (if containers are running)

```bash
cd ~/cv-new/cv-magic-app && \
docker compose cp backend/test_initial_analysis.py backend:/app/ && \
docker compose exec backend python /app/test_initial_analysis.py
```

## If containers are not running

```bash
cd ~/cv-new/cv-magic-app
docker compose up -d
```

Wait 10-15 seconds for services to start, then try again.

## Check backend logs if something fails

```bash
docker compose logs backend --tail=50
```

