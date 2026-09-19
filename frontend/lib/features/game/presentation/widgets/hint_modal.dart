import 'package:flutter/material.dart';

class HintModal extends StatelessWidget {
  final int coins;
  final Function(String hintType, int cost) onSelectHint;

  const HintModal({
    super.key,
    required this.coins,
    required this.onSelectHint,
  });

  static const List<Map<String, dynamic>> hintOptions = [
    {"type": "first_letter", "title": "Reveal First Letter", "cost": 30, "icon": Icons.title},
    {"type": "last_letter", "title": "Reveal Last Letter", "cost": 30, "icon": Icons.text_fields},
    {"type": "random_letter", "title": "Reveal Random Letter", "cost": 40, "icon": Icons.auto_awesome},
    {"type": "vowel_count", "title": "Vowel Count", "cost": 15, "icon": Icons.subtitles},
    {"type": "consonant_count", "title": "Consonant Count", "cost": 15, "icon": Icons.numbers},
    {"type": "definition", "title": "Word Definition", "cost": 25, "icon": Icons.menu_book},
    {"type": "part_of_speech", "title": "Part of Speech", "cost": 10, "icon": Icons.category},
    {"type": "category", "title": "Category", "cost": 10, "icon": Icons.explore},
    {"type": "synonym", "title": "Synonyms", "cost": 20, "icon": Icons.find_replace},
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardTheme.color,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              const Icon(Icons.lightbulb, color: Colors.amber),
              const SizedBox(width: 8),
              const Text(
                "INTELLIGENT HINT SHOP",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.amber.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.monetization_on, color: Colors.amber, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      "$coins",
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.amber),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          Flexible(
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: hintOptions.length,
              separatorBuilder: (context, index) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final opt = hintOptions[index];
                final canAfford = coins >= (opt['cost'] as int);

                return ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  tileColor: Theme.of(context).scaffoldBackgroundColor,
                  leading: Icon(opt['icon'] as IconData, color: canAfford ? Theme.of(context).colorScheme.primary : Colors.grey),
                  title: Text(
                    opt['title'] as String,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: canAfford ? null : Colors.grey,
                    ),
                  ),
                  trailing: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: canAfford ? Colors.amber : Colors.grey[700],
                      foregroundColor: Colors.black,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                    ),
                    onPressed: canAfford
                        ? () {
                            Navigator.pop(context);
                            onSelectHint(opt['type'] as String, opt['cost'] as int);
                          }
                        : null,
                    icon: const Icon(Icons.monetization_on, size: 14),
                    label: Text("${opt['cost']}"),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
