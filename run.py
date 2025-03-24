#!/usr/bin/env python
import os
import subprocess
import sys
import platform
import venv
from pathlib import Path

def create_venv(venv_path):
    """가상환경 생성"""
    print(f"가상환경 생성 중... ({venv_path})")
    venv.create(venv_path, with_pip=True)
    return venv_path

def get_venv_activate_command(venv_path):
    """운영체제에 맞는 가상환경 활성화 명령어 반환"""
    if platform.system() == "Windows":
        return str(Path(venv_path) / "Scripts" / "activate.bat")
    else:
        return f"source {Path(venv_path) / 'bin' / 'activate'}"

def install_requirements(venv_path):
    """필요한 패키지 설치"""
    print("필요한 패키지 설치 중...")
    
    # 운영체제에 맞는 pip 경로 결정
    if platform.system() == "Windows":
        pip_path = str(Path(venv_path) / "Scripts" / "pip")
    else:
        pip_path = str(Path(venv_path) / "bin" / "pip")
    
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])

def run_app():
    """Streamlit 앱 실행"""
    print("기업가치 평가계산기 실행 중...")
    
    # 현재 작업 디렉토리를 스크립트 위치로 변경
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 가상환경 경로 설정
    venv_path = Path("venv")
    
    # 가상환경이 없으면 생성
    if not venv_path.exists():
        create_venv(venv_path)
        install_requirements(venv_path)
    
    # 운영체제에 맞는 streamlit 실행 파일 경로 결정
    if platform.system() == "Windows":
        streamlit_path = str(venv_path / "Scripts" / "streamlit")
    else:
        streamlit_path = str(venv_path / "bin" / "streamlit")
    
    # Streamlit 앱 실행
    subprocess.call([streamlit_path, "run", "app.py"])

if __name__ == "__main__":
    run_app() 