"""pathladder: schema-driven weak labels from GI pathology report free text."""
from .schema import LabelSchema, BARRETTS_LADDER, TCGA_GI
from .extract import label_report, label_frame

__version__ = "0.1.0"
__all__ = ["LabelSchema", "BARRETTS_LADDER", "TCGA_GI", "label_report", "label_frame"]
