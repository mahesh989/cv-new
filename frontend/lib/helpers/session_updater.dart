import '../state/session_state.dart';

class SessionUpdater {
  static void updateOriginalCV(String filename) {
    SessionState.originalCVFilename = filename;
    SessionState.saveToDisk(); // Save to disk immediately
  }

  static void updateJD(String jdText) {
    SessionState.jdText = jdText;
    SessionState.saveToDisk(); // Save to disk immediately
  }

  static void updatePrompt(String prompt) {
    SessionState.currentPrompt = prompt;
    SessionState.saveToDisk(); // Save to disk immediately
  }

  static void updateTailoredCV(String filename) {
    SessionState.tailoredCVFilename = filename;
    SessionState.saveToDisk(); // Save to disk immediately
  }
}
