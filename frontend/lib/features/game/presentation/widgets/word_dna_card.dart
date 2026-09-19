import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class WordDnaCard extends StatelessWidget {
  final Map<String, dynamic> dna;

  const WordDnaCard({super.key, required this.dna});

  @override
  Widget build(BuildContext context) {
    final length = dna['length'] ?? 0;
    final vowels = dna['vowels'] ?? 0;
    final consonants = dna['consonants'] ?? 0;
    final repeated = dna['has_repeated_letters'] ?? false;
    final category = dna['category'] ?? 'General';
    final pos = dna['part_of_speech'] ?? 'word';

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 4.0),
      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
      decoration: BoxDecoration(
        color: const Color(0xFF181816),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF2A2A26)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "WORD DNA",
                style: GoogleFonts.inter(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                  color: const Color(0xFFD5A84B),
                ),
              ),
              Text(
                "[$category · $pos]",
                style: GoogleFonts.inter(
                  fontSize: 10,
                  fontStyle: FontStyle.italic,
                  color: const Color(0xFFA9A396),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Wrap(
            spacing: 12,
            children: [
              _MetadataItem(label: "LENGTH", value: "$length"),
              _MetadataItem(label: "VOWELS", value: "$vowels"),
              _MetadataItem(label: "CONSONANTS", value: "$consonants"),
              _MetadataItem(label: "REPEATED", value: repeated ? "YES" : "NO"),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetadataItem extends StatelessWidget {
  final String label;
  final String value;
  const _MetadataItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          "$label: ",
          style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFFA9A396), fontWeight: FontWeight.bold),
        ),
        Text(
          value,
          style: GoogleFonts.inter(fontSize: 10, color: const Color(0xFFF1EBDD), fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}
