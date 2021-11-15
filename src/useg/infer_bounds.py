import sys
from unidecode import unidecode

l_ctg = {
    "a": "vowel",
    "e": "vowel",
    "i": "vowel",
    "o": "vowel",
    "u": "vowel",
    "æ": "vowel",
    "œ": "vowel",
    "ä": "vowel",
    "ë": "vowel",
    "ï": "vowel",
    "ö": "vowel",
    "ü": "vowel",
    "á": "vowel",
    "é": "vowel",
    "í": "vowel",
    "ó": "vowel",
    "ú": "vowel",
    "à": "vowel",
    "è": "vowel",
    "ì": "vowel",
    "ò": "vowel",
    "ù": "vowel",
    "â": "vowel",
    "ê": "vowel",
    "î": "vowel",
    "ô": "vowel",
    "û": "vowel",
    "å": "vowel",
    "ě": "vowel",
    "ø": "vowel",
    "A": "vowel",
    "E": "vowel",
    "I": "vowel",
    "O": "vowel",
    "U": "vowel",
    "Æ": "vowel",
    "Œ": "vowel",
    "Ä": "vowel",
    "Ë": "vowel",
    "Ï": "vowel",
    "Ö": "vowel",
    "Ü": "vowel",
    "Á": "vowel",
    "É": "vowel",
    "Í": "vowel",
    "Ó": "vowel",
    "Ú": "vowel",
    "À": "vowel",
    "È": "vowel",
    "Ì": "vowel",
    "Ò": "vowel",
    "Ù": "vowel",
    "Â": "vowel",
    "Ê": "vowel",
    "Î": "vowel",
    "Ô": "vowel",
    "Û": "vowel",
    "Å": "vowel",
    "Ě": "vowel",
    "Ø": "vowel",
    "b": "cons",
    "c": "cons",
    "č": "cons",
    "ç": "cons",
    "d": "cons",
    "ď": "cons",
    "f": "cons",
    "g": "cons",
    "h": "cons",
    "j": "cons",
    "k": "cons",
    "l": "cons",
    "ł": "cons",
    "m": "cons",
    "n": "cons",
    "ň": "cons",
    "ñ": "cons",
    "p": "cons",
    "q": "cons",
    "r": "cons",
    "ŕ": "cons",
    "ř": "cons",
    "s": "cons",
    "ś": "cons",
    "ş": "cons",
    "š": "cons",
    "ß": "cons",
    "t": "cons",
    "ť": "cons",
    "v": "cons",
    "w": "cons",
    "x": "cons",
    "z": "cons",
    "ž": "cons",
    "B": "cons",
    "C": "cons",
    "Č": "cons",
    "Ç": "cons",
    "D": "cons",
    "Ď": "cons",
    "F": "cons",
    "G": "cons",
    "H": "cons",
    "J": "cons",
    "K": "cons",
    "L": "cons",
    "Ł": "cons",
    "M": "cons",
    "N": "cons",
    "Ň": "cons",
    "Ñ": "cons",
    "P": "cons",
    "Q": "cons",
    "R": "cons",
    "Ŕ": "cons",
    "Ř": "cons",
    "S": "cons",
    "Ś": "cons",
    "Ş": "cons",
    "Š": "cons",
    "T": "cons",
    "Ť": "cons",
    "V": "cons",
    "W": "cons",
    "X": "cons",
    "Z": "cons",
    "Ž": "cons",
}

def letter_category(l):
    return l_ctg.get(l, "other")

def bound_indices(xs):
    """
    Return a set of indices, at which bounds occur in the list of strings xs.

    >>> bound_indices(["a", "bc", "def"])
    {0, 1, 3, 6}
    """
    bounds = set()
    current_pos = 0

    for item in xs:
        bounds.add(current_pos)
        current_pos += len(item)

    bounds.add(current_pos)

    return bounds

# Costs should be in order:
#  1. exact subst
#  2. subst differing in accent marks
#  3. insert or delete a vowel
#  4. subst vowel for vowel
#  5. insert or delete a consonant
#  6. subst consonant for consonant
#  7. subst consonant for vowel or vice versa
def subst_cost(sa, ia, sb, ib):
    ca = sa[ia]
    cb = sb[ib]

    if ca == cb:
        # Exact match.
        return 0.0

    da = unidecode(ca)
    db = unidecode(cb)

    if da == db:
        # The characters differ only in accent marks.
        return 0.1

    lca = letter_category(sa[ia])
    lcb = letter_category(sb[ib])

    if lca == lcb == "vowel":
        # Substitution of one vowel for another.
        return 0.5

    return 1.5

def insert_cost(s, i):
    lc = letter_category(s[i])
    if lc == "vowel":
        return 0.3

    return 1.0

def delete_cost(s, i):
    lc = letter_category(s[i])
    if lc == "vowel":
        return 0.3

    return 1.0

def infer_bounds(morphs, form):
    """
    Use the list of strings `morphs` to infer boundaries in the string
    `form`. Return a list of boundary indices.
    >>> infer_bounds(["pes", "vést"], "psovod")
    [0, 3, 6]
    """
    assert morphs, "Morphs must not be empty"
    assert form,   "Form must not be empty"
    for morph in morphs:
        assert morph, "No morph may be empty"

    verbose = False

    m_bounds = bound_indices(morphs)
    m_form = "".join(morphs)

    f_len = len(form)
    m_len = len(m_form)

    # Create the search space.
    ss = [[None] * (m_len + 1) for i in range(f_len + 1)]
    ss[0][0] = {"bounds": [0], "cost": 0.0}

    # Initialize the first row of the search space.
    # FIXME don't include the 0 boundary when starting out, the 0 may be
    #  mapped to another place in the form.
    for j in range(m_len):
        prev = ss[0][j]

        cost = prev["cost"] + delete_cost(m_form, j)

        if j in m_bounds and j != 0:
            if verbose:
                print("\t*d{}-{}".format(m_form[j], cost), file=sys.stderr, end="")
            bounds = prev["bounds"] + [0]
        else:
            if verbose:
                print("\td{}-{}".format(m_form[j], cost), file=sys.stderr, end="")
            bounds = prev["bounds"]


        ss[0][j+1] = {"bounds": bounds, "cost": cost}

    if verbose:
        print(file=sys.stderr)

    # Process the rest of the search space.
    for i in range(f_len):
        # Process the first column.
        cost = ss[i][0]["cost"] + insert_cost(form, i)
        if verbose:
            print("i{}-{}".format(form[i], cost), file=sys.stderr, end="")
        ss[i+1][0] = {"bounds": [i+1], "cost": cost}

        for j in range(m_len):
            s_cost = ss[ i ][ j ]["cost"] + subst_cost(m_form, j, form, i)
            d_cost = ss[i+1][ j ]["cost"] + delete_cost(m_form, j)
            i_cost = ss[ i ][j+1]["cost"] + insert_cost(form, i)

            cost = min(s_cost, d_cost, i_cost)
            if cost == s_cost:
                if j + 1 in m_bounds:
                    if verbose:
                        print("\t*s{}{}-{}".format(m_form[j], form[i], cost), file=sys.stderr, end="")
                    bounds = ss[i][j]["bounds"] + [i+1]
                else:
                    if verbose:
                        print("\ts{}{}-{}".format(m_form[j], form[i], cost), file=sys.stderr, end="")
                    bounds = ss[i][j]["bounds"]
            elif cost == i_cost:
                if verbose:
                    print("\ti{}-{}".format(form[i], cost), file=sys.stderr, end="")
                bounds = ss[i][j+1]["bounds"]
            elif cost == d_cost:
                if j + 1 in m_bounds:
                    if verbose:
                        print("\t*d{}-{}".format(m_form[j], cost), file=sys.stderr, end="")
                    bounds = ss[i+1][j]["bounds"] + [i+1]
                else:
                    if verbose:
                        print("\td{}-{}".format(m_form[j], cost), file=sys.stderr, end="")
                    bounds = ss[i+1][j]["bounds"]
            else:
                assert False

            ss[i+1][j+1] = {"bounds": bounds, "cost": cost}

        if verbose:
            print(file=sys.stderr)

    bounds = ss[f_len][m_len]["bounds"]
    assert len(bounds) == len(morphs) + 1, "Wrong number of bounds {} when segmenting {} by {}".format(bounds, form, morphs)
    assert bounds[0] >= 0
    assert bounds[-1] <= len(form)
    for i in range(1, len(bounds)):
        assert bounds[i-1] <= bounds[i], "Bounds {} not strictly ascending when segmenting {} by {}".format(bounds, form, morphs)

    return bounds
