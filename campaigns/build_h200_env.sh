set -e
source ~/miniforge3/etc/profile.d/conda.sh
conda create -n erin_h200 python=3.10 -y -q
conda activate erin_h200
pip install -q torch --index-url https://download.pytorch.org/whl/cu124
pip install -q timm h5py openslide-python openslide-bin numpy pandas pillow
python -c "import torch, timm, openslide, h5py; print(\x27env ok\x27, torch.__version__)"
