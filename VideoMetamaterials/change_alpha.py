import os
from PIL import Image
from tqdm import tqdm

# 1. 토폴로지 데이터가 있는 경로를 지정하세요.
# (사용자분의 에러 로그에 있던 경로를 기준으로 작성했습니다)
target_folder = './data/lagrangian/validation/gifs/topo'  # 실제 경로 확인 필요

def force_save_as_fake_gif(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.gif')]
    print(f"총 {len(files)}개의 파일을 처리합니다...")
    
    for filename in tqdm(files):
        file_path = os.path.join(folder_path, filename)
        
        try:
            with Image.open(file_path) as img:
                # 1. L 모드(찐 흑백)로 변환
                gray_img = img.convert('L')
                
                # 2. [핵심] 포맷은 'PNG'로 강제 지정하고, 이름은 그대로(.gif) 덮어씌움
                # PNG는 L 모드를 완벽하게 지원합니다.
                gray_img.save(file_path, format='PNG')
                
        except Exception as e:
            print(f"에러: {filename} - {e}")

    print("변환 완료.")

if __name__ == "__main__":
    if os.path.exists(target_folder):
        force_save_as_fake_gif(target_folder)
        
        # 검증
        sample_file = os.listdir(target_folder)[0]
        test_img = Image.open(os.path.join(target_folder, sample_file))
        print(f"\n최종 검증 ({sample_file}):")
        print(f"이미지 포맷: {test_img.format} (PNG여야 성공)")
        print(f"이미지 모드: {test_img.mode} (L이어야 성공)")
    else:
        print("경로를 확인해주세요.")