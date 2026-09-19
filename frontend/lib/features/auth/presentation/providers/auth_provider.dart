import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/api_client.dart';
import '../../../game/presentation/providers/game_provider.dart';

class AuthState {
  final bool isLoggedIn;
  final String? token;
  final String? userId;
  final String? username;
  final String? email;
  final bool isLoading;
  final String? errorMessage;

  AuthState({
    this.isLoggedIn = false,
    this.token,
    this.userId,
    this.username,
    this.email,
    this.isLoading = false,
    this.errorMessage,
  });

  AuthState copyWith({
    bool? isLoggedIn,
    String? token,
    String? userId,
    String? username,
    String? email,
    bool? isLoading,
    String? errorMessage,
  }) {
    return AuthState(
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      token: token ?? this.token,
      userId: userId ?? this.userId,
      username: username ?? this.username,
      email: email ?? this.email,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _apiClient;

  AuthNotifier(this._apiClient) : super(AuthState());

  Future<bool> login(String emailOrUsername, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final res = await _apiClient.login(emailOrUsername, password);
      final token = res['token'] ?? '';
      final userId = res['user_id'] ?? '';
      final username = res['username'] ?? '';
      final email = res['email'] ?? '';

      _apiClient.setAuthToken(token);

      state = state.copyWith(
        isLoggedIn: true,
        token: token,
        userId: userId,
        username: username,
        email: email,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: "Login failed: Incorrect credentials");
      return false;
    }
  }

  Future<bool> signup(String email, String username, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final res = await _apiClient.signup(email, username, password);
      final token = res['token'] ?? '';
      final userId = res['user_id'] ?? '';

      _apiClient.setAuthToken(token);

      state = state.copyWith(
        isLoggedIn: true,
        token: token,
        userId: userId,
        username: username,
        email: email,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: "Sign Up failed: Email or username already taken");
      return false;
    }
  }

  void logout() {
    _apiClient.setAuthToken(null);
    state = AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final api = ref.watch(apiClientProvider);
  return AuthNotifier(api);
});
