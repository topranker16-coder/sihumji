import streamlit as st
import json
import os
import streamlit.components.v1 as components

# 페이지 설정 (와이드 모드)
st.set_page_config(page_title="수능 수학 시험지 자동 생성기", layout="wide")

st.title("🎓 수능 수학 시험지 자동 생성기")
st.markdown("원하는 문제 수를 선택하고, 우측 상단의 **[PDF로 저장 / 인쇄하기]** 버튼을 눌러 B4 PDF로 바로 저장하세요.")

# 1. JSON 데이터 로드
DATA_FILE = "questions.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        all_questions = json.load(f)
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다. GitHub 저장소를 확인해주세요.")
    all_questions = []

# 2. 사이드바 설정 (출제 문항 수 조절)
st.sidebar.header("⚙️ 시험지 설정")
max_q = len(all_questions)
if max_q > 0:
    selected_count = st.sidebar.slider("출제할 문제 수", min_value=1, max_value=max_q, value=min(4, max_q))
else:
    selected_count = 0

exam_title = st.sidebar.text_input("시험지 제목", "2022학년도 대학수학능력시험 문제지")
subject_name = st.sidebar.text_input("과목명", "수학 영역")
exam_type = st.sidebar.selectbox("형태", ["홀수형", "짝수형"])

# 선택된 문제만큼 자르기
target_questions = all_questions[:selected_count]

# 3. HTML 템플릿 생성 함수 (인쇄 버튼 포함)
def generate_exam_html(questions, title, subject, type_str):
    pages = [questions[i:i + 4] for i in range(0, len(questions), 4)]
    total_pages = len(pages) if pages else 1
    
    pages_html = ""
    
    for page_idx, page_q in enumerate(pages):
        page_num = page_idx + 1
        q_boxes = ""
        for q in page_q:
            q_boxes += f'''
            <div class="q-box">
              <div>
                <span class="q-title">{q["number"]}.</span> {q["body"]} <span class="q-score">[{q["score"]}점]</span>
              </div>
              <div class="q-choices">
                <span>① {q["choices"][0]}</span>
                <span>② {q["choices"][1]}</span>
                <span>③ {q["choices"][2]}</span>
                <span>④ {q["choices"][3]}</span>
                <span>⑤ {q["choices"][4]}</span>
              </div>
            </div>
            '''
        
        pages_html += f'''
        <div class="paper">
          <div class="header">
            <div class="header-top">
              <div class="header-title">{title}</div>
              <div class="header-page-num">{page_num}</div>
            </div>
            <div class="header-mid">
              <div class="badge-period">제 2 교시</div>
              <div class="header-subject">{subject}</div>
              <div class="badge-type">{type_str}</div>
            </div>
          </div>

          <div class="badge-choice-wrap">
            <div class="badge-choice">5지선다형</div>
          </div>

          <div class="grid-container">
            {q_boxes}
          </div>

          <div class="footer">
            <div class="page-box">{page_num} / {total_pages}</div>
            <div>이 문제지에 관한 저작권은 한국교육과정평가원에 있습니다.</div>
          </div>
        </div>
        '''

    full_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
  @page {{
    size: 257mm 364mm;
    margin: 12mm 15mm 10mm 15mm;
  }}
  body {{
    font-family: "Batang", "KoPubBatang", "바탕", serif;
    margin: 0; padding: 0; background-color: #333; color: #000;
  }}
  /* 상단 고정 인쇄 버튼 스타일 */
  .no-print {{
    position: fixed; top: 15px; right: 25px; z-index: 9999;
    background: #007bff; color: white; border: none; padding: 12px 20px;
    font-size: 14pt; font-weight: bold; border-radius: 8px; cursor: pointer;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
  }}
  .no-print:hover {{ background: #0056b3; }}

  .paper {{
    width: 227mm; height: 338mm; margin: 15mm auto; background: #fff;
    box-sizing: border-box; display: flex; flex-direction: column;
    justify-content: space-between; position: relative; padding: 12mm 15mm 10mm 15mm;
    box-shadow: 0 0 15px rgba(0,0,0,0.5); page-break-after: always;
  }}
  .header {{
    border-bottom: 2px solid #000; padding-bottom: 2mm; margin-bottom: 3mm; position: relative;
  }}
  .header-top {{ position: relative; text-align: center; height: 10mm; }}
  .header-title {{ font-size: 20pt; font-weight: 900; letter-spacing: -1px; font-family: "Batang", "바탕", serif; display: inline-block; }}
  .header-page-num {{ position: absolute; right: 2mm; top: -2mm; font-size: 28pt; font-weight: bold; font-family: "Batang", "바탕", serif; line-height: 1; }}
  .header-mid {{ display: flex; justify-content: space-between; align-items: center; margin-top: 1mm; position: relative; }}
  .badge-period {{ border: 2px solid #000; border-radius: 14px; padding: 1px 12px; font-size: 13pt; font-weight: bold; font-family: "Batang", "바탕", serif; }}
  .header-subject {{ position: absolute; left: 50%; transform: translateX(-50%); font-size: 32pt; font-weight: 900; letter-spacing: 6px; font-family: "Batang", "바탕", serif; }}
  .badge-type {{ border: 2.5px solid #000; border-radius: 4px; padding: 2px 8px; font-size: 15pt; font-weight: 900; font-family: "Batang", "바탕", serif; }}
  .badge-choice-wrap {{ margin-top: 2mm; margin-bottom: 2mm; }}
  .badge-choice {{ display: inline-block; border: 1.5px solid #000; padding: 2px 10px; font-size: 10.5pt; font-weight: bold; font-family: "Dotum", "돋움", sans-serif; letter-spacing: 2px; }}
  .grid-container {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 8mm 10mm; height: 280mm; position: relative; }}
  .grid-container::before {{ content: ""; position: absolute; left: 50%; top: -4mm; bottom: -6mm; width: 1.5px; background-color: #000; transform: translateX(-50%); }}
  .q-box {{ padding: 2mm 4mm; box-sizing: border-box; display: flex; flex-direction: column; justify-content: flex-start; font-size: 10.5pt; line-height: 1.7; word-break: keep-all; }}
  .q-title {{ font-weight: bold; font-size: 11pt; font-family: "Dotum", "돋움", sans-serif; }}
  .q-score {{ font-weight: normal; font-size: 9.5pt; }}
  .q-choices {{ display: flex; justify-content: space-between; margin-top: 5mm; padding-left: 1mm; padding-right: 1mm; }}
  .footer {{ position: relative; padding-top: 3mm; display: flex; justify-content: flex-end; align-items: center; font-size: 8pt; font-family: "Dotum", "돋움", sans-serif; color: #444; }}
  .page-box {{ position: absolute; left: 50%; top: -4mm; transform: translateX(-50%); background-color: #fff; border: 1px solid #000; padding: 1px 6px; font-size: 9pt; font-weight: bold; font-family: "Dotum", "돋움", sans-serif; color: #000; }}

  /* 인쇄 시 버튼 숨기기 및 배경 깔끔하게 처리 */
  @media print {{
    .no-print {{ display: none; }}
    body {{ background: none; }}
    .paper {{ box-shadow: none; margin: 0; }}
  }}
</style>
</head>
<body>

<button class="no-print" onclick="window.print()">🖨️ PDF로 저장 / 인쇄하기</button>

{pages_html}

<script>
  if (window.MathJax) {{
      MathJax.typeset();
  }}
</script>
</body>
</html>
'''
    return full_html

# 4. 화면 출력
if target_questions:
    st.subheader(f"📄 미리보기 (총 {len(target_questions)}문제 선택됨)")
    exam_html_code = generate_exam_html(target_questions, exam_title, subject_name, exam_type)
    
    # Streamlit 내에 HTML 렌더링 (높이 넉넉하게 설정)
    components.html(exam_html_code, height=1200, scrolling=True)
else:
    st.warning("선택된 문제가 없습니다.")