import 'package:flutter_test/flutter_test.dart';
import 'package:hangman_reimagined/features/game/presentation/widgets/word_dna_card.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('WordDnaCard displays correct metadata', (WidgetTester tester) async {
    final mockDna = {
      'length': 8,
      'vowels': 3,
      'consonants': 5,
      'has_repeated_letters': true,
      'category': 'Science',
      'part_of_speech': 'adjective'
    };

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: WordDnaCard(dna: mockDna),
        ),
      ),
    );

    expect(find.text('WORD DNA'), findsOneWidget);
    expect(find.text('LENGTH: '), findsOneWidget);
    expect(find.text('8'), findsOneWidget);
    expect(find.text('VOWELS: '), findsOneWidget);
    expect(find.text('3'), findsOneWidget);
  });
}
