# SEO Audit Automation Tool (SEO 감사 자동화 툴)

반복적인 SEO 감사(Audit) 작업을 자동화하고, 수정 및 공유가 용이한 동적 HTML 리포트를 생성하는 Python GUI 애플리케이션입니다.
엑셀 및 정적 HTML 리포트로 내보내기 기능을 지원합니다.

<br>

## 🖼️ 스크린샷

![audit tool 실행](assets/image.png?v=2)

![Report 1](assets/image-1.png?v=2)

![Report 2](assets/image-2.png?v=2)

<br>

## ✨ 주요 기능 (Features)

- **Tkinter 기반 GUI**: 사용자가 쉽게 URL 목록과 티켓명을 입력하고 감사를 실행할 수 있는 직관적인 인터페이스를 제공합니다.
- **SEO 핵심 요소 자동 분석**:
  - Title, Description, H1, Canonical 태그 등의 기본 메타 데이터를 수집합니다.
  - Open Graph 및 Twitter Card 태그를 분석합니다.
  - 페이지 내 Broken Link(손상된 링크)를 검사합니다.
  - XML 사이트맵 내 URL 포함 여부를 확인합니다.
- **이미지 Alt Text 진단**: 페이지 내 모든 이미지의 Alt Text 현황을 리포트에 포함하여 SEO 개선점을 제안합니다.
- **동적 HTML 리포트 생성**:
  - 분석 결과를 웹 브라우저에서 바로 확인할 수 있습니다.
  - 리포트 내에서 Comment와 SEO 수정안을 직접 수정하고 정적 파일로 다시 내보낼 수 있습니다.
  - 여러 URL 감사 시, 탭으로 구분하여 결과를 보여줍니다.

<br>

## 🛠️ 사용 기술 (Tech Stack)

- **Language**: Python
- **GUI**: Tkinter
- **Web Scraping**: `requests`, `BeautifulSoup4`
- **Data Handling**: `pandas`
- **Reporting**: `jinja2` (HTML 템플릿), `sheetjs` (Excel 내보내기)
- **Deployment**: `PyInstaller`

<br>

## ⚙️ 설치 및 실행 방법

1.  **저장소 클론**
    ```bash
    git clone [https://github.com/yerin-joo-ba/SEO_Tools.git](https://github.com/yerin-joo-ba/SEO_Tools.git)
    cd YourRepoName
    ```

2.  **필요 라이브러리 설치**
    ```bash
    pip install -r requirements.txt
    ```

3.  **프로그램 실행**
    ```bash
    python main_app.py
    ```

<br>

## 📂 프로젝트 구조

- `main_app.py`: 메인 GUI 애플리케이션의 레이아웃과 이벤트 처리를 담당합니다.
- `seo_core.py`: 실제 웹사이트를 크롤링하고 SEO 데이터를 분석하는 핵심 로직을 포함합니다. **(※ 본 포트폴리오 저장소에서는 제외됨)**
- `report_generator.py`: 분석된 데이터를 바탕으로 최종 HTML 리포트를 생성합니다.
- `sitemap_management.py`: 사이트맵 URL 매핑 데이터를 관리(로드/저장)합니다.
- `utils.py`: 브랜드/국가 코드 추출, Alt Text 수집 등 보조 유틸리티 함수를 포함합니다.
- `templates/`: HTML, CSS, JS 템플릿 파일들을 보관합니다.

<br>

## ⚠️ 중요

본 포트폴리오용 저장소에는 실제 웹사이트를 분석하는 핵심 로직이 담긴 **`seo_core.py` 파일은 제외**되어 있습니다. 이 프로젝트는 프로그램의 전체적인 구조, GUI 구현, 데이터 처리 및 리포트 생성 방식을 보여주기 위함입니다.
