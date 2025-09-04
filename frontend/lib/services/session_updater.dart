import '../state/session_state.dart';

class SessionUpdater {
  static void updateOriginalCV(String filename) {
    SessionState.originalCVFilename = filename;
    // Don't save to disk - keep only in memory for current session
  }

  static void updateJobDescription(String text, {String? url}) {
    SessionState.jdText = text;
    if (url != null) {
      SessionState.jdUrl = url;
      SessionState.lastJobUrl = url;
    }
    // Don't save to disk - keep only in memory for current session
  }

  static void updateCurrentPrompt(String prompt) {
    SessionState.currentPrompt = prompt;
    // Save prompts to disk as they should persist
    SessionState.saveToDisk();
  }

  static void updateTailoredCV(String filename) {
    SessionState.tailoredCVFilename = filename;
    // Don't save to disk - keep only in memory for current session
  }

  static void updateMatchResult(String result) {
    SessionState.matchResult = result;
    // Don't save to disk - keep only in memory for current session
  }

  static void updateKeywords(List<String> keywords) {
    SessionState.keywords = keywords;
    // Don't save to disk - keep only in memory for current session
  }

  static void updateKeyPhrases(List<String> keyPhrases) {
    SessionState.keyPhrases = keyPhrases;
    // Don't save to disk - keep only in memory for current session
  }
}
