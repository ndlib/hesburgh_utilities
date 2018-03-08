from hesburgh import scriptutil

text = ""
for bg in scriptutil.BG_COLORS:
  text += scriptutil.format("bg", bg)

print text
text = ""

for fg in scriptutil.FG_COLORS:
  text += scriptutil.format("fg", fg)

print text
text = ""

for extra in scriptutil.EXTRA_FORMATS:
  text += scriptutil.format("extra", extra)

print text
text = ""

for fg in scriptutil.FG_COLORS:
  for bg in scriptutil.BG_COLORS:
    text += scriptutil.format("fgbg", fg, bg)
    for extra in scriptutil.EXTRA_FORMATS:
      text += scriptutil.format("all", fg, bg, extra)
  print text
  text = ""

print scriptutil.success("win!")
print scriptutil.error("lose!")
