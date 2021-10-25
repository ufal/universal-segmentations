from collections import namedtuple
import json

SegRecord = namedtuple("SegRecord", ["form", "lemma", "pos", "simple_seg", "annot"])

def parse_line(line):
    """
    Parse an Universal-Segmentations-formatted `line` and return
    a direct object representation of its contents as a namedtuple.
    """
    line = line.rstrip("\n")
    fields = line.split("\t", maxsplit=4)

    if len(fields) != 5:
        raise ValueError("Invalid line '{}'".format(line))

    simple_seg = fields[3].split(" + ")
    annot = json.loads(fields[4])

    return SegRecord(
        fields[0],
        fields[1],
        fields[2],
        simple_seg,
        annot
    )

class SpanEncoder(json.JSONEncoder):
    """
    Properly serialize morph spans, which are represented using
    frozensets, as ordered lists.
    """
    def default(self, o):
        if isinstance(o, frozenset):
            return list(sorted(o))
        return json.JSONEncoder.default(self, o)

def format_record(record):
    """
    Serialize the SegRecord namedtuple `record` into its TSV format and
    return the string of the line, with the line-terminating newline
    already attached.
    """
    joined_morphs = "".join(record.simple_seg)
    assert record.form == joined_morphs, \
        "The segmentation {} doesn't match the word form '{}'".format(record.simple_seg, record.form)

    return "{}\t{}\t{}\t{}\t{}\n".format(
        record.form,
        record.lemma,
        record.pos,
        " + ".join(record.simple_seg),
        json.dumps(
            record.annot,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            sort_keys=True,
            cls=SpanEncoder
        )
    )
