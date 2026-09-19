import 'package:go_router/go_router.dart';
import '../../features/home/presentation/pages/home_page.dart';
import '../../features/game/presentation/pages/game_page.dart';
import '../../features/game/presentation/pages/level_map_page.dart';
import '../../features/game/presentation/pages/category_selection_page.dart';
import '../../features/codex/presentation/pages/codex_page.dart';
import '../../features/multiplayer/presentation/pages/multiplayer_lobby_page.dart';
import '../../features/multiplayer/presentation/pages/multiplayer_game_page.dart';
import '../../features/profile/presentation/pages/profile_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';
import '../../features/auth/presentation/pages/auth_page.dart';

final GoRouter appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
    ),
    GoRoute(
      path: '/auth',
      builder: (context, state) => const AuthPage(),
    ),
    GoRoute(
      path: '/levels',
      builder: (context, state) => const LevelMapPage(),
    ),
    GoRoute(
      path: '/categories',
      builder: (context, state) => const CategorySelectionPage(),
    ),
    GoRoute(
      path: '/codex',
      builder: (context, state) => const CodexPage(),
    ),
    GoRoute(
      path: '/multiplayer',
      builder: (context, state) => const MultiplayerLobbyPage(),
    ),
    GoRoute(
      path: '/multiplayer/game/:code',
      builder: (context, state) {
        final code = state.pathParameters['code'] ?? '';
        final pid = state.uri.queryParameters['pid'] ?? '';
        final name = state.uri.queryParameters['name'] ?? 'Player';
        return MultiplayerGamePage(
          roomCode: code,
          localPlayerId: pid,
          localPlayerName: name,
        );
      },
    ),
    GoRoute(
      path: '/game/:mode',
      builder: (context, state) {
        final mode = state.pathParameters['mode'] ?? 'classic';
        final cat = state.uri.queryParameters['cat'] ?? 'Technology';
        final duration = int.tryParse(state.uri.queryParameters['duration'] ?? '') ?? 60;
        final level = int.tryParse(state.uri.queryParameters['level'] ?? '');
        return GamePage(mode: mode, category: cat, timerDuration: duration, level: level);
      },
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfilePage(),
    ),
    GoRoute(
      path: '/settings',
      builder: (context, state) => const SettingsPage(),
    ),
  ],
);
