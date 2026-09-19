import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class KnowledgeCard extends StatelessWidget {
  final Map<String, dynamic> cardData;
  final VoidCallback onNextGame;

  const KnowledgeCard({
    super.key,
    required this.cardData,
    required this.onNextGame,
  });

  @override
  Widget build(BuildContext context) {
    final word = cardData['word'] ?? '';
    final def = cardData['definition'] ?? '';
    final pos = cardData['part_of_speech'] ?? '';
    final synonyms = List<String>.from(cardData['synonyms'] ?? []);
    final category = cardData['category'] ?? 'General';

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF181816),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFD5A84B), width: 1.5),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                category.toUpperCase(),
                style: GoogleFonts.inter(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  color: const Color(0xFFD5A84B),
                ),
              ),
              const Spacer(),
              Text(
                pos,
                style: GoogleFonts.inter(
                  fontStyle: FontStyle.italic,
                  fontSize: 12,
                  color: const Color(0xFFA9A396),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            word,
            style: GoogleFonts.dmSerifDisplay(
              fontSize: 28,
              color: const Color(0xFFF1EBDD),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            def,
            style: GoogleFonts.inter(
              fontSize: 13,
              height: 1.4,
              color: const Color(0xFFF1EBDD),
            ),
          ),
          if (synonyms.isNotEmpty) ...[
            const SizedBox(height: 14),
            Text(
              "SYNONYMS",
              style: GoogleFonts.inter(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.0,
                color: const Color(0xFFA9A396),
              ),
            ),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              children: synonyms.map((s) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFF11110F),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: const Color(0xFF2A2A26)),
                  ),
                  child: Text(
                    s,
                    style: GoogleFonts.inter(fontSize: 11, color: const Color(0xFFF1EBDD)),
                  ),
                );
              }).toList(),
            ),
          ],
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            height: 44,
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFFF1EBDD),
                side: const BorderSide(color: Color(0xFFD5A84B)),
              ),
              onPressed: onNextGame,
              child: Text(
                "PLAY NEXT WORD →",
                style: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 1.0),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
