import 'dart:html' as html;
import 'dart:ui_web' as ui;
import 'package:flutter/material.dart';

class YouTubePlayerWeb extends StatefulWidget {
  final String videoId;
  final double? aspectRatio;

  const YouTubePlayerWeb({
    super.key,
    required this.videoId,
    this.aspectRatio,
  });

  @override
  State<YouTubePlayerWeb> createState() => _YouTubePlayerWebState();
}

class _YouTubePlayerWebState extends State<YouTubePlayerWeb> {
  final _iframeElementId = 'youtube_player_iframe';
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _initializePlayer();
  }

  void _initializePlayer() {
    // Register the iframe element view
    ui.platformViewRegistry.registerViewFactory(
      _iframeElementId,
      (int viewId) {
        final element = html.IFrameElement()
          ..src =
              'https://www.youtube.com/embed/${widget.videoId}?enablejsapi=1&origin=${Uri.encodeComponent(html.window.location.origin)}'
          ..style.border = 'none'
          ..style.pointerEvents = 'auto'
          ..style.zIndex = '1'
          ..allow =
              'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture'
          ..allowFullscreen = true;

        // Prevent iframe from capturing events that should go to Flutter
        element.onClick.listen((event) {
          // Allow the iframe to handle its own clicks but prevent event bubbling
          event.stopPropagation();
        });

        return element;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        // Use 90% of available width or 1024px, whichever is smaller
        final width = constraints.maxWidth * 0.9;
        final height = width * (widget.aspectRatio ?? 9 / 16);

        return Center(
          child: Container(
            width: width,
            height: height * 2,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Container(
                color: Colors.black,
                height: height,
                child: Center(
                  child: AspectRatio(
                    aspectRatio: widget.aspectRatio ?? 16 / 9,
                    child: _buildContent(),
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildContent() {
    if (_hasError) {
      return _buildErrorWidget();
    }

    return Container(
      // Ensure the container doesn't interfere with Flutter's event handling
      child: AbsorbPointer(
        absorbing: false, // Allow clicks on the video itself
        child: GestureDetector(
          onTap: () {
            // Prevent iframe from interfering with Flutter gestures
            print(
                '🎬 YouTube player container tapped - preventing event conflicts');
          },
          child: HtmlElementView(
            viewType: _iframeElementId,
          ),
        ),
      ),
    );
  }

  Widget _buildErrorWidget() {
    return Container(
      color: Colors.grey[900],
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.play_circle_outline,
            color: Colors.white.withOpacity(0.7),
            size: 48,
          ),
          const SizedBox(height: 16),
          Text(
            'Tutorial Video',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: Text(
              'This video cannot be embedded. Please watch it directly on YouTube.',
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.shade600,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            icon: Icon(Icons.launch_rounded, size: 18),
            label: Text('Watch on YouTube'),
            onPressed: () {
              html.window.open(
                  'https://www.youtube.com/watch?v=${widget.videoId}',
                  '_blank');
            },
          ),
        ],
      ),
    );
  }
}
