import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class LifelineModal extends StatefulWidget {
  final int level;
  final int inventory;
  final Function(String option) onSelectOption;

  const LifelineModal({
    super.key,
    required this.level,
    required this.inventory,
    required this.onSelectOption,
  });

  @override
  State<LifelineModal> createState() => _LifelineModalState();
}

class _LifelineModalState extends State<LifelineModal> {
  String? _selectedOption;

  @override
  Widget build(BuildContext context) {
    final isLocked = widget.level < 5;
    final hasInventory = widget.inventory > 0;
    final canUse = !isLocked && hasInventory;

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 440),
        decoration: BoxDecoration(
          color: const Color(0xFF181816),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFD5A84B).withOpacity(0.4), width: 1.5),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.6),
              blurRadius: 20,
              spreadRadius: 2,
            ),
          ],
        ),
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.flash_on, color: Color(0xFFD5A84B), size: 20),
                    const SizedBox(width: 8),
                    Text(
                      "WORD LIFELINE",
                      style: GoogleFonts.dmSerifDisplay(
                        fontSize: 18,
                        color: const Color(0xFFF1EBDD),
                        letterSpacing: 0.5,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2A2A26),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: const Color(0xFFD5A84B).withOpacity(0.3)),
                  ),
                  child: Text(
                    "INVENTORY: ${widget.inventory}",
                    style: GoogleFonts.inter(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFFD5A84B),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              isLocked
                  ? "Word Lifeline unlocks at Classic Level 5. Reach Level 5 to access strategic assistance options."
                  : "Select one strategic assistance option. Using a lifeline consumes 1 item from inventory.",
              style: GoogleFonts.inter(
                fontSize: 12,
                color: const Color(0xFFA9A396),
                height: 1.4,
              ),
            ),
            const SizedBox(height: 16),

            // Option A: Reveal a Letter
            _buildOptionCard(
              optionKey: 'reveal_letter',
              title: "OPTION A: REVEAL A LETTER",
              description: "Instantly unveils 1 unrevealed position in the word without deducting any hearts.",
              icon: Icons.font_download_outlined,
              isLocked: isLocked || !hasInventory,
            ),
            const SizedBox(height: 10),

            // Option B: Striking Clue
            _buildOptionCard(
              optionKey: 'striking_clue',
              title: "OPTION B: STRIKING CLUE",
              description: "Reveals a concise, high-impact 1-sentence semantic clue tailored to this word.",
              icon: Icons.auto_awesome_outlined,
              isLocked: isLocked || !hasInventory,
            ),
            const SizedBox(height: 20),

            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: Text(
                    "CANCEL",
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFFA9A396),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFD5A84B),
                    foregroundColor: const Color(0xFF181816),
                    disabledBackgroundColor: const Color(0xFF2A2A26),
                    disabledForegroundColor: const Color(0xFFA9A396),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                  ),
                  onPressed: (canUse && _selectedOption != null)
                      ? () {
                          Navigator.of(context).pop();
                          widget.onSelectOption(_selectedOption!);
                        }
                      : null,
                  child: Text(
                    "ACTIVATE LIFELINE",
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOptionCard({
    required String optionKey,
    required String title,
    required String description,
    required IconData icon,
    required bool isLocked,
  }) {
    final isSelected = _selectedOption == optionKey;

    return InkWell(
      onTap: isLocked
          ? null
          : () {
              setState(() {
                _selectedOption = optionKey;
              });
            },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFFD5A84B).withOpacity(0.12) : const Color(0xFF22221E),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected
                ? const Color(0xFFD5A84B)
                : (isLocked ? const Color(0xFF2A2A26) : const Color(0xFF3A3A34)),
            width: isSelected ? 1.5 : 1.0,
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              isLocked ? Icons.lock_outline : icon,
              size: 22,
              color: isLocked
                  ? const Color(0xFF6A6A60)
                  : (isSelected ? const Color(0xFFD5A84B) : const Color(0xFFA9A396)),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: isLocked
                          ? const Color(0xFF6A6A60)
                          : (isSelected ? const Color(0xFFD5A84B) : const Color(0xFFF1EBDD)),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: isLocked ? const Color(0xFF55554E) : const Color(0xFFA9A396),
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
