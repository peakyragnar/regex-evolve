description = (
    "Match exactly the strings 'cat', 'dog', and 'bird', "
    "and reject all other strings."
)

cases = [
    ("cat",      True),
    ("dog",      True),
    ("bird",     True),
    ("fish",     False),
    ("cats",     False),
    ("dogs",     False),
    ("birds",    False),
    ("category", False),
    ("hotdog",   False),
    ("",         False),
    ("CAT",      False),
]
