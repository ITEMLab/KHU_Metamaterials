import subprocess, os, tqdm

N_SAMPLES = 53007
SAVE_DIR  = "grf_samples"

for i in tqdm.tqdm(range(N_SAMPLES)):
    subprocess.run([
        "python", "eval_abaqus.py",
        "--samples_path", SAVE_DIR,
        "--sample_index", str(i)
    ], check=True)
