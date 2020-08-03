special_chars = {
    '─': 'Ä',
    'Σ': 'ä',
    '╓': 'Ö',
    '÷': 'ö',
    '▄': 'Ü',
    'ⁿ': 'ü',
    '▀': 'ß',
}

def check_substring(line):
  print('Line to check: ' + line)
  for sc in special_chars:
    print('Checking for ' + sc)
    while sc in line:
      line = line.replace(sc, special_chars.get(sc))
    print(line)

  return line

check_substring('─ ── Schⁿtz ⁿⁿ Σ ΣΣ ╓ ╓╓ ÷ffentlich ÷÷ ▄ ▄▄ gro▀ ▀▀')
