#!/usr/bin/env python3

import re
import sys
sys.path.append('../../src/')
from useg import SegLex
from collections import defaultdict


import logging
# logging.basicConfig(filename="unsolved.log", level=logging.WARNING)

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    # formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    # fileHandler.setFormatter(formatter)
    # streamHandler = logging.StreamHandler()
    # streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    # l.addHandler(streamHandler)

setup_logger('gen_issues', r'general.log')
setup_logger('seg_issues', r'segmentation.log')
setup_logger('boundary_overlap_issues', r'boundary_overlaps.log')
setup_logger('pos_issues', r'pos.log')
gen_issues = logging.getLogger('gen_issues')
seg_issues = logging.getLogger('seg_issues')
pos_issues = logging.getLogger('pos_issues')
boundary_overlap_issues = logging.getLogger('boundary_overlap_issues')

if len(sys.argv) != 4:
    sys.stderr.write("Usage:\n  "+__file__+" Italian-DerIvaTario-file.csv UDer-Italian-file.tsv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[3]}")

def initialize_all_upos():
    '''Reads UDer file and converts to dictionary'''
    uder = open(sys.argv[2])
    upos_assignment = defaultdict(lambda: set())
    for line in uder:
        if line == "\n" or line == " ":
            continue
        word, upos = line.split("\t")[1].strip().split("#")
        upos_assignment[word].add(upos)

        # if word in upos_assignment and upos_assignment[word] != upos:
        #     # logging.warning("Word %s has more than 1 POS: %s, %s ", word, upos_assignment[word], upos)
        #     upos_assignment[word] = upos_assignment[word] + " , " + upos
        # else:
        #     upos_assignment[word] = upos

    return upos_assignment


def assign_upos(lexeme, upos_assignment):
    '''Finds lexeme in UDer and its POS'''

    if len(upos_assignment[lexeme])==0:
        pos_issues.warning("Lexeme %s not in UDer, POS not found", lexeme)
        return "UNK", set()
    #RETURNING SOME CHOSEN POS AS WELL THE REMAINING ELEMENTS
    for pos in upos_assignment[lexeme]:
        break
    return pos, upos_assignment[lexeme] - {pos}

def longest_common_prefix(s, t):
    '''Finds length of LCP'''
    lcp_len = 0
    while(lcp_len <= min(len(s),len(t)) and s[:lcp_len]==t[:lcp_len]):
        lcp_len += 1
    return lcp_len-1

def find_morph_boundaries(lexeme, morph, req_start = -1, is_last = False, is_prefix = False):
    '''Finds boundaries of allomorph'''
    # if is_prefix:
    #     return 0, longest_common_prefix(lexeme, morph)
    morph_start = 0
    for i in range(len(morph)):
        # print(i)
        # print(morph[:len(morph)-i])
        # morph_start = lexeme.find(morph[:len(morph)-i])
        shortened_morph = morph[:len(morph)-i]

        dist_from_req_start = len(lexeme)+1

        best_start, best_end = -1, -1

        for match in re.finditer(shortened_morph, lexeme):
            current_start, current_end = -1, -1

            morph_start, morph_end = match.start(), match.end()

            if morph_start != -1:

                #If we are not dealing with prefix
                if is_prefix == False and morph_start >= req_start:
                    if is_last==False and morph_end == len(lexeme):
                        pass
                    else:
                        current_start, current_end = morph_start, morph_end

                #Allow one-character interfix for prefixes - e.g. "-"
                allowed_interfix_len = 1
                if morph_start <= req_start + allowed_interfix_len and morph_start >= req_start:
                    current_start, current_end = morph_start, morph_end

                #If morph is found before req_start, it should span the previous morph for all affixes
                if morph_start < req_start:
                    if shortened_morph.startswith(lexeme[morph_start:req_start]):
                        current_start, current_end = morph_start, morph_end


                #If more than 1 matches for same length, choose the one closest to req_start
                if best_start == -1:
                    best_start, best_end = current_start, current_end

                if current_start != -1 and abs(current_start - req_start) < abs(best_start - req_start):
                    best_start, best_end = current_start, current_end

        if best_start != -1:
            return best_start, best_end

    return -1,-1


def choose_allomorph_boundaries(lexeme, allomorph_set = set(), req_start = -1, is_last = False, is_prefix = False):
    '''Finds boundaries of allomorph'''
    # if is_prefix:
    #     return 0, longest_common_prefix(lexeme, morph)
    best_boundary = dict()

    for morph in allomorph_set:
        morph_start, morph_end = find_morph_boundaries(lexeme, morph, req_start, root_not_found, is_prefix)
        if morph_start != -1:
            best_boundary[morph] = (morph_start, morph_end)

    #Choose allomorph with best boundary
    if len(best_boundary) == 0:
        return -1,-1

    if len(best_boundary) == 1:
        for morph in best_boundary:
            return best_boundary[morph]

    allo_lengths = [[morph, best_boundary[morph][1]-best_boundary[morph][0]] for morph in best_boundary.keys()]
    allo_lengths = sorted(allo_lengths, key = lambda x: x[1], reverse=True)

    # if allo_lengths[0][1] > allo_lengths[1][1]:
    #     return best_boundary[allo_lengths[0][0]]

    #Take all allomorphs with max len
    best_allo_lengths = filter(lambda x: x[1]==allo_lengths[0][1], allo_lengths)

    #If not, judge by closeness to req_start
    dist_from_req = [[morph, abs(req_start - best_boundary[morph][0])] for [morph, len] in best_allo_lengths]
    dist_from_req = sorted(dist_from_req, key = lambda x: x[1])

    return best_boundary[dist_from_req[0][0]]



# print(find_morph_boundaries("vactacaction", "tion"))

lexicon = SegLex()

infile = open(sys.argv[1])

annot_name = "DerIvaTario"

prefixes = {"acons", "anti", "auto", "bi", "tri", "de", "1de", "2de", "dis", "in",
"micro", "mini", "ri", "1s", "2s", "co", "neo", "1in", "2in", "a", "con",
"per", "pre", "inter", "intra", "iper", "mega", "mono", "maxi", "multi", "pan",
"cis", "para", "pro", "tras", "es",
"ex","e", "proto", "stra", "trans", "fra"}

root_types = {"adj_th", "dnt_root", "ltn_pp", "presp", "pst_ptcp", "root", "suppl", "unrec", "vrb_th"}

complex_base_type = {"acr", "cmp", "neocl_cmp", "noun_phr", "parad", "prp_phr", "vrb_phr"}

allomorph_set = {
"1aio":{"aio"},
"2aio":{"aio", "aro"},
"ale":{"ale","are","iale","uale"},
"bile":{"bile","ibile"},
"ico":{"ico","atico"},
"1in":{"in","im","il","ir"},
"2in":{"in","im","il","ir"},
"ismo":{"ismo","tismo"},
"ità":{"ità","età","tà"},
"oso":{"oso","uoso"},
"ri":{"ri","re"},
"trans":{"trans","tras"},
"tore":{"tore","ore"},
"ore":{"tore","ore"},
"torio":{"torio","orio"},
"orio":{"torio","orio"},
"tora":{"tora","ora"},
"ora":{"tora","ora"},
"zione":{"zione","gione","ione","sion","sione"},
"ione":{"zione","gione","ione","sion","sione"},
"nza":{"nza"} #This is just because "NZA" is sometimes annotated with "object" as allomorph
}



upos_assignment = initialize_all_upos()

for line in infile:
    entries = [s.lower() for s in line.strip().split(";")]
    entries = list(filter(lambda f: f!="", entries))
    colfis_id = entries[0]
    lexeme = entries[1]
    root = entries[2].split(":")


    # if lexeme!="RACCAPEZZARE".lower():
        # continue

    if len(root) < 2:
        gen_issues.warning("Root %s does not have 2 fields", root)
        continue
    if len(entries) <= 2:
        gen_issues.warning("Lexeme %s only has root", lexeme)

    lex_features = dict()
    lex_features["colfis_id"] = colfis_id

    upos, all_upos = assign_upos(lexeme, upos_assignment)
    # lex_features["upos"] = upos
    # if all_upos:
    #     lex_features["other_possible_upos"] = " , ".join(all_upos)

    if root[0] == "BASELESS":
        lex_features["root"] = "unrec"
    else:
        lex_features["root"] = root[0]
        if root[1] != "root":
            lex_features["root_type"] = root[1]
        if len(root) > 2:
            lex_features["complex_type"] = root[2]

    for upos in all_upos.union({upos}):

        lex_features["upos"] = upos
        lex_id = lexicon.add_lexeme(lexeme, lexeme, upos, features=lex_features)

        info_morphemes = entries[2:]

        # Arranging morphemes according to order in wordform
        morpheme_seq = []
        ordering = list()
        for idx, info_morpheme in enumerate(info_morphemes):
            if info_morpheme.split(":")[0] in prefixes:
                morpheme_seq = [info_morpheme] + morpheme_seq
                ordering = [idx] + ordering
            else:
                morpheme_seq = morpheme_seq + [info_morpheme]
                ordering = ordering + [idx]

            # if info_morpheme.split(":")[0] == "conversion":
                # conversion_lengths.append(sum([len(m.split(":")[1]) for m in morpheme_seq]))


        # print("lexeme ", lexeme)
        # print("info_morpheme ", info_morphemes)
        # print("morpheme_seq ", morpheme_seq)
        # print("ordering ", ordering)
        # print("conv length ", conversion_lengths)

        start = 0
        root_not_found = False
        post_root = False
        for info_morpheme_idx, info_morpheme in enumerate(morpheme_seq):
            is_last = info_morpheme_idx == len(morpheme_seq)-1

            is_root = False
            is_prefix = False

            order = ordering.pop(0)

            if info_morpheme.split(":")[0] == "conversion":
                # print(conversion_lengths, info_morpheme)
                # length = conversion_lengths[0]
                # conversion_lengths = conversion_lengths[1:]
                features = {"type":"conversion", "ordering":order}
                if info_morpheme.endswith("-p"):
                    features["order_info"] = "simultaneous"
                    info_morpheme = info_morpheme[:-2]
                if info_morpheme.endswith("-g"):
                    features["order_info"] = "undecided"
                    info_morpheme = info_morpheme[:-2]
                features["conv_type"] = info_morpheme.split(":")[1]

                lexicon.add_contiguous_morpheme(lex_id, annot_name, start, start, features)

                continue

            if len(info_morpheme.split(":")) < 2:
                seg_issues.warning("Empty morph information %s of lexeme %s with desc %s", info_morpheme, lexeme, line)
                continue

            if info_morpheme.split(":")[1] in root_types:
                is_root = True

            if info_morpheme.split(":")[0] == "baseless" or info_morpheme.split(":")[1] == "suppl":
                root_not_found = True
                continue

            morpheme = info_morpheme.split(":")[0]
            if morpheme in prefixes:
                is_prefix = True

            if is_root: #handing NZA:object annotation
                allomorph = info_morpheme.split(":")[0]
            else:
                allomorph = info_morpheme.split(":")[1]


            current_allomorph_set = {allomorph}
            if morpheme in allomorph_set:
                current_allomorph_set = current_allomorph_set.union(allomorph_set[morpheme])

            # HANDLING PRE-S/RI-S RE-ORDERING OF PREFIXES BY SIMPLE HEURISTIC
            set_start = start
            if allomorph in ["s", "ri"] and lexeme.startswith(allomorph[0]):
                set_start = 0
                #This works because there are no other prefixes that start with "s"
                #Specifically, there are none that cause a prefix re-ordering ("ri", "pre")
                #Since the prefix must be before the root, if we know that the prefix "s"
                #exists in the word, and the first letter is "s", that must be the prefix.
                #Similar argument for "ri"

            morph_start, morph_end = choose_allomorph_boundaries(lexeme, current_allomorph_set, set_start, is_last, is_prefix)

            # print(morpheme, allomorph, morph_start, morph_end)
            #POSSIBLE ISSUES
            if morph_start == -1:
                if is_root:
                    root_not_found = True
                seg_issues.warning("Morph %s not found in lexeme %s with entry %s", allomorph, lexeme, line)
                continue
            if morph_end <= start:
                seg_issues.warning("Morph %s contained in previous morph in lexeme %s with entry %s", allomorph, lexeme, line)
            if morph_start < start:
                if allomorph.startswith(lexeme[morph_start:start]):
                    boundary_overlap_issues.warning("Morph %s overlaps with previous morpheme in lexeme %s with entry %s", allomorph, lexeme, line)
            if morph_start == morph_end:
                seg_issues.warning("Empty morph %s in lexeme %s with entry %s", allomorph, lexeme, line)
                continue

            #CHECK FOR DOUBLING
            doubling = False
            if morpheme == "acons":
                if lexeme[morph_end] == lexeme[morph_end+1]:
                    morph_end = morph_end+1
                    doubling = True


            # print("New field: ")
            # print(info_morpheme)
            # print("Search with start: ", start)
            # print("Final ", morpheme, allomorph, morph_start, morph_end)
            #ADD INTERFIX/STEM IF REQUIRED
            if morph_start > start:
                if root_not_found:
                    #ADD WARNING HERE?
                    features = {"type":"root", "ordering":0}
                    features["morpheme"] = lex_features["root"]
                    if "root_type" in lex_features:
                        features["root_type"] = lex_features["root_type"]
                    if "complex_type" in lex_features:
                        features["complex_type"] = lex_features["complex_type"]
                    lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features)
                    root_not_found = False
                elif post_root:
                    lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features={"type":"part_of_root","ordering":0})
                else:
                    lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features={"type":"interfix","ordering":order})
            #ADD MORPH
            #Find features
            features = {"morpheme":morpheme, "ordering":order}
            if is_root == True:
                features["type"] = "root"
                if "root_type" in lex_features:
                    features["root_type"] = lex_features["root_type"]
                if "complex_type" in lex_features:
                    features["complex_type"] = lex_features["complex_type"]
            else:
                if info_morpheme.endswith("-p"):
                    features["order_info"] = "simultaneous"
                    info_morpheme = info_morpheme[:-2]
                if info_morpheme.endswith("-g"):
                    features["order_info"] = "undecided"
                    info_morpheme = info_morpheme[:-2]

                if len(info_morpheme.split(":")) > 2:
                    features["mt"] = info_morpheme.split(":")[2][2:]
                if len(info_morpheme.split(":")) > 3:
                    features["ms"] = info_morpheme.split(":")[3][2:]

            if doubling:
                features["doubling"] = True

            lexicon.add_contiguous_morpheme(lex_id, annot_name, morph_start, morph_end, features)


            start = max(start, morph_end)

            #post_root only true if current morph was root, if not, it needs to be falsified
            if is_root:
                post_root = True
            else:
                post_root = False
            #root_not_found only stays true for the immediately next morph, not after that
            if root_not_found:
                root_not_found = False

        #ADD FOR ALL UPOS
        # curr_lexeme = lexicon.form(lex_id)
        # curr_lemma = lexicon.lemma(lex_id)
        # curr_features = lexicon.features(lex_id)


outfile = open(sys.argv[3], 'w')
lexicon.save(outfile)
