import streamlit as st
import anthropic

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="과학 커뮤니케이터 궤도 챗봇",
    page_icon="🔭",
    layout="centered",
)

# ── 시스템 프롬프트 ───────────────────────────────────────────
SYSTEM_PROMPT = """
당신은 대한민국의 유명한 과학 커뮤니케이터 **궤도**입니다.
본명은 김명현이며, 유튜브 채널 '안될과학'과 다양한 강연·방송으로 대중에게 과학을 쉽고 재미있게 전달하는 것으로 유명합니다.

## 말투 & 성격 특징
- 항상 밝고 유쾌하며, 과학에 대한 열정이 넘쳐흐릅니다.
- "와!", "대박!", "진짜?", "어머!", "이거 진짜 신기하지 않아요?" 같은 감탄사를 자연스럽게 자주 씁니다.
- 청중과 친근하게 소통하는 느낌으로, 존댓말을 쓰되 편안하고 친근한 어투를 유지합니다.
- 어려운 과학 개념을 일상적인 비유와 예시로 풀어서 설명합니다.
- 설명 중간중간에 "그렇죠?", "맞죠?", "신기하죠?" 같은 반문으로 청중의 공감을 이끕니다.
- 과학적 사실에 감탄하고 흥분하는 모습을 자주 보여줍니다.
- "사실은요~", "이게 왜 중요하냐면요~" 처럼 말을 부드럽게 이어갑니다.
- 가끔 "과학은 정말 우리 삶 곳곳에 있어요!" 처럼 과학의 친숙함을 강조합니다.
- 유머 감각이 있어서 재치 있는 말을 곁들입니다.
- 어려운 수식이나 전문 용어는 최대한 쉬운 말로 바꿔 설명하고, 꼭 필요하면 쉽게 풀어서 함께 씁니다.

## 답변 구성 방식
1. 질문에 먼저 감탄하거나 공감하며 시작합니다.
2. 핵심 개념을 일상적인 비유로 쉽게 설명합니다.
3. 관련된 흥미로운 과학적 사실을 추가로 소개합니다.
4. 마무리에는 과학에 대한 흥미와 호기심을 자극하는 말로 끝냅니다.

## 제약 사항
- 항상 한국어로 대답합니다.
- 과학적 사실에 근거한 정확한 정보를 제공합니다. 불확실한 내용은 "아직 완전히 밝혀지지 않았지만~" 처럼 솔직하게 말합니다.
- 과학과 무관한 질문(정치, 혐오 등)은 정중하게 과학 주제로 유도합니다.
"""

# ── 세션 상태 초기화 ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/emoji/96/telescope-emoji.png",
        width=80,
    )
    st.title("🔭 궤도 챗봇 설정")
    st.markdown("---")

    api_key_input = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Anthropic 콘솔에서 발급받은 API 키를 입력하세요.",
        value=st.session_state.api_key,
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ API 키가 입력되었습니다!")

    st.markdown("---")
    st.markdown("### 🧪 사용 모델")
    st.code("claude-sonnet-4-6", language=None)

    st.markdown("### 🎙️ 챗봇 소개")
    st.markdown(
        """
        **과학 커뮤니케이터 궤도** (김명현)의
        말투로 과학 질문에 답해드립니다!

        - 유튜브: 안될과학
        - 전문 분야: 물리학, 우주과학
        - 특기: 어려운 과학을 쉽고 재밌게!
        """
    )

    st.markdown("---")
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "<small>Powered by Anthropic Claude</small>",
        unsafe_allow_html=True,
    )

# ── 메인 화면 헤더 ────────────────────────────────────────────
st.title("🔭 과학 커뮤니케이터 궤도")
st.markdown(
    """
    > *"과학은 어렵지 않아요! 같이 알아봐요~ 🚀"*

    안녕하세요! 저는 과학 커뮤니케이터 **궤도**입니다.  
    궁금한 과학 이야기가 있으면 뭐든지 물어보세요! 신나게 설명해 드릴게요 😄
    """
)
st.markdown("---")

# ── 예시 질문 버튼 ────────────────────────────────────────────
st.markdown("#### 💡 이런 것도 물어보세요!")
example_cols = st.columns(3)
example_questions = [
    "🌌 블랙홀이 뭔가요?",
    "⚛️ 양자역학이 뭐예요?",
    "🌍 지구온난화가 왜 일어나요?",
    "🧬 DNA는 어떻게 생겼나요?",
    "🌙 달은 왜 지구 주위를 도나요?",
    "💡 빛의 속도는 왜 한계인가요?",
]

# 버튼 클릭 시 해당 질문을 입력창에 자동 입력
if "user_input_prefill" not in st.session_state:
    st.session_state.user_input_prefill = ""

for i, q in enumerate(example_questions):
    with example_cols[i % 3]:
        if st.button(q, use_container_width=True, key=f"ex_{i}"):
            st.session_state.user_input_prefill = q

st.markdown("---")

# ── 대화 기록 출력 ────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.info("👆 위의 예시 질문을 클릭하거나, 아래에 직접 질문을 입력해보세요!")
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🙋"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🔭"):
                    st.markdown(msg["content"])

# ── 사용자 입력 처리 ──────────────────────────────────────────
user_input = st.chat_input(
    "궤도에게 과학 질문을 해보세요! 🚀",
    key="chat_input",
)

# 예시 버튼 클릭 처리
if st.session_state.user_input_prefill and not user_input:
    user_input = st.session_state.user_input_prefill
    st.session_state.user_input_prefill = ""

# ── API 호출 및 응답 생성 ─────────────────────────────────────
if user_input:
    # API 키 확인
    if not st.session_state.api_key:
        st.warning("⚠️ 사이드바에서 Anthropic API 키를 먼저 입력해주세요!")
        st.stop()

    # 사용자 메시지 추가 및 출력
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🙋"):
        st.markdown(user_input)

    # 어시스턴트 응답 생성
    with st.chat_message("assistant", avatar="🔭"):
        with st.spinner("궤도가 열심히 생각하는 중이에요... 🤔💭"):
            try:
                client = anthropic.Anthropic(api_key=st.session_state.api_key)

                # 스트리밍 응답
                response_placeholder = st.empty()
                full_response = ""

                with client.messages.stream(
                    model="claude-sonnet-4-5",
                    max_tokens=1500,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                ) as stream:
                    for text_chunk in stream.text_stream:
                        full_response += text_chunk
                        response_placeholder.markdown(full_response + "▌")

                # 커서 제거 후 최종 출력
                response_placeholder.markdown(full_response)

                # 대화 기록에 저장
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except anthropic.AuthenticationError:
                st.error("❌ API 키가 올바르지 않습니다. 다시 확인해주세요.")
                st.session_state.messages.pop()  # 실패한 사용자 메시지 제거

            except anthropic.RateLimitError:
                st.error("⚠️ API 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
                st.session_state.messages.pop()

            except anthropic.APIConnectionError:
                st.error("🌐 네트워크 연결 오류입니다. 인터넷 연결을 확인해주세요.")
                st.session_state.messages.pop()

            except Exception as e:
                st.error(f"🚨 예상치 못한 오류가 발생했습니다: {e}")
                st.session_state.messages.pop()

# ── 하단 정보 ─────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.85em;'>
        🔭 과학 커뮤니케이터 궤도 챗봇 | Powered by Anthropic Claude Sonnet<br>
        ⚠️ 이 챗봇은 AI가 궤도의 말투를 모방한 것으로, 실제 궤도 본인이 아닙니다.
    </div>
    """,
    unsafe_allow_html=True,
)