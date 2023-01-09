
# iOS Symbolicate Tool

## 사용 목적
ios 크래시발생시 단말기에 남게되는 ips로그파일을 symbolicate 하여 크래시를 발생한 소스 코드의 라인 수를 확인 가능하다

## 다운로드
앱형태는 사이닝 문제때문에 더이상 지원불가. 레포지터리 클론후에 파이썬3로 실행한다. 

## 실행 준비
- 터미널을 열어 sh StartSymbolicateTool.sh 혹은 python3 iosSymbolcateMain.py 입력한다.
- pyQT6 라이브러리가 필요하므로 설치가 되지 않은 경우 python -m pip install pyQt6 로 pyQt6 를 설치해 준다.
- pyinstaller가 catalina이후 권한설정이 변경되어 pyinstaller로 만든 앱이 제대로 실행 되지 않아 추후 python이 아닌 native앱으로 변경 계획중

## 사용 방법
- 크래시가 발생한 단말기에서 로그파일인 ips파일을 가져온다. 파일 가져오는 법은 아래 하단의 IPS 파일 가져오는 법을 참고한다. 
- 각 리전별 빌드머신(a.k.a FTP서버) 로부터 아래 그림과 같이 dsym파일을 다운로드 한다.
- ips경로에 해당로그파일을 지정한후 symbolicate 버튼을 누르면 파일명_output파일이 생성된다.
- symbolicate시 ips파일양식이 최근에 변경되어서 포맷이 맞지않는경우가있는데(IPS file format need to convert) 이 경우에는 Convert IPS버튼을 누르면 자동으로 파일을 컨버트하고 ips경로를 바뀐파일로 바꿔준다. 이후 다시 symbolicate를 누르면된다. 

## IPS 파일 가져오는 법
- 설정-개인정보보호-분석 및 향상-분석데이터에서 로그데이터를 볼 수 있다.
- 인하우스 빌드의 경우 inhouse~로시작하는 로그를 찾아서 공유하여 저장한다.