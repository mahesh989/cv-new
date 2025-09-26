import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_flutter_android/webview_flutter_android.dart';
import 'package:webview_flutter_wkwebview/webview_flutter_wkwebview.dart';

class YouTubePlayerWidget extends StatefulWidget {
  final String videoId;
  final double? aspectRatio;

  const YouTubePlayerWidget({
    super.key,
    required this.videoId,
    this.aspectRatio,
  });

  @override
  State<YouTubePlayerWidget> createState() => _YouTubePlayerWidgetState();
}

class _YouTubePlayerWidgetState extends State<YouTubePlayerWidget> {
  late WebViewController _controller;
  bool _isLoading = true;
  bool _hasError = false;

  @override
  void initState() {
    super.initState();
    _initializeWebView();
  }

  void _initializeWebView() {
    try {
      // Platform-specific WebView creation
      late final PlatformWebViewControllerCreationParams params;
      if (WebViewPlatform.instance is WebKitWebViewPlatform) {
        params = WebKitWebViewControllerCreationParams(
          allowsInlineMediaPlayback: true,
          mediaTypesRequiringUserAction: const <PlaybackMediaTypes>{},
        );
      } else {
        params = const PlatformWebViewControllerCreationParams();
      }

      final WebViewController controller =
          WebViewController.fromPlatformCreationParams(params);

      controller
        ..setJavaScriptMode(JavaScriptMode.unrestricted)
        ..setBackgroundColor(const Color(0x00000000))
        ..setNavigationDelegate(
          NavigationDelegate(
            onProgress: (int progress) {
              print('🎬 WebView loading progress: $progress%');
            },
            onPageStarted: (String url) {
              print('🎬 Page started loading: $url');
              setState(() {
                _isLoading = true;
                _hasError = false;
              });
            },
            onPageFinished: (String url) {
              print('🎬 Page finished loading: $url');
              setState(() {
                _isLoading = false;
              });
            },
            onWebResourceError: (WebResourceError error) {
              print('🎬 WebView error: ${error.description}');
              setState(() {
                _isLoading = false;
                _hasError = true;
              });
            },
            onNavigationRequest: (NavigationRequest request) {
              print('🎬 Navigation request: ${request.url}');
              if (request.url.startsWith('https://www.youtube.com/')) {
                return NavigationDecision.navigate;
              }
              return NavigationDecision.prevent;
            },
          ),
        )
        ..loadRequest(Uri.parse(_getEmbedUrl()));

      // Platform-specific configuration
      if (controller.platform is AndroidWebViewController) {
        AndroidWebViewController.enableDebugging(true);
        (controller.platform as AndroidWebViewController)
            .setMediaPlaybackRequiresUserGesture(false);
      }

      _controller = controller;
    } catch (e) {
      print('🎬 WebView initialization error: $e');
      setState(() {
        _isLoading = false;
        _hasError = true;
      });
    }
  }

  String _getEmbedUrl() {
    // Convert YouTube URL to embed format
    // From: https://www.youtube.com/watch?v=io-5b07geD4
    // To: https://www.youtube.com/embed/io-5b07geD4
    final url =
        'https://www.youtube.com/embed/${widget.videoId}?autoplay=0&loop=1&controls=1&modestbranding=1&rel=0&enablejsapi=1';
    print('🎬 YouTube embed URL: $url'); // Debug log
    return url;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
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
        child: AspectRatio(
          aspectRatio: widget.aspectRatio ?? 16 / 9,
          child: Container(
            color: Colors.black,
            child: _buildContent(),
          ),
        ),
      ),
    );
  }

  Widget _buildContent() {
    if (_hasError) {
      return _buildErrorWidget();
    }

    return Stack(
      children: [
        WebViewWidget(controller: _controller),
        if (_isLoading) _buildLoadingWidget(),
      ],
    );
  }

  Widget _buildLoadingWidget() {
    return Container(
      color: Colors.grey[900],
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 40,
            height: 40,
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              strokeWidth: 3,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Loading tutorial video...',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Getting CV Magic ready for you',
            style: TextStyle(
              color: Colors.white.withOpacity(0.7),
              fontSize: 12,
            ),
          ),
        ],
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
              'Watch our quick tutorial to see CV Magic in action. The video will load shortly!',
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () {
              setState(() {
                _hasError = false;
                _isLoading = true;
              });
              _initializeWebView();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.shade600,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            icon: Icon(Icons.refresh_rounded, size: 18),
            label: Text('Retry'),
          ),
        ],
      ),
    );
  }
}
