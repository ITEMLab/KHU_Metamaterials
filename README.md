# KHU_Metamaterials

메타물질 관련 공부 자료와 실험/코드 결과를 한곳에 모아둔 저장소입니다. 
## 빠른 길잡이

- **코드를 보고 싶으면** → `VideoMetamaterials_Code/`
- **생성 결과/시각화 결과를 보고 싶으면** → `VideoMetamaterials_Result/`
- **개인 정리 문서** → 저장소 루트의 한국어 문서 파일들
- **실행 시작점** → `VideoMetamaterials_Code/main.py`

### 루트 문서 설명

#### `데이터셋 생성 설명서.pdf`
- 논문 기반 메타물질 데이터셋을 어떻게 생성하는지 단계별로 풀어쓴 설명 문서입니다.
- 무작위 geometry 패턴 생성 → 이진화 → 유효성 검사 → 대칭 복사까지의 파이프라인을 정리.
- 후반부에는 Abaqus 코드에서 geometry를 part로 변환하는 과정과 mesh/edge/node 구성 아이디어도 함께 설명.

#### `메타물질 정리자료_이진영.pptx`
- 메타물질 전반을 개괄하는 입문 발표자료입니다.
- 기계적 메타물질의 분류, stiffness 기반 메타물질, micro/nano lattice, chiral / anti-chiral 구조 같은 대표 개념을 정리

#### `협업미팅자료_이진영.pptx`
- 비선형 기계 메타물질 inverse design 프로젝트의 실제 진행 상황과 이슈를 정리한 미팅 자료입니다.
- 실측 데이터셋 학습 후의 preliminary result, target response 대비 생성 결과, compression test와 hyperelastic coefficient 추정 이슈를 적었습니다.


## 폴더 구조

```text
KHU_Metamaterials/
├─ VideoMetamaterials_Code/ # 메인 코드, 설정, 보조 스크립트, 예시 결과
├─ VideoMetamaterials_Result/ # 학습/추론 후 생성된 결과물
├─ *.pdf / *.pptx # 공부/정리 문서, 발표자료, 참고자료
└─ README.md # 현재 문서
```

---

## 1. `VideoMetamaterials_Code/`

비디오 기반 메타물질 생성/역설계를 위한 핵심 코드 폴더입니다. 기존 공개 연구 코드(비디오 diffusion 기반 메타물질 설계)를 중심으로, 실행 스크립트와 Abaqus 평가 스크립트, 시각화 파일이 같이 들어 있습니다.

### 안에서 먼저 볼 파일

#### `README.md`
- 원본 프로젝트 설명 문서입니다.
- 논문 링크, 데이터 다운로드 위치, 기본 실행 방법, Abaqus 평가 방법이 들어 있습니다.
- **이 프로젝트의 배경을 가장 먼저 이해하려면 이 파일부터 보는 게 좋습니다.**

#### `main.py`
- 이 저장소의 **메인 실행 진입점**입니다.
- 현재 코드상 기본 동작은:
 - 기존 체크포인트를 불러와
 - target stress-strain curve 기준으로
 - 샘플을 생성하는 `eval_only=True` 모드입니다.
- 주요 사용자 입력:
 - `eval_only`
 - `run_name`, `load_run_name`
 - `load_model_step`
 - `num_preds`
 - `guidance_scale`
- 즉, **실제로 모델을 돌릴 때 가장 먼저 수정하게 될 파일**입니다.

#### `model.yaml`
- 모델/학습 설정 파일입니다.
- 배치 크기, learning rate, diffusion timestep, attention 관련 설정, reference frame 등이 들어 있습니다.
- 구조를 빠르게 이해하려면 `main.py`와 같이 보는 게 좋습니다.

#### `target_responses.csv`
- 조건으로 넣는 target stress-strain response 데이터입니다.
- 원하는 응답 곡선으로 조건을 바꾸려면 이 파일을 수정하면 됩니다.

### 하위 폴더 설명

#### `src/`
- 공통 유틸리티 코드가 들어 있습니다.
- 현재 확인된 핵심 파일:
 - `normalization.py`: 데이터 정규화 관련 로직
 - `utils.py`: 보조 함수 모음

#### `denoising_diffusion_pytorch/`
- diffusion 모델 구현부입니다.
- 사실상 모델 핵심 로직이 들어 있는 폴더로 보면 됩니다.
- 네트워크 구조와 sampling/training 관련 코드가 이쪽에 있습니다.

#### `abaqus/`
- Abaqus CAE 평가용 보조 코드입니다.
- 주요 파일:
 - `abaqus_script.py`
 - `abq_utils.py`
- 생성된 geometry를 실제 FEM으로 검증할 때 참고하면 됩니다.

#### `runs/`
- 학습 결과/불러온 결과 저장 경로 입니다.


### 보조 스크립트 설명

#### `eval_abaqus.py`
- 생성된 샘플을 Abaqus로 평가하는 래퍼 스크립트입니다.
- geometry 예측 결과를 FEM 결과와 비교할 때 사용합니다.

#### `batch_eval.py`
- 여러 결과를 한 번에 평가할 때 쓰는 배치 실행 스크립트로 보입니다.

#### `create_dataset.py`
- 학습용 데이터셋 생성/전처리용 스크립트입니다.

#### `create_geo.py`
- geometry 생성 또는 geometry 관련 후처리 스크립트입니다.

#### `gif_visualization.py`
- raw gif 결과를 보기 좋은 형태로 정리하는 시각화 스크립트입니다.

#### `change_alpha.py`
- 시각화/이미지 처리 관련 보조 스크립트로 보입니다.

#### `autoRun.bat`
- Windows에서 eval_abaqus.py 파일을 반복 실행 하기 위한 배치 파일입니다.

### 참고 이미지/문서

- `pred_light.gif`, `pred_dark.gif`
- `target_responses_stress_strain.png`
- `target_responses_stress_strain_subplots.png`
- `target_00_07_vs_4_predictions_grid.png`
- `Videometamaterial settings.pdf`
- 기타 PDF 자료

이 파일들은 **논문식 결과 예시나 설정 참고자료**로 보면 됩니다.

---

## 2. `VideoMetamaterials_Result/`

실행 결과를 모아둔 폴더입니다.


- `step_200000/` 내부에 다음 자료들이 있습니다.
 - `geometries.csv`
 - `gifs/`
 - stress-strain 비교 이미지들

### 안에서 볼 것

#### `geometries.csv`
- 생성된 메타물질 geometry 정보가 저장된 파일입니다.

#### `gifs/`
- 생성 결과 시각화 gif 모음입니다.

#### `target_vs_predicted_stress_strain_*`
- 목표 응답과 예측 응답 비교 그림들입니다.


## 처음 보는 사람에게 추천하는 읽는 순서

### 연구 배경을 먼저 알고 싶은 경우
1. 루트의 PDF/PPTX 자료 확인
2. `VideoMetamaterials_Code/README.md`
3. `VideoMetamaterials_Result/`의 결과 gif/plot 확인

### 코드를 먼저 이해하고 싶은 경우
1. `VideoMetamaterials_Code/README.md`
2. `VideoMetamaterials_Code/main.py`
3. `VideoMetamaterials_Code/model.yaml`
4. `VideoMetamaterials_Code/src/`
5. 필요 시 `abaqus/`, `eval_abaqus.py`

### 결과만 빠르게 보고 싶은 경우
1. `VideoMetamaterials_Result/step_200000/gifs/`
2. `target_vs_predicted_stress_strain_*`
3. `geometries.csv`

---

## 실행/재현 시 참고

현재 코드 구조상 완전한 재현에는 아래가 필요할 가능성이 큽니다.

- Python 3.11 계열 환경
- PyTorch / Accelerate 등 diffusion 실행 의존성
- 학습/추론용 데이터셋
- 필요 시 Abaqus 라이선스 및 실행 환경

자세한 의존성은 `VideoMetamaterials_Code/README.md`와 `model.yaml` 기준으로 확인하면 됩니다.
