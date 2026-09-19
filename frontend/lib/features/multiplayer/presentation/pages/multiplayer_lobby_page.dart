import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../../core/network/api_client.dart';
import '../../../auth/presentation/providers/auth_provider.dart';
import '../../../game/presentation/providers/game_provider.dart';

class MultiplayerLobbyPage extends ConsumerStatefulWidget {
  const MultiplayerLobbyPage({super.key});

  @override
  ConsumerState<MultiplayerLobbyPage> createState() => _MultiplayerLobbyPageState();
}

class _MultiplayerLobbyPageState extends ConsumerState<MultiplayerLobbyPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final _createNameController = TextEditingController();
  final _joinNameController = TextEditingController();
  final _joinCodeController = TextEditingController();

  String _selectedCategory = 'Technology';
  bool _isLoading = false;
  String? _errorMessage;

  final List<String> _categories = [
    'General',
    'Technology',
    'Science',
    'Nature',
    'Animals',
    'Space',
    'Geography',
    'Food & Cooking',
    'Sports',
    'History',
    'Medicine',
    'Arts & Culture',
    'Business',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    final auth = ref.read(authProvider);
    final username = auth.username;
    final defaultName = (username != null && username.isNotEmpty) ? username : "Player1";
    _createNameController.text = defaultName;
    _joinNameController.text = (username != null && username.isNotEmpty) ? username : "Player2";
  }

  @override
  void dispose() {
    _tabController.dispose();
    _createNameController.dispose();
    _joinNameController.dispose();
    _joinCodeController.dispose();
    super.dispose();
  }

  void _createRoom() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final auth = ref.read(authProvider);
      final api = ref.read(apiClientProvider);
      final name = _createNameController.text.trim().isEmpty ? "Player 1" : _createNameController.text.trim();

      final res = await api.createRoom(
        playerName: name,
        userId: auth.userId,
        category: _selectedCategory,
      );

      final code = res['room_code'];
      final p1Id = res['player1_id'];

      if (mounted) {
        context.push('/multiplayer/game/$code?pid=$p1Id&name=${Uri.encodeComponent(name)}');
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Failed to create room: $e";
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _joinRoom() async {
    final code = _joinCodeController.text.trim().toUpperCase();
    if (code.isEmpty || code.length < 4) {
      setState(() {
        _errorMessage = "Please enter a valid room code";
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final auth = ref.read(authProvider);
      final api = ref.read(apiClientProvider);
      final name = _joinNameController.text.trim().isEmpty ? "Player 2" : _joinNameController.text.trim();

      final res = await api.joinRoom(
        roomCode: code,
        playerName: name,
        userId: auth.userId,
      );

      final p2Id = res['player2_id'];

      if (mounted) {
        context.push('/multiplayer/game/$code?pid=$p2Id&name=${Uri.encodeComponent(name)}');
      }
    } catch (e) {
      setState(() {
        _errorMessage = "Failed to join room: Invalid or full room code.";
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("1v1 ROOM DUEL", style: GoogleFonts.dmSerifDisplay()),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: const Color(0xFFD5A84B),
          labelColor: const Color(0xFFF1EBDD),
          unselectedLabelColor: const Color(0xFFA9A396),
          labelStyle: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 1.0),
          tabs: const [
            Tab(text: "CREATE ROOM"),
            Tab(text: "JOIN ROOM"),
          ],
        ),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 520),
          child: TabBarView(
            controller: _tabController,
            children: [
              // Create Room Tab
              SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Host a 1v1 Room Duel",
                      style: GoogleFonts.dmSerifDisplay(fontSize: 24, color: const Color(0xFFF1EBDD)),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Generate a 6-character room code to invite a friend to a shared turn-based Hangman duel.",
                      style: GoogleFonts.inter(color: const Color(0xFFA9A396), fontSize: 13, height: 1.4),
                    ),
                    const SizedBox(height: 24),
                    TextField(
                      controller: _createNameController,
                      decoration: const InputDecoration(
                        labelText: "Your Nickname",
                        prefixIcon: Icon(Icons.person_outline, color: Color(0xFFA9A396)),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      value: _selectedCategory,
                      decoration: const InputDecoration(
                        labelText: "Vocabulary Category",
                        prefixIcon: Icon(Icons.category_outlined, color: Color(0xFFA9A396)),
                        border: OutlineInputBorder(),
                      ),
                      dropdownColor: const Color(0xFF181816),
                      items: _categories.map((cat) {
                        return DropdownMenuItem(
                          value: cat,
                          child: Text(cat, style: GoogleFonts.inter(color: const Color(0xFFF1EBDD))),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedCategory = val);
                      },
                    ),
                    if (_errorMessage != null) ...[
                      const SizedBox(height: 12),
                      Text(_errorMessage!, style: GoogleFonts.inter(color: const Color(0xFFB95745), fontSize: 13)),
                    ],
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 46,
                      child: OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFFF1EBDD),
                          side: const BorderSide(color: Color(0xFFD5A84B)),
                        ),
                        onPressed: _isLoading ? null : _createRoom,
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Color(0xFFD5A84B))
                            : Text("CREATE ROOM & GET CODE →", style: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 1.0)),
                      ),
                    ),
                  ],
                ),
              ),

              // Join Room Tab
              SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Enter Room Code",
                      style: GoogleFonts.dmSerifDisplay(fontSize: 24, color: const Color(0xFFF1EBDD)),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      "Join an active room duel hosted by your friend using their 6-character room code.",
                      style: GoogleFonts.inter(color: const Color(0xFFA9A396), fontSize: 13, height: 1.4),
                    ),
                    const SizedBox(height: 24),
                    TextField(
                      controller: _joinNameController,
                      decoration: const InputDecoration(
                        labelText: "Your Nickname",
                        prefixIcon: Icon(Icons.person_outline, color: Color(0xFFA9A396)),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _joinCodeController,
                      textCapitalization: TextCapitalization.characters,
                      decoration: const InputDecoration(
                        labelText: "6-Character Room Code (e.g. HANG88)",
                        prefixIcon: Icon(Icons.numbers, color: Color(0xFFA9A396)),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    if (_errorMessage != null) ...[
                      const SizedBox(height: 12),
                      Text(_errorMessage!, style: GoogleFonts.inter(color: const Color(0xFFB95745), fontSize: 13)),
                    ],
                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 46,
                      child: OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFFF1EBDD),
                          side: const BorderSide(color: Color(0xFFD5A84B)),
                        ),
                        onPressed: _isLoading ? null : _joinRoom,
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Color(0xFFD5A84B))
                            : Text("ENTER ROOM DUEL →", style: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 1.0)),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
