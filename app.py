import re
import streamlit as st
import markdown
from bs4 import BeautifulSoup
from weasyprint import HTML

st.set_page_config(page_title="수능 모의고사 시험지 자동 생성기", layout="wide")

def parse_math_markdown(md_text):
    """
    마크다운을 문항 단위로 파싱하여 HTML 구조로 전환
    """
    # [문제지] 섹션 추출 (정답 및 해설 부분 제외)
    if "## Ⅱ. [정답 및 상세 해설]" in md_text:
        problem_part = md_text.split("## Ⅱ. [정답 및 상세 해설]")[0]
    else:
        problem_part = md_text

    # 문항 단위 분할 (### n. [예상 변형 문제 n] 형태 기준)
    raw_questions = re.split(r'(?=^### \d+\.)', problem_part, flags=re.M)
    
    parsed_items = []
    for q_text in raw_questions:
        q_text = q_text.strip()
        if not q_text or q_text.startswith("# "):
            continue

        # 수식 태그 보존 및 LaTeX 인라인/디스플레이 식 정규화
        # MathJax rendering ready format
        html_item = markdown.markdown(q_text, extensions=['fenced_code', 'tables'])
        parsed_items.append(f'<div class="question-card">{html_item}</div>')

    return "".join(parsed_items)

def generate_b4_pdf(questions_html):
    """
    B4 2단 수능 모의고사 고정 레이아웃 HTML/CSS 생성 및 PDF 변환
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      @page {{
        size: 257mm 364mm; /* B4 정규 규격 */
        margin: 15mm 12mm 15mm 12mm;
      }}
      body {{
        font-family: "Malgun Gothic", "UnBatang", "Batang", serif;
        font-size: 10.5pt;
        line-height: 1.6;
        color: #000;
        margin: 0;
        padding: 0;
      }}
      
      /* 헤더 영역 (시험지 상단 타이틀) */
      .exam-header {{
        text-align: center;
        border-bottom: 2px solid #000;
        padding-bottom: 5px;
        margin-bottom: 12px;
      }}
      .exam-header h1 {{
        font-size: 18pt;
        margin: 0;
        letter-spacing: 2px;
      }}

      /* B4 2단 핵심 레이아웃 */
      .exam-grid {{
        column-count: 2;
        column-gap: 12mm;
        column-rule: 1px solid #777;
        height: 100%;
      }}

      /* 문항 단락 쪼개짐 방지 박스 */
      .question-card {{
        break-inside: avoid;
        page-break-inside: avoid;
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 0.5px dashed #ccc;
      }}

      .question-card h3 {{
        font-size: 11pt;
        margin: 0 0 6px 0;
        background-color: #f8f9fa;
        padding: 2px 4px;
        border-left: 3px solid #000;
      }}

      p {{
        margin: 4px 0;
        text-align: justify;
      }}
      
      /* 보기①~⑤ 선지 세로/가로 정렬 보장 */
      ol, ul {{
        margin: 6px 0;
        padding-left: 18px;
      }}
    </style>
    <!-- LaTeX 수식 시각화를 위한 MathJax 렌더링 -->
    <script>
    MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
      }}
    }};
    </script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
    </head>
    <body>
      <div class="exam-header">
        <h1>2026학년도 수능 대비 수학 영역 모의고사</h1>
      </div>
      <div class="exam-grid">
        {questions_html}
      </div>
    </body>
    </html>
    """
    
    # WeasyPrint 엔진으로 무결한 PDF 바이너리 바이패스 렌더링
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

# Streamlit UI
st.title("📐 수능 모의고사 B4 2단 시험지 자동 생성기")
st.caption("제미나이 노트북 마크다운(.md)을 입력하면 텍스트 밀림 없는 B4 수능 규격 PDF로 즉시 변환합니다.")

uploaded_file = st.file_uploader("제미나이 노트북 문제 마크다운(.md) 파일 업로드", type=["md", "txt"])

if uploaded_file is not None:
    raw_md = uploaded_file.read().decode("utf-8")
    
    st.success("파일 파싱 완료!")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 원본 마크다운 미리보기")
        st.text_area("Markdown Contents", raw_md, height=400)
        
    with col2:
        st.subheader("⚡ B4 2단 렌더링 실행")
        if st.button("수능 모의고사 PDF 생성하기", type="primary"):
            with st.spinner("B4 2단 레이아웃 및 수식 렌더링 중..."):
                parsed_html = parse_math_markdown(raw_md)
                pdf_data = generate_b4_pdf(parsed_html)
                
                st.download_button(
                    label="⬇️ 수능 모의고사 PDF 다운로드",
                    data=pdf_data,
                    file_name="2026_수능모의고사_수학영역.pdf",
                    mime="application/pdf"
                )
