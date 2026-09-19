import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';

class WittyLossDialog extends StatelessWidget {
  final String title;
  final String message;
  final int consecutiveLosses;
  final String vocabularySuggestion;
  final VoidCallback onRetry;

  const WittyLossDialog({
    super.key,
    required this.title,
    required this.message,
    required this.consecutiveLosses,
    required this.vocabularySuggestion,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      backgroundColor: const Color(0xFF181816),
      title: Row(
        children: [
          const Icon(Icons.warning_amber_outlined, color: Color(0xFFB95745), size: 24),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              title.toUpperCase(),
              style: GoogleFonts.dmSerifDisplay(color: const Color(0xFFF1EBDD), fontSize: 18),
            ),
          ),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFB95745).withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(color: const Color(0xFFB95745).withOpacity(0.3)),
            ),
            child: Text(
              "\"$message\"",
              style: GoogleFonts.inter(
                fontStyle: FontStyle.italic,
                color: const Color(0xFFF1EBDD),
                fontSize: 13,
                height: 1.4,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            "Defeat Streak: $consecutiveLosses games",
            style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: const Color(0xFFA9A396), fontSize: 11),
          ),
          const SizedBox(height: 12),
          Text(
            "VOCABULARY TIP",
            style: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 10, letterSpacing: 1.0, color: const Color(0xFFD5A84B)),
          ),
          const SizedBox(height: 4),
          Text(
            vocabularySuggestion,
            style: GoogleFonts.inter(color: const Color(0xFFF1EBDD), fontSize: 12, height: 1.3),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.of(context).pop();
            context.push('/game/practice');
          },
          child: Text("PRACTICE MODE", style: GoogleFonts.inter(color: const Color(0xFFA9A396), fontSize: 12, fontWeight: FontWeight.bold)),
        ),
        OutlinedButton(
          style: OutlinedButton.styleFrom(
            foregroundColor: const Color(0xFFF1EBDD),
            side: const BorderSide(color: Color(0xFFD5A84B)),
          ),
          onPressed: () {
            Navigator.of(context).pop();
            onRetry();
          },
          child: Text("TRY AGAIN →", style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}
