import 'package:flutter/material.dart';

class HangmanCanvas extends StatelessWidget {
  final int livesRemaining;
  final int maxLives;

  const HangmanCanvas({
    super.key,
    required this.livesRemaining,
    this.maxLives = 5,
  });

  @override
  Widget build(BuildContext context) {
    final mistakes = maxLives - livesRemaining;

    return Container(
      height: 140,
      width: 140,
      decoration: BoxDecoration(
        color: const Color(0xFF181816),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: const Color(0xFF2A2A26)),
      ),
      child: CustomPaint(
        painter: HangmanPainter(
          mistakes: mistakes,
          lineColor: const Color(0xFFF1EBDD),
          ropeColor: const Color(0xFFD5A84B),
          bodyColor: const Color(0xFFB95745),
        ),
      ),
    );
  }
}

class HangmanPainter extends CustomPainter {
  final int mistakes;
  final Color lineColor;
  final Color ropeColor;
  final Color bodyColor;

  HangmanPainter({
    required this.mistakes,
    required this.lineColor,
    required this.ropeColor,
    required this.bodyColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final gallowsPaint = Paint()
      ..color = lineColor.withOpacity(0.7)
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final bodyPaint = Paint()
      ..color = bodyColor
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final ropePaint = Paint()
      ..color = ropeColor
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;

    // Gallows base line
    canvas.drawLine(
      Offset(size.width * 0.15, size.height * 0.85),
      Offset(size.width * 0.65, size.height * 0.85),
      gallowsPaint,
    );

    // Vertical pole
    canvas.drawLine(
      Offset(size.width * 0.35, size.height * 0.85),
      Offset(size.width * 0.35, size.height * 0.15),
      gallowsPaint,
    );

    // Top beam
    canvas.drawLine(
      Offset(size.width * 0.35, size.height * 0.15),
      Offset(size.width * 0.75, size.height * 0.15),
      gallowsPaint,
    );

    // Noose rope
    canvas.drawLine(
      Offset(size.width * 0.75, size.height * 0.15),
      Offset(size.width * 0.75, size.height * 0.28),
      ropePaint,
    );

    final headCenter = Offset(size.width * 0.75, size.height * 0.36);
    final headRadius = size.height * 0.08;

    if (mistakes >= 1) {
      // Head
      canvas.drawCircle(headCenter, headRadius, bodyPaint);
    }

    if (mistakes >= 2) {
      // Torso
      canvas.drawLine(
        Offset(headCenter.dx, headCenter.dy + headRadius),
        Offset(headCenter.dx, headCenter.dy + headRadius + 24),
        bodyPaint,
      );
    }

    if (mistakes >= 3) {
      // Both Arms
      canvas.drawLine(
        Offset(headCenter.dx, headCenter.dy + headRadius + 6),
        Offset(headCenter.dx - 14, headCenter.dy + headRadius + 18),
        bodyPaint,
      );
      canvas.drawLine(
        Offset(headCenter.dx, headCenter.dy + headRadius + 6),
        Offset(headCenter.dx + 14, headCenter.dy + headRadius + 18),
        bodyPaint,
      );
    }

    if (mistakes >= 4) {
      // Left Leg
      canvas.drawLine(
        Offset(headCenter.dx, headCenter.dy + headRadius + 24),
        Offset(headCenter.dx - 12, headCenter.dy + headRadius + 40),
        bodyPaint,
      );
    }

    if (mistakes >= 5) {
      // Right Leg & Dead Eyes
      canvas.drawLine(
        Offset(headCenter.dx, headCenter.dy + headRadius + 24),
        Offset(headCenter.dx + 12, headCenter.dy + headRadius + 40),
        bodyPaint,
      );

      final eyePaint = Paint()
        ..color = const Color(0xFFB95745)
        ..strokeWidth = 1.5;

      canvas.drawLine(
        Offset(headCenter.dx - 4, headCenter.dy - 3),
        Offset(headCenter.dx - 1, headCenter.dy + 3),
        eyePaint,
      );
      canvas.drawLine(
        Offset(headCenter.dx - 1, headCenter.dy - 3),
        Offset(headCenter.dx - 4, headCenter.dy + 3),
        eyePaint,
      );

      canvas.drawLine(
        Offset(headCenter.dx + 1, headCenter.dy - 3),
        Offset(headCenter.dx + 4, headCenter.dy + 3),
        eyePaint,
      );
      canvas.drawLine(
        Offset(headCenter.dx + 4, headCenter.dy - 3),
        Offset(headCenter.dx + 1, headCenter.dy + 3),
        eyePaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant HangmanPainter oldDelegate) {
    return oldDelegate.mistakes != mistakes;
  }
}
