import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../game/presentation/providers/game_provider.dart';

final profileFutureProvider = FutureProvider.family<Map<String, dynamic>, String>((ref, userId) async {
  final api = ref.watch(apiClientProvider);
  return api.getProfile(userId);
});

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    if (!authState.isLoggedIn || authState.userId == null) {
      return Scaffold(
        appBar: AppBar(title: Text("PLAYER PROFILE", style: GoogleFonts.dmSerifDisplay())),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.person_outline, size: 56, color: Color(0xFFA9A396)),
                const SizedBox(height: 16),
                Text(
                  "Sign in to view your personal vocabulary record.",
                  textAlign: TextAlign.center,
                  style: GoogleFonts.inter(fontSize: 14, color: const Color(0xFFF1EBDD)),
                ),
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFFF1EBDD),
                    side: const BorderSide(color: Color(0xFFD5A84B)),
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  ),
                  onPressed: () => context.push('/auth'),
                  icon: const Icon(Icons.login_outlined, size: 18),
                  label: Text("LOGIN / SIGN UP", style: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 1.0)),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final profileAsync = ref.watch(profileFutureProvider(authState.userId!));

    return Scaffold(
      appBar: AppBar(
        title: Text("PLAYER RECORD", style: GoogleFonts.dmSerifDisplay()),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout_outlined, size: 20),
            tooltip: "Logout",
            onPressed: () {
              ref.read(authProvider.notifier).logout();
              context.go('/');
            },
          ),
        ],
      ),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFFD5A84B))),
        error: (err, stack) => Center(child: Text("Error loading profile: $err", style: const TextStyle(color: Color(0xFFB95745)))),
        data: (profile) {
          final username = profile['username'] ?? authState.username;
          final email = profile['email'] ?? authState.email;
          final hearts = profile['hearts_remaining'] ?? 5;
          final level = profile['classic_level'] ?? 1;
          final modeStats = Map<String, dynamic>.from(profile['mode_stats'] ?? {});
          final wordLifelines = profile['word_lifelines'] ?? 2;

          return Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 720),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header Container
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF181816),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFF2A2A26)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            username.toUpperCase(),
                            style: GoogleFonts.dmSerifDisplay(fontSize: 24, color: const Color(0xFFF1EBDD)),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            email,
                            style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFFA9A396)),
                          ),
                          const SizedBox(height: 12),
                          const Divider(color: Color(0xFF2A2A26)),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Text(
                                "VOCABULARY EXPLORER",
                                style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.0, color: const Color(0xFFD5A84B)),
                              ),
                              const Spacer(),
                              Text(
                                "CLASSIC LEVEL $level",
                                style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: const Color(0xFFF1EBDD)),
                              ),
                              const SizedBox(width: 12),
                              Row(
                                children: [
                                  const Icon(Icons.flash_on, color: Color(0xFFD5A84B), size: 14),
                                  const SizedBox(width: 2),
                                  Text(
                                    "LIFELINES: $wordLifelines",
                                    style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: const Color(0xFFD5A84B)),
                                  ),
                                ],
                              ),
                              const SizedBox(width: 12),
                              Row(
                                children: [
                                  const Icon(Icons.favorite, color: Color(0xFFB95745), size: 14),
                                  const SizedBox(width: 4),
                                  Text("$hearts/5", style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: const Color(0xFFF1EBDD))),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 28),

                    Text(
                      "PERFORMANCE RECORD",
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 1.5,
                        color: const Color(0xFFA9A396),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Stat Rows for 4 Core Modes
                    _EditorialStatRow("CLASSIC MODE", modeStats['classic']),
                    _EditorialStatRow("TIMED MODE", modeStats['timed']),
                    _EditorialStatRow("DAILY CHALLENGE", modeStats['daily']),
                    _EditorialStatRow("CATEGORY DOMAIN MODE", modeStats['category']),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _EditorialStatRow extends StatelessWidget {
  final String title;
  final Map<String, dynamic>? stats;

  const _EditorialStatRow(this.title, this.stats);

  @override
  Widget build(BuildContext context) {
    final played = stats?['games_played'] ?? 0;
    final won = stats?['games_won'] ?? 0;
    final lost = stats?['games_lost'] ?? 0;
    final winRate = played > 0 ? ((won / played) * 100).toStringAsFixed(0) : "0";

    return Column(
      children: [
        const Divider(color: Color(0xFF2A2A26), height: 1),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 14.0, horizontal: 4.0),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: GoogleFonts.dmSerifDisplay(fontSize: 16, color: const Color(0xFFF1EBDD)),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "$played games played  ·  $won wins  ·  $lost losses",
                      style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFFA9A396)),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    "$winRate%",
                    style: GoogleFonts.dmSerifDisplay(fontSize: 18, color: const Color(0xFFD5A84B)),
                  ),
                  Text(
                    "WIN RATE",
                    style: GoogleFonts.inter(fontSize: 9, fontWeight: FontWeight.bold, color: const Color(0xFFA9A396)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}
