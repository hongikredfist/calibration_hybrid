# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🤖 Claude Code를 위한 업데이트 가이드라인

**대상**: Claude Code (AI 개발 어시스턴트)
**목적**: 새 세션마다 작업 컨텍스트 복원, 개발 가이드라인 제공

**업데이트 규칙** (사용자가 ".md 문서를 각각 작성 규칙에 맞게 업데이트 해줘" 요청 시):
1. **"📍 현재 작업 상태"** 섹션 업데이트
   - 어느 Phase인지
   - 어떤 파일을 작업 중인지
   - 완료된 작업 체크

2. **"🎯 다음 작업"** 섹션 업데이트
   - 바로 다음에 해야 할 작업
   - 완료 조건
   - 예상 파일명

3. **"📝 개발 중 발견사항"** 섹션에 추가
   - 발견한 이슈
   - 내린 설계 결정
   - 변경된 데이터 포맷
   - 주의사항

4. **"✅ 완료된 작업"** 섹션에 추가
   - 완료한 Phase/파일
   - 주요 기능
   - 파일 위치

**절대 변경하지 말 것**: "🛠️ Development Philosophy", "🏗️ System Architecture" (핵심 원칙)

---

## 🎯 Project Identity

**calibration_hybrid** - Unity-Python Hybrid Parameter Calibration System for PIONA

- **PIONA**: Pedestrian Intelligence for Oriented Navigation Architecture (보행 시뮬레이션)
- **목표**: Unity 시뮬레이션 파라미터를 실제 데이터에 맞게 자동 최적화
- **전략**: Unity(시뮬레이션) + Python(최적화/분석) 분리 아키텍처

---

## 🏗️ System Architecture

```
Unity (시뮬레이션)  ←→  Python (최적화)
     ↓                      ↓
 JSON/CSV              파라미터 생성
```

**워크플로우**: Python 파라미터 생성 → Unity 시뮬레이션 → Python 결과 평가 → 반복

---

## 🛠️ Development Philosophy

### ✅ DO
- **수동 검증 가능한 개별 모듈** 작성
- **단일 스크립트**로 독립 실행 가능하게
- **각 단계별 안정성 확인** 후 다음 단계
- **필요한 것만** 만들기
- 간결하고 명확한 코드

### ❌ DON'T
- 처음부터 완전 자동화 시도
- 복잡한 클래스 구조 만들기
- 불필요한 기능 추가
- 볼륨 증가시키기

---

## 📍 현재 작업 상태

**현재 Phase**: Phase 1 진행 중
**현재 작업**: Unity → Python 데이터 파이프라인 구축
**작업 중인 파일**: Unity OutputManager (완료), Python loader (예정)

### 완료 항목
- [x] 프로젝트 초기화
- [x] README.md 작성 (사용자 대상)
- [x] CLAUDE.md 작성 (Claude Code 대상)
- [x] 개발 계획 수립
- [x] data/input, data/output 디렉토리 생성
- [x] Unity OutputManager 구현 (`Calibration_hybrid_OutputManager.cs`)
  - 18 SFM 파라미터 수집
  - 에이전트별 오차 데이터 수집
  - JSON 파일 저장

### 미완료 항목
- [ ] Phase 1: `load_simulation_results.py` 구현
- [ ] Phase 1: Unity 시뮬레이션 실행 후 Python 로드 테스트
- [ ] Phase 2: `evaluate_objective.py` 구현
- [ ] Phase 3: `generate_parameters.py`, `export_to_unity.py` 구현
- [ ] Phase 4: `run_optimization.py` 구현

---

## 🎯 다음 작업

### 즉시 해야 할 작업
1. **Python 로더 스크립트** 작성: `load_simulation_results.py`
   - Unity 저장 JSON 파일 읽기
   - 데이터 구조 확인 및 출력
   - 파일 위치: 프로젝트 루트

2. **Unity 시뮬레이션 실행** 후 테스트
   - StreamingAssets/Calibration/Output/simulation_result.json 생성 확인
   - Python으로 파일 로드 테스트

### Phase 1 완료 조건
- Unity에서 JSON 파일 생성 성공
- Python에서 JSON 파일 읽기 성공
- 파라미터 18개, 에이전트 오차 데이터 확인

### 예상 출력 경로
- Unity: `D:\UnityProjects\META_VERYOLD_P01_s\Assets\StreamingAssets\Calibration\Output\simulation_result.json`
- Python: 위 경로에서 직접 읽거나 `data/output/`로 복사

---

## 📁 Project Structure

```
calibration_hybrid/
├── data/
│   ├── input/          # Unity가 읽을 파라미터 (Python → Unity)
│   └── output/         # Unity 시뮬레이션 결과 (Unity → Python)
├── dev/                # 개발 중인 스크립트
├── archive/            # deprecated 코드
├── .venv/              # Python 가상환경
├── README.md           # 프로젝트 개요 및 사용법 (사람 대상)
└── CLAUDE.md           # (이 파일) Claude Code 개발 가이드
```

---

## 🚀 Development Roadmap

### Phase 1: 데이터 파이프라인 검증 (👈 현재 단계)
- **목표**: Unity ↔ Python 데이터 교환 확인
- **파일**: `load_simulation_results.py`
- **완료 조건**: Unity 출력 파일을 Python에서 정상적으로 읽고 내용 출력

### Phase 2: Objective Function 구현
- **목표**: 시뮬레이션 결과 정량적 평가
- **파일**: `evaluate_objective.py`
- **완료 조건**: 시뮬레이션 결과에 대한 정량적 평가 점수 산출

### Phase 3: 최적화 알고리즘 연결
- **목표**: 파라미터 생성 및 변환
- **파일**: `generate_parameters.py`, `export_to_unity.py`
- **완료 조건**: 수동으로 최적화 루프 1회 완전 순환

### Phase 4: 자동화
- **목표**: 전체 워크플로우 자동 실행
- **파일**: `run_optimization.py`
- **완료 조건**: 사용자 개입 없이 N회 최적화 반복 실행

---

## 📝 개발 중 발견사항

### 이슈 및 결정사항
*(작업 진행하면서 여기에 추가)*

**예시**:
- 2025-01-XX: Unity 결과 파일 포맷을 JSON으로 결정 (CSV보다 중첩 구조 표현 용이)
- 2025-01-XX: 목적함수는 3가지 메트릭 가중 평균으로 결정

### 데이터 포맷 결정
*(Unity-Python 간 데이터 포맷이 결정되면 여기에 기록)*

**Unity → Python** (시뮬레이션 결과):
```json
// 추후 정의
```

**Python → Unity** (파라미터):
```json
// 추후 정의
```

### 주의사항
*(개발 중 발견한 주의사항)*

---

## ✅ 완료된 작업

### 초기 설정
- **README.md**: 사용자 대상 프로젝트 사용법 문서 작성
- **CLAUDE.md**: Claude Code 대상 개발 가이드 작성
- **개발 계획**: 4단계 Phase 계획 수립

*(이후 완료된 작업들을 여기에 추가)*

---

## 💻 Python Environment

### Activation
```bash
# Windows
.venv\Scripts\activate

# Unix/Mac
source .venv/bin/activate
```

### Dependencies (현재 상태)
- Python 3.10+
- 추후 추가: NumPy, Pandas, Scipy (requirements.txt 생성 예정)

---

## 🔍 Important Conventions

### Data Format
- **Unity → Python**: JSON 또는 CSV (시뮬레이션 결과)
- **Python → Unity**: JSON 또는 CSV (파라미터 설정)

### File Locations
- Unity 출력: `data/output/`
- Unity 입력: `data/input/`
- 개발 스크립트: 프로젝트 루트 또는 `dev/`

### Gitignore
- `data/` - 데이터 파일 (git 추적 안함)
- `archive/` - deprecated 코드 (git 추적 안함)
- `.venv/` - Python 가상환경

---

## 🎓 Context for New Sessions

### 새 Claude Code 세션 시작 시 체크리스트:

1. **"📍 현재 작업 상태"** 확인
   - 어느 Phase인지
   - 어떤 파일 작업 중인지
   - 완료/미완료 항목

2. **"🎯 다음 작업"** 확인
   - 바로 해야 할 작업
   - 완료 조건

3. **"📝 개발 중 발견사항"** 확인
   - 이전 세션에서 발견한 이슈
   - 내린 설계 결정

4. **"🛠️ Development Philosophy"** 숙지
   - 수동 검증 우선
   - 단순하고 독립적인 스크립트
   - 필요한 것만 만들기

5. **작업 시작 전 확인**
   - README.md의 "현재 상태" 체크리스트 확인
   - 해당 Phase의 완료 조건 확인

---

## 🔧 Development Tips

### 코딩 스타일
- 각 스크립트는 독립적으로 실행 가능
- argparse로 명령줄 인자 처리
- 간단한 사용 예시 docstring 포함
- 복잡한 클래스보다 함수 중심

### 테스트 접근법
- Phase 1: 샘플 JSON/CSV로 로드 테스트
- Phase 2: 여러 결과 파일로 목적함수 값 비교
- Phase 3: 수동으로 1회 전체 루프 실행
- Phase 4: 자동화 파이프라인 검증

### 문서 업데이트
- Phase 완료 시 README.md의 체크리스트 업데이트
- CLAUDE.md의 "📍 현재 작업 상태", "✅ 완료된 작업" 업데이트
- 새로운 발견사항은 "📝 개발 중 발견사항"에 추가

---

## 🚨 Critical Reminders

1. **단순함 유지**: 복잡한 구조 금지
2. **단계별 검증**: 각 Phase 완료 조건 충족 확인
3. **수동 우선**: 자동화는 마지막 단계에서만
4. **독립 실행**: 각 스크립트는 단독으로 실행 가능해야 함
5. **볼륨 관리**: 불필요한 코드 생성 금지

---

## 📚 Additional Resources

- **README.md**: 전체 시스템 개요, 워크플로우, 사용법 (사람 대상)
- **Unity 프로젝트**: PIONA 시뮬레이션 (별도 위치, 추후 명시)
- **실제 데이터**: ATC 궤적 데이터 (추후 명시)
- to memorize: 1. 앞으로 너가 작성해주는 모든 코드, 이미지, 그래프, 파일 등 모든 output은 영어로만 작성해줬으면 좋겠어. 2. .md 파일을 제외한 모든 파일(특히 코드 작성)을 작업할 때 이모지를 쓰지마.