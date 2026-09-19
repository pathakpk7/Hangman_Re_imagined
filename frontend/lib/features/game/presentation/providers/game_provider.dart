import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/api_client.dart';

final apiClientProvider = Provider((ref) => ApiClient());

class GameState {
  final String gameId;
  final String mode;
  final int level;
  final String tierLabel;
  final List<String> maskedWord;
  final int livesRemaining; // 5 hearts max
  final int score;
  final int combo;
  final int mistakes;
  final String status; // in_progress, won, lost
  final Map<String, dynamic> wordDna;
  final List<String> guessedLetters;
  final String? hintClue;
  final String? clue1Definition;
  final String? clue2Sentence;
  final String? clue3Context;
  final String? strikingClue;
  final bool lifelineUnlocked;
  final int wordLifelines;
  final bool lifelineUsed;
  final bool lifelineUnlockedMoment;
  final int hintStep;
  final Map<String, dynamic>? knowledgeCard;
  final Map<String, dynamic>? wittyLossPopup;
  final bool isLoading;
  final String? errorMessage;
  final int heartRegenSecondsLeft;

  GameState({
    required this.gameId,
    required this.mode,
    required this.level,
    required this.tierLabel,
    required this.maskedWord,
    required this.livesRemaining,
    required this.score,
    required this.combo,
    required this.mistakes,
    required this.status,
    required this.wordDna,
    required this.guessedLetters,
    this.hintClue,
    this.clue1Definition,
    this.clue2Sentence,
    this.clue3Context,
    this.strikingClue,
    this.lifelineUnlocked = false,
    this.wordLifelines = 2,
    this.lifelineUsed = false,
    this.lifelineUnlockedMoment = false,
    this.hintStep = 0,
    this.knowledgeCard,
    this.wittyLossPopup,
    this.isLoading = false,
    this.errorMessage,
    this.heartRegenSecondsLeft = 0,
  });

  GameState copyWith({
    String? gameId,
    String? mode,
    int? level,
    String? tierLabel,
    List<String>? maskedWord,
    int? livesRemaining,
    int? score,
    int? combo,
    int? mistakes,
    String? status,
    Map<String, dynamic>? wordDna,
    List<String>? guessedLetters,
    String? hintClue,
    String? clue1Definition,
    String? clue2Sentence,
    String? clue3Context,
    String? strikingClue,
    bool? lifelineUnlocked,
    int? wordLifelines,
    bool? lifelineUsed,
    bool? lifelineUnlockedMoment,
    int? hintStep,
    Map<String, dynamic>? knowledgeCard,
    Map<String, dynamic>? wittyLossPopup,
    bool? isLoading,
    String? errorMessage,
    int? heartRegenSecondsLeft,
  }) {
    return GameState(
      gameId: gameId ?? this.gameId,
      mode: mode ?? this.mode,
      level: level ?? this.level,
      tierLabel: tierLabel ?? this.tierLabel,
      maskedWord: maskedWord ?? this.maskedWord,
      livesRemaining: livesRemaining ?? this.livesRemaining,
      score: score ?? this.score,
      combo: combo ?? this.combo,
      mistakes: mistakes ?? this.mistakes,
      status: status ?? this.status,
      wordDna: wordDna ?? this.wordDna,
      guessedLetters: guessedLetters ?? this.guessedLetters,
      hintClue: hintClue ?? this.hintClue,
      clue1Definition: clue1Definition ?? this.clue1Definition,
      clue2Sentence: clue2Sentence ?? this.clue2Sentence,
      clue3Context: clue3Context ?? this.clue3Context,
      strikingClue: strikingClue ?? this.strikingClue,
      lifelineUnlocked: lifelineUnlocked ?? this.lifelineUnlocked,
      wordLifelines: wordLifelines ?? this.wordLifelines,
      lifelineUsed: lifelineUsed ?? this.lifelineUsed,
      lifelineUnlockedMoment: lifelineUnlockedMoment ?? this.lifelineUnlockedMoment,
      hintStep: hintStep ?? this.hintStep,
      knowledgeCard: knowledgeCard ?? this.knowledgeCard,
      wittyLossPopup: wittyLossPopup ?? this.wittyLossPopup,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
      heartRegenSecondsLeft: heartRegenSecondsLeft ?? this.heartRegenSecondsLeft,
    );
  }
}

class GameNotifier extends StateNotifier<GameState> {
  final ApiClient _apiClient;

  GameNotifier(this._apiClient)
      : super(GameState(
          gameId: '',
          mode: 'classic',
          level: 1,
          tierLabel: 'Very Easy',
          maskedWord: [],
          livesRemaining: 5,
          score: 0,
          combo: 0,
          mistakes: 0,
          status: 'in_progress',
          wordDna: {},
          guessedLetters: [],
        ));

  Future<void> startNewGame({String mode = 'classic', int level = 1, String category = 'General', String? userId}) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final res = await _apiClient.startGame(mode: mode, level: level, category: category, userId: userId);
      state = GameState(
        gameId: res['game_id'] ?? 'g_1',
        mode: res['mode'] ?? mode,
        level: res['level'] ?? level,
        tierLabel: res['tier_label'] ?? 'Very Easy',
        maskedWord: List<String>.from(res['masked_word'] ?? []),
        livesRemaining: res['lives_remaining'] ?? 5,
        score: res['score'] ?? 0,
        combo: res['combo'] ?? 0,
        mistakes: res['mistakes'] ?? 0,
        status: res['status'] ?? 'in_progress',
        wordDna: res['word_dna'] ?? {},
        guessedLetters: List<String>.from(res['guessed_letters'] ?? []),
        hintClue: res['hint_clue'],
        clue1Definition: res['clue1_definition'],
        clue2Sentence: res['clue2_sentence'],
        clue3Context: res['clue3_context'],
        strikingClue: res['striking_clue'],
        lifelineUnlocked: res['lifeline_unlocked'] ?? ((res['level'] ?? level) >= 5),
        wordLifelines: res['word_lifelines'] ?? 2,
        lifelineUsed: res['lifeline_used'] ?? false,
        lifelineUnlockedMoment: res['lifeline_unlocked_moment'] ?? false,
        hintStep: 0,
        knowledgeCard: res['knowledge_card'],
        wittyLossPopup: res['witty_loss_popup'],
        heartRegenSecondsLeft: res['heart_regen_seconds_left'] ?? 0,
      );
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMessage: "Failed to start game: $e");
    }
  }

  Future<void> useLifeline(String option, {String? userId}) async {
    if (state.lifelineUsed || state.status != 'in_progress') return;
    try {
      final res = await _apiClient.useLifeline(gameId: state.gameId, option: option, userId: userId);
      final gState = res['game_state'] ?? {};
      state = state.copyWith(
        maskedWord: List<String>.from(gState['masked_word'] ?? state.maskedWord),
        strikingClue: res['striking_clue'] ?? gState['striking_clue'] ?? state.strikingClue,
        wordLifelines: res['word_lifelines_remaining'] ?? gState['word_lifelines'] ?? state.wordLifelines,
        lifelineUsed: true,
        status: gState['status'] ?? state.status,
      );
    } catch (e) {
      state = state.copyWith(errorMessage: "Failed to activate Word Lifeline: $e");
    }
  }

  Future<void> makeGuess(String letter) async {
    if (state.status != 'in_progress' || state.guessedLetters.contains(letter)) return;

    final updatedGuessed = [...state.guessedLetters, letter];
    state = state.copyWith(guessedLetters: updatedGuessed);

    try {
      final res = await _apiClient.makeGuess(state.gameId, letter);
      state = state.copyWith(
        maskedWord: List<String>.from(res['masked_word'] ?? state.maskedWord),
        livesRemaining: res['lives_remaining'] ?? state.livesRemaining,
        score: res['score'] ?? state.score,
        combo: res['combo'] ?? state.combo,
        mistakes: res['mistakes'] ?? state.mistakes,
        status: res['status'] ?? state.status,
        knowledgeCard: res['knowledge_card'],
        wittyLossPopup: res['witty_loss_popup'],
      );
    } catch (e) {
      _handleLocalGuess(letter);
    }
  }

  Future<void> requestHint([int? step]) async {
    final targetStep = step ?? ((state.hintStep < 3) ? state.hintStep + 1 : 3);
    try {
      final res = await _apiClient.requestHint(state.gameId, hintStep: targetStep);
      final clue = res['clue_text'] ?? "Clue revealed.";
      final gState = res['game_state'] ?? {};

      state = state.copyWith(
        hintClue: clue,
        clue1Definition: gState['clue1_definition'] ?? res['clue1_definition'] ?? state.clue1Definition,
        clue2Sentence: gState['clue2_sentence'] ?? res['clue2_sentence'] ?? state.clue2Sentence,
        clue3Context: gState['clue3_context'] ?? res['clue3_context'] ?? state.clue3Context,
        hintStep: targetStep,
        maskedWord: List<String>.from(gState['masked_word'] ?? state.maskedWord),
        status: gState['status'] ?? state.status,
      );
    } catch (e) {
      state = state.copyWith(
        hintClue: "Clue: A word related to ${state.wordDna['category'] ?? 'General'}",
        hintStep: targetStep,
      );
    }
  }

  void markTimedOut() {
    state = state.copyWith(status: 'lost', livesRemaining: 0);
  }

  void _handleLocalGuess(String letter) {
    int updatedLives = state.livesRemaining;
    int updatedScore = state.score;
    int updatedCombo = state.combo;
    int updatedMistakes = state.mistakes;
    String updatedStatus = state.status;

    updatedLives -= 1;
    if (updatedLives <= 0) updatedStatus = 'lost';

    state = state.copyWith(
      livesRemaining: updatedLives,
      score: updatedScore,
      combo: updatedCombo,
      mistakes: updatedMistakes,
      status: updatedStatus,
    );
  }
}

final gameProvider = StateNotifierProvider<GameNotifier, GameState>((ref) {
  final api = ref.watch(apiClientProvider);
  return GameNotifier(api);
});
