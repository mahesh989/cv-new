# Frontend Logging Setup in Docker

## Overview
Comprehensive frontend request logging has been added to capture all frontend API calls during analysis in the Docker backend container.

## What Gets Logged

### 1. Request Logging (`main.py` middleware)

All frontend requests to analysis endpoints are logged with:
- **Request Method & Path**: `POST /api/preliminary-analysis`
- **User Email**: Extracted from JWT token
- **Client IP**: Request origin IP
- **User-Agent**: Frontend client information
- **Request Body Preview**: First 500 characters of POST/PUT/PATCH requests
- **Request Duration**: Time taken to process request
- **Response Status**: HTTP status code
- **Content-Type**: Response content type

### 2. Analysis Endpoint Logging

#### Preliminary Analysis (`/api/preliminary-analysis`)
- Logs when frontend starts analysis
- Logs authentication status
- Logs analysis completion

#### Analysis Results (`/api/analysis-results/{company}`)
- Logs frontend polling requests
- Logs when ATS data is fetched
- Logs response status

## Log Format

### Request Logs
```
📱 [FRONTEND_REQUEST] POST /api/preliminary-analysis
   User: user@example.com
   IP: 172.18.0.5
   User-Agent: Flutter/3.0.0 (iOS 17.0)
   Request Body Preview: {"cv_filename":"cv.pdf","jd_text":"..."}
```

### Response Logs
```
📱 [FRONTEND_RESPONSE] POST /api/preliminary-analysis - Status: 200 (took 2.345s)
   Content-Type: application/json
```

### Analysis Endpoint Logs
```
📱 [FRONTEND] POST /api/preliminary-analysis - Frontend starting analysis
📱 [FRONTEND] GET /api/analysis-results/Foodbank - Frontend polling for ATS data
```

## How to View Logs in Docker

### View Real-Time Logs
```bash
ssh ubuntu@13.210.217.204 "docker logs cv_backend -f"
```

### Filter Frontend Logs
```bash
ssh ubuntu@13.210.217.204 "docker logs cv_backend -f 2>&1 | grep -E 'FRONTEND|📱'"
```

### Filter Analysis Logs
```bash
ssh ubuntu@13.210.217.204 "docker logs cv_backend -f 2>&1 | grep -E 'FRONTEND.*analysis|preliminary-analysis|analysis-results'"
```

### View Recent Frontend Activity
```bash
ssh ubuntu@13.210.217.204 "docker logs cv_backend --tail 1000 2>&1 | grep '📱'"
```

## Log File Location

Logs are written to:
- **Docker Container**: Standard output (captured by `docker logs`)
- **File Log**: `/app/backend/log.txt` (rotating, max 5MB, 3 backups)

## Analysis Flow Logging

When a user runs analysis, you'll see:

1. **Initial Request**
   ```
   📱 [FRONTEND_REQUEST] POST /api/preliminary-analysis
   📱 [FRONTEND] POST /api/preliminary-analysis - Frontend starting analysis
   ```

2. **Polling Requests** (every few seconds)
   ```
   📱 [FRONTEND_REQUEST] GET /api/analysis-results/Foodbank
   📱 [FRONTEND] GET /api/analysis-results/Foodbank - Frontend polling for ATS data
   📱 [FRONTEND_RESPONSE] GET /api/analysis-results/Foodbank - Status: 200 (took 0.123s)
   ```

3. **Final Response**
   ```
   📱 [FRONTEND_RESPONSE] POST /api/preliminary-analysis - Status: 200 (took 45.678s)
   ```

## Slow Request Detection

Requests taking longer than 5 seconds are automatically logged:
```
⚠️ [SLOW_REQUEST] POST /api/preliminary-analysis took 6.234s
```

## Error Logging

Frontend errors are logged with full context:
```
❌ [FRONTEND_ERROR] POST /api/preliminary-analysis - Error: ... (took 2.345s)
```

## Testing

To verify logging is working:

1. **Run an analysis** from the mobile app
2. **Check Docker logs**:
   ```bash
   ssh ubuntu@13.210.217.204 "docker logs cv_backend --tail 50 | grep '📱'"
   ```
3. **Verify you see**:
   - Frontend request logs
   - User email
   - Request/response details
   - Timing information

## Log Retention

- **Docker logs**: Managed by Docker (default retention)
- **File logs**: Rotating file handler (5MB max, 3 backups)
- **Log level**: Set by `LOG_LEVEL` in settings (default: INFO)

## Troubleshooting

### No Frontend Logs Appearing

1. Check if middleware is active:
   ```bash
   ssh ubuntu@13.210.217.204 "docker logs cv_backend --tail 100 | grep 'FRONTEND'"
   ```

2. Verify log level is INFO or lower:
   - Check `LOG_LEVEL` in backend settings
   - Should be `INFO` or `DEBUG`

3. Check if requests are reaching backend:
   ```bash
   ssh ubuntu@13.210.217.204 "docker logs cv_backend --tail 100 | grep 'POST\|GET'"
   ```

### Logs Too Verbose

To reduce logging, you can:
- Set `LOG_LEVEL` to `WARNING` (will only log warnings/errors)
- Modify middleware to only log specific endpoints

### Missing User Email

If user email shows as "Anonymous":
- Check JWT token is being sent in Authorization header
- Verify token is valid and contains email claim
- Check token verification is working

## Next Steps

1. **Monitor logs during analysis** to track frontend behavior
2. **Use logs to debug** ATS widget rendering issues
3. **Track polling frequency** to optimize frontend polling
4. **Identify slow requests** and optimize backend performance

