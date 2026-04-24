import numpy as np, os
from abaqus.abq_utils import generate_geometry

N_SAMPLES          = 4928
PIXELS             = 96 // 2          
GRF_ALPHA          = 6
PIXEL_THRESH_REL   = 0.1
GRF_THRESH_REL     = 0.5
SAVE_DIR           = "grf_samples/"
os.makedirs(SAVE_DIR, exist_ok=True)
csv_path = os.path.join(SAVE_DIR, "geometries_val.csv")

with open(csv_path, "w") as f:
    for i in range(N_SAMPLES):
        geom = generate_geometry(GRF_ALPHA, PIXELS,
                                 PIXEL_THRESH_REL, GRF_THRESH_REL)
        np.savetxt(f, geom.reshape(1, -1), delimiter=",",
                   fmt="%d")
