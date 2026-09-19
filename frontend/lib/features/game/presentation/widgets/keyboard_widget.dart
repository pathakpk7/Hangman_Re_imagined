import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class KeyboardWidget extends StatelessWidget {
  final List<String> guessedLetters;
  final List<String> maskedWord;
  final Function(String) onKeyPress;

  const KeyboardWidget({
    super.key,
    required this.guessedLetters,
    required this.maskedWord,
    required this.onKeyPress,
  });

  static const List<List<String>> qwertyRows = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
  ];

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0, vertical: 6.0),
      child: Column(
        children: qwertyRows.map((row) {
          return Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: row.map((char) {
              final isGuessed = guessedLetters.contains(char);
              final isCorrect = maskedWord.contains(char);

              Color keyBg = const Color(0xFF181816);
              Color keyBorder = const Color(0xFF2A2A26);
              Color textColor = const Color(0xFFF1EBDD);
              TextDecoration textDec = TextDecoration.none;

              if (isGuessed) {
                if (isCorrect) {
                  keyBg = const Color(0xFFD5A84B).withOpacity(0.2);
                  keyBorder = const Color(0xFFD5A84B);
                  textColor = const Color(0xFFD5A84B);
                } else {
                  keyBg = const Color(0xFF11110F);
                  keyBorder = const Color(0xFF2A2A26);
                  textColor = const Color(0xFFA9A396).withOpacity(0.4);
                  textDec = TextDecoration.lineThrough;
                }
              }

              return Padding(
                padding: const EdgeInsets.all(2.5),
                child: SizedBox(
                  width: 30,
                  height: 40,
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      backgroundColor: keyBg,
                      side: BorderSide(color: keyBorder, width: 1),
                      padding: EdgeInsets.zero,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                    onPressed: isGuessed ? null : () => onKeyPress(char),
                    child: Text(
                      char.toUpperCase(),
                      style: GoogleFonts.inter(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: textColor,
                        decoration: textDec,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          );
        }).toList(),
      ),
    );
  }
}
