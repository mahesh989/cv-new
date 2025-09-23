/// Exception thrown when a tailored CV is not found during rerun analysis
class TailoredCVNotFoundException implements Exception {
  final String message;

  TailoredCVNotFoundException(this.message);

  @override
  String toString() => message;
}