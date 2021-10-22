from collections import namedtuple
import json

SegRecord = namedtuple("SegRecord", ["form", "lemma", "pos", "simple_seg", "annot"])

def parse_line(line):
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
    def default(self, obj):
        if isinstance(obj, frozenset):
            return list(sorted(obj))
        return json.JSONEncoder.default(self, obj)

def format_record(record):
    joined_morphs = "".join(record.simple_seg)
    assert record.form == joined_morphs, "The segmentation {} doesn't match the word form '{}'".format(record.simple_seg, record.form)

    return "{}\t{}\t{}\t{}\t{}\n".format(
        record.form,
        record.lemma,
        record.pos,
        " + ".join(record.simple_seg),
        json.dumps(record.annot, ensure_ascii=False, allow_nan=False, indent=None, sort_keys=True, cls=SpanEncoder)
    )
