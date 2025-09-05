// ats_saved_service.dart
class SavedATSApplication {
  final String originalCV;
  final String tailoredCV;
  final String jdText;
  final int atsScore; // we will pass ATS Score too later

  SavedATSApplication({
    required this.originalCV,
    required this.tailoredCV,
    required this.jdText,
    required this.atsScore,
  });
}

class SavedATSService {
  static final List<SavedATSApplication> savedApplications = [];

  static void saveApplication(SavedATSApplication application) {
    savedApplications.add(application);
  }

  static List<SavedATSApplication> getSavedApplications() {
    return savedApplications;
  }
}
