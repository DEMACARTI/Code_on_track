// Simple User model for inspection-only app
class User {
  final String username;
  final String email;

  // In production, never store or transfer plain passwords in the model.
  User({required this.username, required this.email});
}

// Authentication will be provided by an external AuthService implementation
// (e.g. REST-backed). See `lib/services/auth_service.dart`.
