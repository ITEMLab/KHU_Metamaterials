import os
import os.path
import numpy as np
from abaqus.abq_utils import *
from pathlib import Path
import imageio
import argparse
import shutil
import subprocess
	 

def main(args):
    samples_path = Path(args.samples_path).resolve()
    sample_index = args.sample_index
    out_root = Path(args.out_dir).resolve() if args.out_dir is not None else samples_path
    create_gifs = True
    gif_reference_frame = args.gif_reference_frame
    
    assert (samples_path / 'geometries.csv').is_file(), 'geometries.csv not found in samples_path'

    sample_grf = False # use to sample random grf instead of given geometry

    pixels = 96//2 # since we only consider one quarter

    # grf sampling properties
    if sample_grf:
        grf_alpha = 6
        pixel_threshold_rel = 0.1
        grf_threshold_rel = 0.5
        grf_geometry = generate_geometry(grf_alpha, pixels, pixel_threshold_rel, grf_threshold_rel)
        samples_path = Path('grf_sample').resolve()
        out_root = samples_path
        sample_index = 0    
        os.makedirs(samples_path, exist_ok=True)
        np.savetxt(samples_path / 'geometries.csv', grf_geometry, delimiter=',')

    out_root.mkdir(parents=True, exist_ok=True)
    if out_root != samples_path:
        shutil.copy2(samples_path / 'geometries.csv', out_root / 'geometries.csv')

    # change dir to abaqus_path to store abaqus output more conveniently
    abaqus_path = out_root / 'abaqus_eval_sample_{}'.format(sample_index)
    original_dir = Path.cwd()
    os.makedirs(abaqus_path, exist_ok=True)
    os.chdir(abaqus_path)

    script_path = original_dir / 'abaqus' / 'abaqus_script.py'
    rel_samples_path = os.path.relpath(out_root, abaqus_path)

    if create_gifs:
        store_frames = True
    else:
        store_frames = False

    try:
        subprocess.run([
            'abaqus',
            'cae',
            f'noGUI={script_path}',
            '--',
            '--samples_path', rel_samples_path,
            '--sample_index', str(sample_index),
            '--store_frames', str(store_frames),
            '--pixels', str(pixels),
        ], check=True)
        print('abaqus simulation finished')
    finally:
        os.chdir(original_dir)

    if create_gifs:
        csv_dir = abaqus_path / 'csv'
        if (csv_dir / 'geometry_frames_eul.csv').is_file(): # check if abaqus evaluation was successful
            gif_pixels = int(2*pixels)
            if gif_reference_frame == 'eulerian':
                geom_frames = np.genfromtxt(csv_dir / 'geometry_frames_eul.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                s_mises_frames = np.genfromtxt(csv_dir / 's_mises_frames_eul.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                s_22_frames = np.genfromtxt(csv_dir / 's_22_frames_eul.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                strain_energy_frames = np.genfromtxt(csv_dir / 'strain_energy_dens_frames_eul.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)

                # convert data to uint8 and store scaling
                max_s_mises = np.max(s_mises_frames)
                min_s_22 = np.min(s_22_frames)
                max_s_22 = np.max(s_22_frames)
                max_strain_energy = np.max(strain_energy_frames)
                frame_range = np.array([max_s_mises, min_s_22, max_s_22, max_strain_energy])
                frame_range_header = ['max_s_mises', 'min_s_22', 'max_s_22', 'max_strain_energy']

                # rescale data to [0,1]
                if not frame_range.any() == 0:
                    s_mises_frames = s_mises_frames / max_s_mises
                    s_22_frames = (s_22_frames - min_s_22) / (max_s_22 - min_s_22)
                    strain_energy_frames = strain_energy_frames / max_strain_energy

                geom_frames = (geom_frames * 255).astype(np.uint8)
                s_mises_frames = (s_mises_frames * 255).astype(np.uint8)
                s_22_frames = (s_22_frames * 255).astype(np.uint8)
                strain_energy_frames = (strain_energy_frames * 255).astype(np.uint8)

                # stack all frames at the end for consistent gif creation
                full_frames = np.stack((geom_frames, s_mises_frames, s_22_frames, strain_energy_frames), axis=-1).astype(np.uint8)

            elif gif_reference_frame == 'lagrangian':
                    
                u_1_frames = np.genfromtxt(csv_dir / 'u_1_frames_lagr.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                u_2_frames = np.genfromtxt(csv_dir / 'u_2_frames_lagr.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                s_mises_frames = np.genfromtxt(csv_dir / 's_mises_frames_lagr.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                s_22_frames = np.genfromtxt(csv_dir / 's_22_frames_lagr.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)
                strain_energy_frames = np.genfromtxt(csv_dir / 'strain_energy_dens_frames_lagr.csv', delimiter=',').reshape(-1,gif_pixels,gif_pixels)

                # convert data to uint8 and store scaling
                min_u_1 = np.min(u_1_frames)
                max_u_1 = np.max(u_1_frames)
                min_u_2 = np.min(u_2_frames)
                max_u_2 = np.max(u_2_frames)
                max_s_mises = np.max(s_mises_frames)
                min_s_22 = np.min(s_22_frames)
                max_s_22 = np.max(s_22_frames)
                max_strain_energy = np.max(strain_energy_frames)
                frame_range = np.array([min_u_1, max_u_1, min_u_2, max_u_2, max_s_mises, min_s_22, max_s_22, max_strain_energy])
                frame_range_header = ['min_u_1', 'max_u_1', 'min_u_2', 'max_u_2', 'max_s_mises', 'min_s_22', 'max_s_22', 'max_strain_energy']

                # rescale data to [0,1]
                if not frame_range.any() == 0:
                    u_1_frames = (u_1_frames - min_u_1) / (max_u_1 - min_u_1)
                    u_2_frames = (u_2_frames - min_u_2) / (max_u_2 - min_u_2)
                    s_mises_frames = s_mises_frames / max_s_mises
                    s_22_frames = (s_22_frames - min_s_22) / (max_s_22 - min_s_22)

                u_1_frames = (u_1_frames * 255).astype(np.uint8)
                u_2_frames = (u_2_frames * 255).astype(np.uint8)
                s_mises_frames = (s_mises_frames * 255).astype(np.uint8)
                s_22_frames = (s_22_frames * 255).astype(np.uint8)

                # stack all frames at the end for consistent gif creation
                full_frames = np.stack((u_1_frames, u_2_frames, s_mises_frames, s_22_frames), axis=-1).astype(np.uint8)

            no_frames = 11
            gif_save_dir = abaqus_path / 'gif'
            os.makedirs(gif_save_dir, exist_ok=True)
            for j in range(0, full_frames.shape[-1]):
                images = []
                for k in range(no_frames):
                    images.append(full_frames[k,:,:,j])            
                imageio.mimsave(gif_save_dir / ('prediction_channel_' + str(j) + '.gif'), images, duration=0.2)

            np.savetxt(gif_save_dir / 'frame_range.csv', np.array([frame_range]), delimiter=',', comments='', header=','.join(frame_range_header))
            print('gif creation successful')
        else:
            print('gif creation not successful')

def get_cli_args():
    parser = argparse.ArgumentParser(
        description="Batch-evaluate geometries with Abaqus and export GIF/CSV results."
    )

    parser.add_argument(
        "--samples_path",
        type=str,
        default="grf_sample",
        help="폴더 경로 (geometries.csv·출력 서브폴더 위치)"
    )

    parser.add_argument(
        "--sample_index",
        type=int,
        default=0,
        help="geometries.csv에서 평가할 행(index)"
    )

    parser.add_argument(
        "--out_dir",
        type=str,
        default=None,
        help="선택: 결과를 저장할 최상위 폴더. 생략하면 samples_path 아래에 저장"
    )

    parser.add_argument(
        "--material",
        type=str,
        default="DefaultMaterial",
        help="현재 스크립트에서는 사용되지 않는 예약 인자"
    )

    parser.add_argument(
        "--gif_reference_frame",
        type=str,
        default="eulerian",
        choices=["eulerian", "lagrangian"],
        help="저장할 GIF 기준 프레임"
    )

    # 필요 시 추가 파라미터 선언 …
    return parser.parse_args()

if __name__ == "__main__":
    args = get_cli_args()
    main(args)
