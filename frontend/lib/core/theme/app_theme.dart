import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Warm Ink & Paper Editorial Palette
  static const Color darkBackground = Color(0xFF11110F);
  static const Color darkSurface = Color(0xFF181816);
  static const Color darkBorder = Color(0xFF2A2A26);
  
  static const Color paperText = Color(0xFFF1EBDD);
  static const Color mutedInk = Color(0xFFA9A396);
  
  static const Color goldAccent = Color(0xFFD5A84B);
  static const Color terracottaAccent = Color(0xFFB95745);
  static const Color sageSuccess = Color(0xFF879873);

  static ThemeData get darkTheme {
    final baseTextTheme = GoogleFonts.interTextTheme(ThemeData.dark().textTheme);

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: darkBackground,
      colorScheme: const ColorScheme.dark(
        primary: goldAccent,
        secondary: terracottaAccent,
        surface: darkSurface,
        error: terracottaAccent,
        onSurface: paperText,
      ),
      textTheme: baseTextTheme.copyWith(
        displayLarge: GoogleFonts.dmSerifDisplay(color: paperText, fontSize: 32),
        displayMedium: GoogleFonts.dmSerifDisplay(color: paperText, fontSize: 26),
        displaySmall: GoogleFonts.dmSerifDisplay(color: paperText, fontSize: 22),
        headlineMedium: GoogleFonts.dmSerifDisplay(color: paperText, fontSize: 20),
        titleLarge: GoogleFonts.dmSerifDisplay(color: paperText, fontSize: 18),
        bodyLarge: GoogleFonts.inter(color: paperText, fontSize: 15),
        bodyMedium: GoogleFonts.inter(color: mutedInk, fontSize: 13),
        labelLarge: GoogleFonts.inter(color: paperText, fontSize: 13, fontWeight: FontWeight.bold, letterSpacing: 1.0),
      ),
      cardTheme: CardThemeData(
        color: darkSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
          side: const BorderSide(color: darkBorder, width: 1),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: darkBorder,
        thickness: 1,
        space: 1,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: darkBackground,
        elevation: 0,
        centerTitle: true,
        scrolledUnderElevation: 0,
        titleTextStyle: TextStyle(color: paperText, fontSize: 18, fontWeight: FontWeight.bold),
      ),
    );
  }

  static ThemeData get lightTheme => darkTheme;
}
