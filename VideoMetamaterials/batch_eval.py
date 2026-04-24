import pandas as pd, subprocess, csv, os, tqdm
from pathlib import Path

GEOM_CSV   = "grf_samples/geometries.csv"
OUT_ROOT   = Path("data_new/training")
GIF_DIRS   = ["topo", "s_22", "u_1", "u_2", "s_mises", "ener"]
SS_CSV     = OUT_ROOT / "stress_strain_data.csv"
FR_CSV     = OUT_ROOT / "frame_range_data.csv"

# 1) CSV 헤더 준비
with open(SS_CSV, "w", newline="") as f:
    writer = csv.writer(f); writer.writerow(["id"] + [f"s{i}" for i in range(11)])
with open(FR_CSV, "w", newline="") as f:
    writer = csv.writer(f); writer.writerow(["id","start","end"])

# 2) 각 샘플 반복
geom_df = pd.read_csv(GEOM_CSV, header=None)
for idx in tqdm.tqdm(range(len(geom_df))):
    # (a) eval_abaqus 실행
    subprocess.run([
        "python", "eval_abaqus.py",
        "--sample_index", str(idx),
        "--out_dir", OUT_ROOT,        # eval_abaqus 수정 필요
        "--material", "MyMaterial"    # 선택 옵션
    ], check=True)

    # (b) eval_abaqus 가 out_dir/stress_strain_curve.csv 저장했다고 가정
    #     해당 파일을 읽어 master CSV 에 append
    sscurve = pd.read_csv(OUT_ROOT / f"tmp_{idx}/stress_strain_curve.csv", header=None).values.squeeze()
    with open(SS_CSV, "a", newline="") as f:
        csv.writer(f).writerow([idx] + list(sscurve))

    # (c) frame range 정보 예: 항상 0~10 프레임이면
    with open(FR_CSV, "a", newline="") as f:
        csv.writer(f).writerow([idx, 0, 10])

    # (d) GIF 파일을 gifs/*/ 아래로 이동
    for sub in GIF_DIRS:
        os.rename(OUT_ROOT / f"tmp_{idx}/{sub}.gif", OUT_ROOT / "gifs" / sub / f"{idx}.gif")

    # (e) 임시 폴더 정리
    ...

# 3) min_max_values.csv 계산
import numpy as np, glob
all_curves = np.loadtxt(SS_CSV, delimiter=",", skiprows=1)[:,1:]
np.savetxt(OUT_ROOT/"min_max_values.csv",
           np.vstack([all_curves.min(axis=0), all_curves.max(axis=0)]),
           delimiter=",")
