import 'package:flutter/foundation.dart';

class HomeController extends ChangeNotifier {
  int _selectedTabIndex = 0;
  bool _shouldClearCVMagicResults = false;

  // Active tab management
  int get selectedTabIndex => _selectedTabIndex;
  bool get shouldClearCVMagicResults => _shouldClearCVMagicResults;

  // Tab indices
  static const int homeTabIndex = 0;
  static const int cvMagicTabIndex = 1;
  static const int jobGenerationTabIndex = 2;
  static const int jobTrackingTabIndex = 3;

  void setTab(int index) {
    if (_selectedTabIndex != index) {
      debugPrint('🔄 [HOME_SCREEN] Tab tapped: $index');

      // If navigating to CVMagic tab, check if we should clear results
      if (index == cvMagicTabIndex) {
        debugPrint('🧹 [HOME_SCREEN] Navigating to CV Magic tab - any clearing will happen in tab');
        notifyListeners();
        return;
      }

      // Special handling for job tracking tab
      if (index == jobTrackingTabIndex) {
        debugPrint('📊 [HOME_SCREEN] Job Tracking tab selected');
      }

      _selectedTabIndex = index;
      notifyListeners();
    }
  }

  void clearCVMagicResults() {
    debugPrint('🧹 [HOME_SCREEN] Clearing CV Magic results');
    _shouldClearCVMagicResults = true;
    notifyListeners();
  }

  void resetCVMagicClearFlag() {
    debugPrint('🔄 [HOME_SCREEN] Resetting CV Magic clear flag');
    _shouldClearCVMagicResults = false;
    notifyListeners();
  }

  bool shouldClearResults() {
    debugPrint('🔄 HomeScreen: shouldClearResults called');
    if (_shouldClearCVMagicResults) {
      debugPrint('🧹 [HOME_SCREEN] Should clear results: true (flag is set)');
      return true;
    }
    debugPrint('🧹 [HOME_SCREEN] Should clear results: false (flag not set)');
    return false;
  }
}