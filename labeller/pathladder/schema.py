"""Label schemas: each maps report text patterns onto target label sets.

A schema is a list of fields. Ordinal fields (ladder=True) resolve multiple
matches by taking the highest rung — the pathology convention that the worst
finding determines the diagnosis. Categorical fields take the most frequent
match, ties broken by pattern order.
"""
from dataclasses import dataclass, field


@dataclass
class Field:
    name: str
    # ordered (label, [regex, ...]) pairs; for ladder fields, order = severity (low->high)
    levels: list
    ladder: bool = False


@dataclass
class LabelSchema:
    name: str
    fields: list = field(default_factory=list)


# --- Barrett's surveillance ladder (ERIN-style reports) --------------------
# Severity order matters: highest matched rung wins.
BARRETTS_LADDER = LabelSchema(
    name="barretts_ladder",
    fields=[
        Field(
            name="grade",
            ladder=True,
            levels=[
                ("NDBE", [
                    r"\bbarrett'?s?\b(?![^.]*dysplas)",
                    r"\bintestinal metaplasia\b(?![^.]*dysplas)",
                    r"\bnegative for dysplasia\b",
                    r"\bno (?:evidence of )?dysplasia\b",
                ]),
                ("IND", [
                    r"\bindefinite for dysplasia\b",
                    r"\batypia[^.]*(?:indefinite|uncertain)\b",
                ]),
                ("LGD", [
                    r"\blow[- ]grade (?:glandular )?dysplasia\b",
                    r"\bLGD\b",
                ]),
                ("HGD", [
                    r"\bhigh[- ]grade (?:glandular )?dysplasia\b",
                    r"\bHGD\b",
                ]),
                ("CANCER", [
                    r"\badenocarcinoma\b",
                    r"\bcarcinoma\b",
                    r"\bmalignan(?:t|cy)\b",
                    r"\bintramucosal (?:adeno)?carcinoma\b",
                ]),
            ],
        ),
    ],
)

# --- TCGA GI resection reports ---------------------------------------------
TCGA_GI = LabelSchema(
    name="tcga_gi",
    fields=[
        Field(
            name="histologic_type",
            levels=[
                ("adenocarcinoma", [r"\badeno[- ]?carcinoma\b", r"\bsignet[- ]ring\b"]),
                ("squamous", [r"\bsquamous(?:[- ]cell)? carcinoma\b", r"\bSCC\b"]),
            ],
        ),
        Field(
            name="grade",
            ladder=True,
            levels=[
                ("G1", [r"\bwell[- ]differentiated\b", r"\bgrade 1\b", r"\bG1\b"]),
                ("G2", [r"\bmoderately[- ]differentiated\b", r"\bgrade 2\b", r"\bG2\b"]),
                ("G3", [r"\bpoorly[- ]differentiated\b", r"\bgrade 3\b", r"\bG3\b",
                        r"\bundifferentiated\b", r"\bgrade 4\b"]),
            ],
        ),
        Field(
            name="site",
            levels=[
                ("esophagus", [r"\b(?:o)?esophag(?:us|eal)\b"]),
                ("gej", [r"\bgastro[- ]?(?:o)?esophageal junction\b", r"\bGE junction\b",
                         r"\bcardia\b", r"\bEGJ\b", r"\bGEJ\b"]),
                ("stomach", [r"\bstomach\b", r"\bgastric\b(?![^.]*junction)"]),
            ],
        ),
    ],
)
