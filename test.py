from enchant.checker import SpellChecker

checker = SpellChecker("en_US")
checker.set_text("This is sme sample txt with erors.")

for err in checker:
    print("ERROR:", err.word)
