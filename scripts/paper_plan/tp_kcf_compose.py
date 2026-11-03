"""Two papers, agent KCF: compose the Killcoyne 2020 comparison pages (local; figures only, no row-level data).
Each page: (1) the original published panel (cropped from the locally held publisher PDF; internal comparison only), (2) our copy-number
reproduction, (3) the same analysis with the H&E score, (4) with H&E + copy number. Pages where H&E does not apply are two-way.
Inputs: paper/one_paper/killcoyne_repro/original/<key>.png, panels/kcf_<key>_{cn,he,comb,ours}.png (copied from the cluster), captions in PAGES.
Outputs: paper/one_paper/killcoyne_repro/kcf_<key>_4way.png (300 dpi) and killcoyne_4way.pdf (one page per figure, caption under each)."""
import os, textwrap, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt; from matplotlib.backends.backend_pdf import PdfPages; from PIL import Image
D = "/Users/zuberi01/Documents/thesis/paper/one_paper/killcoyne_repro"; PAN = D + "/panels"; ORIG = D + "/original"
import json; CAP = json.load(open(D + "/captions.json"))   # key -> {"title": ..., "caption": ..., "orig": [original keys]}
def page(key, spec):
    origs = [Image.open(f"{ORIG}/{k}.png") for k in spec["orig"]]
    ours = [(lab, f"{PAN}/kcf_{key}_{s}.png") for lab, s in (("(2) Copy number, our data", "cn"), ("(3) H&E only", "he"), ("(4) H&E + copy number", "comb"))]
    ours = [(lab, f) for lab, f in ours if os.path.exists(f)]
    if not ours: ours = [("(2) Our data", f"{PAN}/kcf_{key}_ours.png")]
    fig = plt.figure(figsize=(16, 12.6) if len(ours) == 3 else (16, 8.4))
    if len(ours) == 3: boxes = [(0.01, 0.53, 0.48, 0.42), (0.51, 0.53, 0.48, 0.42), (0.01, 0.07, 0.48, 0.42), (0.51, 0.07, 0.48, 0.42)]
    else: boxes = [(0.01, 0.12, 0.48, 0.80), (0.51, 0.12, 0.48, 0.80)]
    # original panel(s): stack vertically if more than one
    ax = fig.add_axes(boxes[0]); ax.axis("off")
    if len(origs) == 1: im = origs[0]
    else:
        W = max(o.width for o in origs); im = Image.new("RGB", (W, sum(o.height for o in origs)), "white"); yy = 0
        for o in origs: im.paste(o, (0, yy)); yy += o.height
    ax.imshow(im); ax.set_title("(1) Killcoyne et al. 2020, original (internal comparison only)", fontsize=11, loc="left")
    for b, (lab, f) in zip(boxes[1:], ours):
        ax = fig.add_axes(b); ax.axis("off"); ax.imshow(Image.open(f)); ax.set_title(lab, fontsize=11, loc="left")
    fig.suptitle(spec["title"], fontsize=13, x=0.01, ha="left", y=0.995)
    fig.text(0.01, 0.005, "\n".join(textwrap.wrap(spec["caption"], 190)), fontsize=9.5, va="bottom", ha="left")
    fn = f"{D}/kcf_{key}_4way.png"; fig.savefig(fn, dpi=300); return fig
with PdfPages(D + "/killcoyne_4way.pdf") as pdf:
    for key, spec in CAP.items():
        fig = page(key, spec); pdf.savefig(fig, dpi=150); plt.close(fig); print("page", key)
