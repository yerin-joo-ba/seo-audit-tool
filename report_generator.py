import os
import pandas as pd
from urllib.parse import urlparse
import json

def generate_html_report(ticket_name, urls, final_df, alt_df, output_path):
    """
    HTML 템플릿과 외부 CSS, JS 파일 내용을 읽어와 하나의 독립적인 HTML 파일로 생성합니다.
    """
    length_check_rows = ["Title", "Description", "OG Title", "OG Description"]
    
    # 1. 템플릿, CSS, JS 파일 내용 읽기
    try:
        # 이 스크립트가 실행되는 위치를 기준으로 templates 폴더의 경로를 설정합니다.
        script_dir = os.path.dirname(__file__)
        def read_file(file_name):
            with open(os.path.join(script_dir, "templates", file_name), "r", encoding="utf-8") as f:
                return f.read()

        template = read_file("report_template.html")
        report_css = read_file("report_style.css")
        # sheetjs.min.js 파일도 읽어옵니다.
        try:
            sheetjs_js = read_file("sheetjs.min.js")
        except FileNotFoundError:
            sheetjs_js = "alert('Excel 내보내기 기능에 필요한 sheetjs.min.js 파일을 templates 폴더에서 찾을 수 없습니다.');"
        report_js = read_file("report_script.js")

    except FileNotFoundError as e:
        print(f"오류: {e.filename} 파일을 찾을 수 없습니다.")
        print("프로젝트 폴더에 templates 폴더와 그 안의 파일들이 모두 있는지 확인해주세요.")
        return

    # 2. 탭 버튼 HTML 생성
    tab_buttons_html = ""
    for i, url in enumerate(urls):
        # URL에서 마지막 경로를 탭 이름으로 사용
        path_segment = urlparse(url).path.strip('/')
        tab_name = path_segment.split('/')[-1] or urlparse(url).hostname
        tab_buttons_html += f"<button class='tab-button' title='{url}' onclick='showTab({i})'>{tab_name}</button>\n"

    # 3. 탭 콘텐츠 HTML 생성
    tab_contents_html = ""
    for i, url in enumerate(urls):
        active_class = "active" if i == 0 else ""
        tab_contents_html += f"<div id='urlContent_{i}' class='tab-content {active_class}'>\n"
        
        # SEO QA 테이블
        tab_contents_html += "<h3>SEO QA</h3>\n"
        tab_contents_html += "<table class='seo-table'><thead><tr><th>항목</th><th style='width:30%'>현황</th><th class='len-col'>길이</th><th style='width:22%'>Comment</th><th style='width:auto'>SEO 수정안</th><th class='len-col'>길이</th></tr></thead><tbody>\n"
        
        url_df = final_df[final_df["URL"] == url]
        for _, row in url_df.iterrows():
            factor = row.get('항목', '')
            현황 = "" if pd.isna(row.get("현황")) else str(row["현황"])
            현황_길이 = "" if pd.isna(row.get("현황_길이")) else str(row["현황_길이"])
            comment = "" if pd.isna(row.get("Comment")) else str(row["Comment"])
            seo_fix = "" if pd.isna(row.get("SEO 수정안")) else str(row["SEO 수정안"])
            
            is_length_row = factor in length_check_rows
            comment_status = "ok" if str(comment).lower().strip() in ['이슈 없음', 'n/a', ''] else 'issue'
            editable_status = " contenteditable='true'" if factor == "통이미지 사용" else ""

            tab_contents_html += "<tr>\n"
            tab_contents_html += f"  <td class='factor-name'>{factor}</td>\n"
            
            # 현황 및 현황-길이 칸 처리
            if is_length_row:
                tab_contents_html += f"  <td><div class='editable-field'>{현황}</div></td>\n"
                tab_contents_html += f"  <td class='len-col'>{현황_길이}</td>\n"
            else:
                if editable_status:
                    tab_contents_html += f"  <td colspan='2'><div class='editable-field'{editable_status}>{현황}</div></td>\n"
                else:
                    tab_contents_html += f"  <td colspan='2'>{현황}</td>\n"
            
            # Comment 칸 처리
            tab_contents_html += f"  <td class='comment-cell' data-status='{comment_status}'><div class='editable-field' contenteditable='true'>{comment}</div></td>\n"
            
            # SEO 수정안 및 SEO 수정안-길이 칸 처리
            if is_length_row:
                tab_contents_html += f"  <td class='fix-cell'><div class='editable-field' contenteditable='true'>{seo_fix}</div></td>\n"
                tab_contents_html += f"  <td class='len-col len-counter-fix'>0자</td>\n"
            else:
                tab_contents_html += f"  <td class='fix-cell' colspan='2'><div class='editable-field' contenteditable='true'>{seo_fix}</div></td>\n"
            tab_contents_html += "</tr>\n"
        tab_contents_html += "</tbody></table>\n"
        
        # Alt Text 테이블
        alt_data_for_current_url = alt_df[alt_df["Page URL"] == url]
        if not alt_data_for_current_url.empty:
            tab_contents_html += "<h3>Image Alt QA</h3>\n"
            tab_contents_html += "<table class='alt-table'><thead><tr><th style='width:25%'>Image URL</th><th>Preview</th><th style='width:20%'>Alt Text (AS-IS)</th><th class='sortable' style='width:15%'>SEO Comment <i class='sort-icon'>&#8597;</i></th><th>Alt Text (To-Be)</th></tr></thead><tbody>\n"
            for _, alt_row in alt_data_for_current_url.iterrows():
                image_url = "" if pd.isna(alt_row.get("Image URL")) else str(alt_row["Image URL"])
                alt_asis = "" if pd.isna(alt_row.get("Alt Text (AS-IS)")) else str(alt_row["Alt Text (AS-IS)"])
                default_alt_comment = "이슈 없음" if alt_asis.strip() else "수정 필요"
                default_alt_to_be = "N/A" if alt_asis.strip() else ""
                comment_status = "ok" if default_alt_comment == '이슈 없음' else 'issue'

                tab_contents_html += f"""
                <tr>
                    <td>{image_url}</td>
                    <td><img src="{image_url}" alt="Image Preview"></td>
                    <td>{alt_asis}</td>
                    <td class='comment-cell' data-status='{comment_status}'><div class='alt-comment-toggle'>{default_alt_comment}</div></td>
                    <td><div class='editable-field' contenteditable='true'>{default_alt_to_be}</div></td>
                </tr>
                """
            tab_contents_html += "</tbody></table>\n"
        
        tab_contents_html += "</div>\n"

    # 4. 템플릿에 모든 데이터와 코드 주입
    final_html = template.replace("{{TICKET_NAME}}", ticket_name)
    final_html = final_html.replace("{{TAB_BUTTONS}}", tab_buttons_html)
    final_html = final_html.replace("{{TAB_CONTENTS}}", tab_contents_html)
    
    # 외부 파일을 링크하는 대신, 파일 내용을 직접 삽입
    final_html = final_html.replace('<link rel="stylesheet" href="report_style.css" />', f"<style>{report_css}</style>")
    final_html = final_html.replace('<script src="sheetjs.min.js"></script>', f"<script>{sheetjs_js}</script>")
    final_html = final_html.replace('<script src="report_script.js"></script>', f"<script>{report_js}</script>")

    # 5. 최종 HTML 파일 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)