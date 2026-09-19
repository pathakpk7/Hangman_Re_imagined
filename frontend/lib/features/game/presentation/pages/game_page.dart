import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/game_provider.dart';
import '../widgets/hangman_canvas.dart';
import '../widgets/word_dna_card.dart';
import '../widgets/keyboard_widget.dart';
import '../widgets/witty_loss_dialog.dart';
import '../widgets/lifeline_modal.dart';
import '../../../dictionary/presentation/widgets/knowledge_card.dart';
import '../../../auth/presentation/providers/auth_provider.dart';

class GamePage extends ConsumerStatefulWidget {
  final String mode;
  final String category;
  final int timerDuration;
  final int? level;

  const GamePage({
    super.key,
    this.mode = 'classic',
    this.category = 'Technology',
    this.timerDuration = 60,
    this.level,
  });

  @override
  ConsumerState<GamePage> createState() => _GamePageState();
}

class _GamePageState extends ConsumerState<GamePage> {
  bool _wittyPopupShown = false;
  Timer? _timedModeTimer;
  late int _secondsRemaining;
  int? _expandedClueStep = 1;

  @override
  void initState() {
    super.initState();
    _secondsRemaining = widget.timerDuration;
    Future.microtask(() {
      final auth = ref.read(authProvider);
      final game = ref.read(gameProvider);
      final targetLevel = widget.level ?? (widget.mode == 'classic' ? (game.level > 0 ? game.level : 1) : 1);

      if (game.gameId.isEmpty || game.mode != widget.mode || (widget.mode == 'classic' && game.level != targetLevel)) {
        ref.read(gameProvider.notifier).startNewGame(
              mode: widget.mode,
              level: targetLevel,
              category: widget.category,
              userId: auth.userId,
            );
      }

      if (widget.mode == 'timed') {
        _startTimer();
      }
    });
  }

  void _startTimer() {
    _timedModeTimer?.cancel();
    setState(() {
      _secondsRemaining = widget.timerDuration;
    });

    _timedModeTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) return;
      final gameState = ref.read(gameProvider);
      if (gameState.status != 'in_progress') {
        timer.cancel();
        return;
      }

      if (_secondsRemaining <= 1) {
        timer.cancel();
        setState(() {
          _secondsRemaining = 0;
        });
        ref.read(gameProvider.notifier).markTimedOut();
      } else {
        setState(() {
          _secondsRemaining--;
        });
      }
    });
  }

  @override
  void dispose() {
    _timedModeTimer?.cancel();
    super.dispose();
  }

  void _checkWittyPopup(GameState state) {
    if (state.wittyLossPopup != null && !_wittyPopupShown) {
      _wittyPopupShown = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        showDialog(
          context: context,
          builder: (ctx) => WittyLossDialog(
            title: state.wittyLossPopup!['title'] ?? 'Defeat Streak',
            message: state.wittyLossPopup!['message'] ?? '',
            consecutiveLosses: state.wittyLossPopup!['consecutive_losses'] ?? 5,
            vocabularySuggestion: state.wittyLossPopup!['vocabulary_suggestion'] ?? '',
            onRetry: () {
              final auth = ref.read(authProvider);
              ref.read(gameProvider.notifier).startNewGame(
                    mode: widget.mode,
                    level: state.level,
                    category: widget.category,
                    userId: auth.userId,
                  );
              if (widget.mode == 'timed') _startTimer();
            },
          ),
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final gameState = ref.watch(gameProvider);
    final authState = ref.watch(authProvider);

    _checkWittyPopup(gameState);

    String titleText = "MODE: ${widget.mode.toUpperCase()}";
    if (widget.mode == 'classic') {
      titleText = "LEVEL ${gameState.level} / 100 — ${gameState.tierLabel.toUpperCase()}";
    } else if (widget.mode == 'category') {
      titleText = "CATEGORY: ${widget.category.toUpperCase()}";
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(titleText, style: GoogleFonts.dmSerifDisplay(fontSize: 16)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Row(
              children: List.generate(
                5,
                (index) => Padding(
                  padding: const EdgeInsets.only(left: 2.0),
                  child: Icon(
                    index < gameState.livesRemaining ? Icons.favorite : Icons.favorite_border,
                    color: index < gameState.livesRemaining ? const Color(0xFFB95745) : const Color(0xFF4A4A44),
                    size: 18,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
      body: gameState.isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFD5A84B)))
          : Center(
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
                              // Timed Mode Clock Bar
                              if (widget.mode == 'timed')
                                Container(
                                  width: double.infinity,
                                  color: const Color(0xFF181816),
                                  padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                                  child: Column(
                                    children: [
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Row(
                                            children: [
                                              const Icon(Icons.timer, size: 16, color: Color(0xFFD5A84B)),
                                              const SizedBox(width: 6),
                                              Text(
                                                "TIME REMAINING: ${_secondsRemaining}s",
                                                style: GoogleFonts.inter(
                                                  fontSize: 12,
                                                  fontWeight: FontWeight.bold,
                                                  color: _secondsRemaining <= 10 ? const Color(0xFFB95745) : const Color(0xFFD5A84B),
                                                ),
                                              ),
                                            ],
                                          ),
                                          Text(
                                            "TICKING CLOCK",
                                            style: GoogleFonts.inter(fontSize: 10, letterSpacing: 1.0, color: const Color(0xFFA9A396)),
                                          ),
                                        ],
                                      ),
                                      const SizedBox(height: 6),
                                      LinearProgressIndicator(
                                        value: widget.timerDuration > 0 ? (_secondsRemaining / widget.timerDuration.toDouble()) : 0.0,
                                        backgroundColor: const Color(0xFF2A2A26),
                                        color: _secondsRemaining <= 10 ? const Color(0xFFB95745) : const Color(0xFFD5A84B),
                                        minHeight: 3,
                                      ),
                                    ],
                                  ),
                                ),

                              // Status Bar (Score, Combo, Word Lifeline)
                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 6.0),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      "SCORE: ${gameState.score}",
                                      style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold, color: const Color(0xFFF1EBDD)),
                                    ),
                                    if (gameState.combo > 1)
                                      Text(
                                        "${gameState.combo}x COMBO",
                                        style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold, color: const Color(0xFFD5A84B)),
                                      ).animate().scale(),
                                    
                                    // Word Lifeline Trigger Button
                                    InkWell(
                                      onTap: gameState.status == 'in_progress' ? () {
                                        showDialog(
                                          context: context,
                                          builder: (ctx) => LifelineModal(
                                            level: gameState.level,
                                            inventory: gameState.wordLifelines,
                                            onSelectOption: (option) {
                                              ref.read(gameProvider.notifier).useLifeline(option);
                                            },
                                          ),
                                        );
                                      } : null,
                                      borderRadius: BorderRadius.circular(4),
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: const Color(0xFF181816),
                                          borderRadius: BorderRadius.circular(4),
                                          border: Border.all(
                                            color: gameState.lifelineUnlocked
                                                ? const Color(0xFFD5A84B)
                                                : const Color(0xFF4A4A44),
                                          ),
                                        ),
                                        child: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            Icon(
                                              gameState.lifelineUnlocked ? Icons.flash_on : Icons.lock_outline,
                                              size: 14,
                                              color: gameState.lifelineUnlocked ? const Color(0xFFD5A84B) : const Color(0xFFA9A396),
                                            ),
                                            const SizedBox(width: 4),
                                            Text(
                                              gameState.lifelineUnlocked
                                                  ? "LIFELINE (${gameState.wordLifelines})"
                                                  : "LIFELINE (LVL 5)",
                                              style: GoogleFonts.inter(
                                                fontSize: 10,
                                                fontWeight: FontWeight.bold,
                                                color: gameState.lifelineUnlocked ? const Color(0xFFD5A84B) : const Color(0xFFA9A396),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              // Hangman Canvas
                              Padding(
                                padding: const EdgeInsets.symmetric(vertical: 4.0),
                                child: HangmanCanvas(livesRemaining: gameState.livesRemaining, maxLives: 5),
                              ),

                              // Word DNA Card
                              WordDnaCard(dna: gameState.wordDna),

                              // 3 Progressive Clues Section
                              Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 6.0),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      "PROGRESSIVE DEDUCTION CLUES",
                                      style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2, color: const Color(0xFFA9A396)),
                                    ),
                                    const SizedBox(height: 6),

                                    // Clue 1: Profile & Synonyms
                                    _ClueTile(
                                      stepNumber: 1,
                                      label: "Clue 1 — Word Profile, Origin & Synonyms",
                                      content: gameState.clue1Definition,
                                      icon: Icons.auto_awesome_outlined,
                                      isExpanded: _expandedClueStep == 1,
                                      onUnlock: () {
                                        setState(() {
                                          _expandedClueStep = 1;
                                        });
                                        ref.read(gameProvider.notifier).requestHint(1);
                                      },
                                      onToggleExpand: () {
                                        setState(() {
                                          _expandedClueStep = _expandedClueStep == 1 ? null : 1;
                                        });
                                      },
                                    ),
                                    const SizedBox(height: 6),

                                    // Clue 2: Domain Usage Context
                                    _ClueTile(
                                      stepNumber: 2,
                                      label: "Clue 2 — Where & How It Is Used",
                                      content: gameState.clue2Sentence,
                                      icon: Icons.travel_explore_outlined,
                                      isExpanded: _expandedClueStep == 2,
                                      onUnlock: () {
                                        setState(() {
                                          _expandedClueStep = 2;
                                        });
                                        ref.read(gameProvider.notifier).requestHint(2);
                                      },
                                      onToggleExpand: () {
                                        setState(() {
                                          _expandedClueStep = _expandedClueStep == 2 ? null : 2;
                                        });
                                      },
                                    ),
                                    const SizedBox(height: 6),

                                    // Clue 3: Natural Example Sentence
                                    _ClueTile(
                                      stepNumber: 3,
                                      label: "Clue 3 — Natural Example Sentence",
                                      content: gameState.clue3Context,
                                      icon: Icons.short_text,
                                      isExpanded: _expandedClueStep == 3,
                                      onUnlock: () {
                                        setState(() {
                                          _expandedClueStep = 3;
                                        });
                                        ref.read(gameProvider.notifier).requestHint(3);
                                      },
                                      onToggleExpand: () {
                                        setState(() {
                                          _expandedClueStep = _expandedClueStep == 3 ? null : 3;
                                        });
                                      },
                                    ),
                                  ],
                                ),
                              ),

                              // Striking Clue Card (if Option B activated)
                              if (gameState.strikingClue != null && gameState.strikingClue!.isNotEmpty)
                                Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
                                  child: Container(
                                    width: double.infinity,
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF1F1E1A),
                                      borderRadius: BorderRadius.circular(6),
                                      border: Border.all(color: const Color(0xFFD5A84B), width: 1.2),
                                    ),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Icon(Icons.auto_awesome_outlined, size: 16, color: Color(0xFFD5A84B)),
                                        const SizedBox(width: 8),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                "STRIKING CLUE (LIFELINE OPTION B)",
                                                style: GoogleFonts.inter(
                                                  fontSize: 10,
                                                  fontWeight: FontWeight.bold,
                                                  letterSpacing: 1.0,
                                                  color: const Color(0xFFD5A84B),
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(
                                                gameState.strikingClue!,
                                                style: GoogleFonts.inter(
                                                  fontSize: 12,
                                                  color: const Color(0xFFF1EBDD),
                                                  height: 1.3,
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ).animate().fadeIn().slideY(begin: 0.1, end: 0.0),
                                ),

                              // Masked Word Display
                              Padding(
                                padding: const EdgeInsets.symmetric(vertical: 12.0, horizontal: 8.0),
                                child: Wrap(
                                  spacing: 6,
                                  alignment: WrapAlignment.center,
                                  children: gameState.maskedWord.map((char) {
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
                                    ).animate(target: isRevealed ? 1 : 0).fade().scale();
                                  }).toList(),
                                ),
                              ),

                              const Spacer(),

                              // Keyboard or Knowledge Card / End Game Status
                              if (gameState.status == 'in_progress') ...[
                                KeyboardWidget(
                                  guessedLetters: gameState.guessedLetters,
                                  maskedWord: gameState.maskedWord,
                                  onKeyPress: (char) {
                                    ref.read(gameProvider.notifier).makeGuess(char);
                                  },
                                ),
                              ] else if (gameState.knowledgeCard != null) ...[
                                KnowledgeCard(
                                  cardData: gameState.knowledgeCard!,
                                  onNextGame: () {
                                    _wittyPopupShown = false;
                                    ref.read(gameProvider.notifier).startNewGame(
                                          mode: widget.mode,
                                          level: gameState.status == 'won' && widget.mode == 'classic' ? gameState.level + 1 : gameState.level,
                                          category: widget.category,
                                          userId: authState.userId,
                                        );
                                    if (widget.mode == 'timed') _startTimer();
                                  },
                                ),
                              ] else ...[
                                Padding(
                                  padding: const EdgeInsets.all(16.0),
                                  child: Column(
                                    children: [
                                      Text(
                                        gameState.status == 'won' ? "VICTORY" : "DEFEAT",
                                        style: GoogleFonts.dmSerifDisplay(
                                          fontSize: 28,
                                          color: gameState.status == 'won' ? const Color(0xFF879873) : const Color(0xFFB95745),
                                        ),
                                      ),
                                      const SizedBox(height: 10),
                                      OutlinedButton(
                                        style: OutlinedButton.styleFrom(
                                          foregroundColor: const Color(0xFFF1EBDD),
                                          side: const BorderSide(color: Color(0xFFD5A84B)),
                                        ),
                                        onPressed: () {
                                          _wittyPopupShown = false;
                                          ref.read(gameProvider.notifier).startNewGame(
                                                mode: widget.mode,
                                                level: gameState.level,
                                                category: widget.category,
                                                userId: authState.userId,
                                              );
                                          if (widget.mode == 'timed') _startTimer();
                                        },
                                        child: const Text("CONTINUE →"),
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

class _ClueTile extends StatelessWidget {
  final int stepNumber;
  final String label;
  final String? content;
  final IconData icon;
  final bool isExpanded;
  final VoidCallback onUnlock;
  final VoidCallback onToggleExpand;

  const _ClueTile({
    required this.stepNumber,
    required this.label,
    required this.content,
    required this.icon,
    required this.isExpanded,
    required this.onUnlock,
    required this.onToggleExpand,
  });

  @override
  Widget build(BuildContext context) {
    final isUnlocked = content != null && content!.isNotEmpty;

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF181816),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: isUnlocked
              ? (isExpanded ? const Color(0xFFD5A84B) : const Color(0xFFD5A84B).withValues(alpha: 0.4))
              : const Color(0xFF2A2A26),
        ),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(6),
        onTap: isUnlocked ? onToggleExpand : onUnlock,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 10.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    icon,
                    size: 18,
                    color: isUnlocked ? const Color(0xFFD5A84B) : const Color(0xFFA9A396),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      label,
                      style: GoogleFonts.inter(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: isUnlocked ? const Color(0xFFD5A84B) : const Color(0xFFA9A396),
                      ),
                    ),
                  ),
                  if (!isUnlocked)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF2A2A26),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        "UNLOCK CLUE",
                        style: GoogleFonts.inter(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFFF1EBDD),
                        ),
                      ),
                    )
                  else
                    Icon(
                      isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                      size: 18,
                      color: const Color(0xFFD5A84B),
                    ),
                ],
              ),
              if (isUnlocked && isExpanded) ...[
                const SizedBox(height: 8),
                Padding(
                  padding: const EdgeInsets.only(left: 28.0),
                  child: Text(
                    content!,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      color: const Color(0xFFF1EBDD),
                      height: 1.3,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
