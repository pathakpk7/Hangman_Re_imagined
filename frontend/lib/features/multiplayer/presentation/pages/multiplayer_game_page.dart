import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../game/presentation/providers/game_provider.dart';
import '../../../game/presentation/widgets/hangman_canvas.dart';
import '../../../game/presentation/widgets/keyboard_widget.dart';

class MultiplayerGamePage extends ConsumerStatefulWidget {
  final String roomCode;
  final String localPlayerId;
  final String localPlayerName;

  const MultiplayerGamePage({
    super.key,
    required this.roomCode,
    required this.localPlayerId,
    required this.localPlayerName,
  });

  @override
  ConsumerState<MultiplayerGamePage> createState() => _MultiplayerGamePageState();
}

class _MultiplayerGamePageState extends ConsumerState<MultiplayerGamePage> {
  Timer? _pollTimer;
  Map<String, dynamic>? _roomState;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _fetchRoomState();
    // Poll room state every 1 second
    _pollTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      _fetchRoomState();
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _fetchRoomState() async {
    try {
      final api = ref.read(apiClientProvider);
      final res = await api.getRoomState(widget.roomCode);
      if (mounted) {
        setState(() {
          _roomState = res;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted && _roomState == null) {
        setState(() {
          _errorMessage = "Failed to load room state: $e";
          _isLoading = false;
        });
      }
    }
  }

  void _onKeyPress(String letter) async {
    if (_roomState == null) return;
    final currentTurnId = _roomState!['current_turn_player_id'];
    final status = _roomState!['status'];

    if (status != 'in_progress' || currentTurnId != widget.localPlayerId) return;

    try {
      final api = ref.read(apiClientProvider);
      final res = await api.makeRoomGuess(
        roomCode: widget.roomCode,
        playerId: widget.localPlayerId,
        letter: letter,
      );
      if (mounted) {
        setState(() {
          _roomState = res;
        });
      }
    } catch (e) {
      // Ignored or handle error
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text("ROOM DUEL: ${widget.roomCode}", style: GoogleFonts.dmSerifDisplay())),
        body: const Center(child: CircularProgressIndicator(color: Color(0xFFD5A84B))),
      );
    }

    if (_errorMessage != null || _roomState == null) {
      return Scaffold(
        appBar: AppBar(title: Text("ROOM DUEL ERROR", style: GoogleFonts.dmSerifDisplay())),
        body: Center(
          child: Text(_errorMessage ?? "Room not found", style: const TextStyle(color: Color(0xFFB95745))),
        ),
      );
    }

    final p1Name = _roomState!['player1_name'] ?? 'Player 1';
    final p1Score = _roomState!['player1_score'] ?? 0;
    final p2Name = _roomState!['player2_name'] ?? 'Waiting...';
    final p2Score = _roomState!['player2_score'] ?? 0;
    final currentTurnId = _roomState!['current_turn_player_id'];
    final currentTurnName = _roomState!['current_turn_player_name'] ?? 'Player';
    final status = _roomState!['status'];
    final livesRemaining = _roomState!['lives_remaining'] ?? 5;
    final maskedWord = List<String>.from(_roomState!['masked_word'] ?? []);
    final guessedLetters = List<String>.from(_roomState!['guessed_letters'] ?? []);
    final isMyTurn = currentTurnId == widget.localPlayerId;
    final winnerName = _roomState!['winner_name'];

    return Scaffold(
      appBar: AppBar(
        title: Text("1v1 DUEL — ROOM: ${widget.roomCode}", style: GoogleFonts.dmSerifDisplay(fontSize: 16)),
        actions: [
          IconButton(
            icon: const Icon(Icons.copy_outlined, size: 18),
            tooltip: "Copy Room Code",
            onPressed: () {
              Clipboard.setData(ClipboardData(text: widget.roomCode));
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text("Room Code ${widget.roomCode} copied to clipboard!")),
              );
            },
          ),
        ],
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: LayoutBuilder(
            builder: (context, constraints) {
              return SingleChildScrollView(
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: constraints.maxHeight),
                  child: IntrinsicHeight(
                    child: Column(
                      children: [
                        // Dual Player Scoreboard
                        Container(
                          width: double.infinity,
                          color: const Color(0xFF181816),
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 10.0),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              // Player 1
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Text(
                                        p1Name.toUpperCase(),
                                        style: GoogleFonts.inter(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                          color: _roomState!['player1_id'] == currentTurnId ? const Color(0xFFD5A84B) : const Color(0xFFF1EBDD),
                                        ),
                                      ),
                                      if (_roomState!['player1_id'] == widget.localPlayerId)
                                        Text(" (YOU)", style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFFA9A396))),
                                    ],
                                  ),
                                  Text(
                                    "$p1Score PTS",
                                    style: GoogleFonts.dmSerifDisplay(fontSize: 16, color: const Color(0xFFD5A84B)),
                                  ),
                                ],
                              ),

                              // VS Badge
                              Text(
                                "VS",
                                style: GoogleFonts.dmSerifDisplay(fontSize: 18, fontStyle: FontStyle.italic, color: const Color(0xFFA9A396)),
                              ),

                              // Player 2
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Row(
                                    children: [
                                      if (_roomState!['player2_id'] == widget.localPlayerId)
                                        Text("(YOU) ", style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFFA9A396))),
                                      Text(
                                        p2Name.toUpperCase(),
                                        style: GoogleFonts.inter(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                          color: _roomState!['player2_id'] == currentTurnId ? const Color(0xFFD5A84B) : const Color(0xFFF1EBDD),
                                        ),
                                      ),
                                    ],
                                  ),
                                  Text(
                                    "$p2Score PTS",
                                    style: GoogleFonts.dmSerifDisplay(fontSize: 16, color: const Color(0xFFD5A84B)),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),

                        // Turn State Banner
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.symmetric(vertical: 8.0),
                          decoration: BoxDecoration(
                            color: status == 'waiting_for_player2'
                                ? const Color(0xFF2A2A26)
                                : (isMyTurn ? const Color(0xFFD5A84B).withOpacity(0.2) : const Color(0xFF181816)),
                            border: Border(
                              bottom: BorderSide(
                                color: isMyTurn ? const Color(0xFFD5A84B) : const Color(0xFF2A2A26),
                                width: isMyTurn ? 1.5 : 1,
                              ),
                            ),
                          ),
                          child: Center(
                            child: status == 'waiting_for_player2'
                                ? Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFFD5A84B))),
                                      const SizedBox(width: 10),
                                      Text(
                                        "WAITING FOR PLAYER 2 (SHARE CODE: ${widget.roomCode})",
                                        style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: const Color(0xFFF1EBDD)),
                                      ),
                                    ],
                                  )
                                : Text(
                                    isMyTurn ? "YOUR TURN — CHOOSE A LETTER" : "OPPONENT'S TURN ($currentTurnName)...",
                                    style: GoogleFonts.inter(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      letterSpacing: 1.0,
                                      color: isMyTurn ? const Color(0xFFD5A84B) : const Color(0xFFA9A396),
                                    ),
                                  ),
                          ),
                        ),

                        // Hangman Canvas & Lives
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 8.0),
                          child: HangmanCanvas(livesRemaining: livesRemaining, maxLives: 5),
                        ),

                        // Masked Word Display
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 8.0),
                          child: Wrap(
                            spacing: 6,
                            alignment: WrapAlignment.center,
                            children: maskedWord.map((char) {
                              final isRevealed = char != '_';
                              return Container(
                                width: 32,
                                height: 42,
                                alignment: Alignment.center,
                                decoration: BoxDecoration(
                                  color: isRevealed ? const Color(0xFFD5A84B).withOpacity(0.15) : const Color(0xFF181816),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(
                                    color: isRevealed ? const Color(0xFFD5A84B) : const Color(0xFF2A2A26),
                                    width: 1.5,
                                  ),
                                ),
                                child: Text(
                                  char.toUpperCase(),
                                  style: GoogleFonts.dmSerifDisplay(
                                    fontSize: 22,
                                    color: isRevealed ? const Color(0xFFF1EBDD) : Colors.transparent,
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        ),

                        const Spacer(),

                        // Keyboard or Winner Banner
                        if (status == 'in_progress') ...[
                          Opacity(
                            opacity: isMyTurn ? 1.0 : 0.4,
                            child: AbsorbPointer(
                              absorbing: !isMyTurn,
                              child: KeyboardWidget(
                                guessedLetters: guessedLetters,
                                maskedWord: maskedWord,
                                onKeyPress: _onKeyPress,
                              ),
                            ),
                          ),
                        ] else if (status == 'won') ...[
                          Padding(
                            padding: const EdgeInsets.all(20.0),
                            child: Column(
                              children: [
                                Text(
                                  "${winnerName?.toUpperCase() ?? 'PLAYER'} WINS THE DUEL!",
                                  textAlign: TextAlign.center,
                                  style: GoogleFonts.dmSerifDisplay(fontSize: 24, color: const Color(0xFFD5A84B)),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  "Final Scores: $p1Name ($p1Score pts)  ·  $p2Name ($p2Score pts)",
                                  style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFFF1EBDD)),
                                ),
                                const SizedBox(height: 16),
                                OutlinedButton(
                                  style: OutlinedButton.styleFrom(
                                    foregroundColor: const Color(0xFFF1EBDD),
                                    side: const BorderSide(color: Color(0xFFD5A84B)),
                                  ),
                                  onPressed: () => Navigator.of(context).pop(),
                                  child: const Text("RETURN TO LOBBY →"),
                                ),
                              ],
                            ),
                          ),
                        ] else if (status == 'lost') ...[
                          Padding(
                            padding: const EdgeInsets.all(20.0),
                            child: Column(
                              children: [
                                Text(
                                  "BOTH PLAYERS DEFEATED",
                                  style: GoogleFonts.dmSerifDisplay(fontSize: 24, color: const Color(0xFFB95745)),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  "Shared hearts reached 0.",
                                  style: GoogleFonts.inter(fontSize: 12, color: const Color(0xFFA9A396)),
                                ),
                                const SizedBox(height: 16),
                                OutlinedButton(
                                  style: OutlinedButton.styleFrom(
                                    foregroundColor: const Color(0xFFF1EBDD),
                                    side: const BorderSide(color: Color(0xFFD5A84B)),
                                  ),
                                  onPressed: () => Navigator.of(context).pop(),
                                  child: const Text("RETURN TO LOBBY →"),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
