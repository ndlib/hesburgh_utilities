from hesburgh import scriptText

text = ""
for bg in scriptText.BG_COLORS:
  text += scriptText.format("bg", bg)

print text
text = ""

for fg in scriptText.FG_COLORS:
  text += scriptText.format("fg", fg)

print text
text = ""

for extra in scriptText.EXTRA_FORMATS:
  text += scriptText.format("extra", extra)

print text
text = ""

for fg in scriptText.FG_COLORS:
  for bg in scriptText.BG_COLORS:
    text += scriptText.format("fgbg", fg, bg)
    for extra in scriptText.EXTRA_FORMATS:
      text += scriptText.format("all", fg, bg, extra)
  print text
  text = ""

print scriptText.success("win!")
print scriptText.error("lose!")
