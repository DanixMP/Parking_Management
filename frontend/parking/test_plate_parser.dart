import 'lib/utils/plate_parser.dart';

void main() {
  print('Testing PlateParser...\n');

  final testPlates = [
    'ب1311110',
    '1311110ب',
    'و315715',
    'و5136575',
    'و513565715',
  ];

  for (final plate in testPlates) {
    print('Testing: $plate');
    final result = PlateParser.parse(plate);
    print('Result: $result');
    print('---');
  }
}
