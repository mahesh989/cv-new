// Web-specific helper for disabling iframe interactions
import 'dart:html' as html;

class WebHelper {
  static void disableIframeInteractions() {
    try {
      final document = html.document;
      
      // Only disable iframes and videos, not all elements
      final elements = document.querySelectorAll('iframe, video, embed, object');
      for (final element in elements) {
        element.style.pointerEvents = 'none';
        element.style.zIndex = '-1';
      }
      
      // Don't add overlay - let Flutter handle the barrier
      print('✅ Disabled iframe interactions for web');
    } catch (e) {
      print('❌ Error disabling iframe interactions: $e');
    }
  }

  static void enableIframeInteractions() {
    try {
      final document = html.document;
      
      // Re-enable all iframes and videos
      final elements = document.querySelectorAll('iframe, video, embed, object');
      for (final element in elements) {
        element.style.pointerEvents = 'auto';
        element.style.zIndex = 'auto';
      }
      
      print('✅ Enabled iframe interactions for web');
    } catch (e) {
      print('❌ Error enabling iframe interactions: $e');
    }
  }
}

