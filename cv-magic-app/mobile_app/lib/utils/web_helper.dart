// Web-specific helper for disabling iframe interactions
import 'dart:html' as html;

class WebHelper {
  static void disableIframeInteractions() {
    try {
      final document = html.document;
      
      // Disable all iframes and videos
      final elements = document.querySelectorAll('iframe, video, embed, object');
      for (final element in elements) {
        element.style.pointerEvents = 'none';
        element.style.zIndex = '-1';
      }
      
      // Add overlay to prevent clicks
      final overlay = html.DivElement()
        ..id = 'flt-dialog-overlay'
        ..style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 999998; background: transparent; pointer-events: auto;';
      document.body?.append(overlay);
      
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
      
      // Remove overlay
      final overlay = document.getElementById('flt-dialog-overlay');
      overlay?.remove();
      
      print('✅ Enabled iframe interactions for web');
    } catch (e) {
      print('❌ Error enabling iframe interactions: $e');
    }
  }
}

