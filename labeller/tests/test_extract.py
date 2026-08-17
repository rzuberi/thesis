import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from pathladder import label_report, BARRETTS_LADDER, TCGA_GI


def grade(text):
    return label_report(text, BARRETTS_LADDER)["grade"]


def test_ndbe():
    assert grade("Barrett's oesophagus with intestinal metaplasia. No dysplasia seen.") == "NDBE"


def test_negated_dysplasia_not_lgd():
    assert grade("Negative for dysplasia. Barrett's mucosa present.") == "NDBE"


def test_lgd():
    assert grade("Barrett's mucosa with low-grade dysplasia.") == "LGD"


def test_ladder_max_rule():
    assert grade("Fragments show low grade dysplasia; focal high-grade dysplasia present.") == "HGD"


def test_cancer_tops_ladder():
    assert grade("HGD with a focus of intramucosal adenocarcinoma.") == "CANCER"


def test_negated_malignancy():
    assert grade("No evidence of malignancy. Barrett's oesophagus, negative for dysplasia.") == "NDBE"


def test_indefinite():
    assert grade("Glandular atypia, indefinite for dysplasia.") == "IND"


def test_tcga_fields():
    r = label_report(
        "Moderately differentiated adenocarcinoma of the distal esophagus "
        "extending to the gastroesophageal junction.", TCGA_GI)
    assert r["histologic_type"] == "adenocarcinoma"
    assert r["grade"] == "G2"
    assert r["site"] in ("esophagus", "gej")


def test_tcga_squamous_g3():
    r = label_report("Poorly differentiated squamous cell carcinoma of the mid esophagus.", TCGA_GI)
    assert r["histologic_type"] == "squamous"
    assert r["grade"] == "G3"


def test_empty():
    assert grade("Specimen inadequate for assessment.") is None
