# Video Assets

This directory contains video assets for the CV Magic application.

## Files

- `info.mp4` - Tutorial/introduction video shown in the mobile app's intro screen

## Video Requirements

- **Format**: MP4
- **Recommended Resolution**: 1920x1080 (Full HD)
- **Aspect Ratio**: 16:9
- **Recommended Duration**: 2-5 minutes
- **File Size**: Under 50MB for optimal mobile performance

## Usage

The intro video is served by the backend and displayed in the mobile app's first tab (Tutorial/Intro screen). The video player widget includes:

- Auto-play controls
- Progress bar
- Play/pause functionality
- Loading states
- Error handling with graceful fallbacks

## API Endpoint

The video is accessible via:
```
GET /video/info.mp4
```

## Notes

- Ensure the backend server is configured to serve static files from this directory
- The video player includes fallback content if the video fails to load
- Mobile-optimized with responsive sizing and no overflow issues
