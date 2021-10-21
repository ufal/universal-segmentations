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

def format_record(record):
    return "{}\t{}\t{}\t{}\t{}\n".format(
        record.form,
        record.lemma,
        record.pos,
        " + ".join(TODO),
        json.dumps(record.annot, ensure_ascii=False, allow_nan=False, indent=None, sort_keys=True)
    )
