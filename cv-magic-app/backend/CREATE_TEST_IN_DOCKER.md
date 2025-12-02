# Create Test File Inside Docker Container

## Step 1: Open interactive shell in container

```bash
docker exec -it cv_backend bash
```

This will give you a bash shell inside the container.

## Step 2: Navigate to /app directory

```bash
cd /app
```

## Step 3: Create the test file with nano

```bash
nano test_initial_analysis.py
```

## Step 4: Paste the content

Copy the entire content from `backend/test_initial_analysis.py` and paste it into nano.

**To paste in nano:**
- Right-click or use `Shift+Insert` (depending on your terminal)
- Or use the paste command if your terminal supports it

## Step 5: Save and exit

- Press `Ctrl+O` to save (Write Out)
- Press `Enter` to confirm filename
- Press `Ctrl+X` to exit

## Step 6: Run the test

```bash
python test_initial_analysis.py
```

## Alternative: Use cat to create file

If nano doesn't work, you can use `cat` with a heredoc:

```bash
docker exec -it cv_backend bash -c 'cat > /app/test_initial_analysis.py << "EOF"
[paste file content here]
EOF
'
```

## Or: Copy from local file

If you have the file locally, you can still copy it:

```bash
# From your local machine (if you have SSH access to the server)
scp backend/test_initial_analysis.py ubuntu@your-server:/tmp/
# Then on the server:
docker cp /tmp/test_initial_analysis.py cv_backend:/app/test_initial_analysis.py
```

