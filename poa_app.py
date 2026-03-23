import streamlit as st
from openai import OpenAI

# ==========================================
# 🛑 站长后台配置区 (安全加密版)
# ==========================================
# 这里的 sk-xxx 已经被彻底锁死，真实密钥将填在 Streamlit Cloud 后台的 Secrets 中
MY_API_KEY = st.secrets["MY_API_KEY"] 
MY_BASE_URL = st.secrets["MY_BASE_URL"] 
SECRET_CODE = st.secrets["SECRET_CODE"] 

# ==========================================
# 1. 网页基础配置与状态初始化
# ==========================================
st.set_page_config(page_title="跨境救星 - AI 申诉信生成器", page_icon="⚖️", layout="centered")

# 初始化：使用次数、是否已解锁
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0
if 'is_unlocked' not in st.session_state:
    st.session_state.is_unlocked = False

# 顶端引流横幅
st.info("💡 站长福利：联系左侧微信名片，即可【免费获取】无限次使用激活码！")

st.title("⚖️ 跨境救星：亚马逊 AI 申诉信专家")
st.markdown("只需三步，自动生成符合亚马逊官方审核逻辑的高通过率英文 Plan of Action (POA)。")

# ==========================================
# 2. 侧边栏：名片置顶与激活 (左侧)
# ==========================================
# --- 顶部：名片与加群 ---
st.sidebar.header("🎁 联系站长免费获取激活码")
st.sidebar.write("加群/领内测码请加V：**15645178095**") 

try:
    # 这里放你的个人名片 wechat.jpg
    st.sidebar.image("wechat.jpg", caption="加好友备注：领激活码", use_container_width=True)
except FileNotFoundError:
    st.sidebar.info("📷 提示：缺少 wechat.jpg 图片")

st.sidebar.markdown("---")

# --- 中部：激活码解锁 ---
st.sidebar.header("🔑 激活码解锁")
if st.session_state.is_unlocked:
    st.sidebar.success("✅ 尊享会员：已解锁无限次生成！")
else:
    input_code = st.sidebar.text_input("在此输入激活码", type="password", help="扫描上方名片加微信免费领取")
    if input_code == SECRET_CODE:
        st.session_state.is_unlocked = True
        st.sidebar.success("✅ 解锁成功！")
        st.rerun()

st.sidebar.markdown("---")

# --- 底部：收款区 ---
st.sidebar.header("💰 快速充值")
st.sidebar.warning("💡 前 2 次免费。以后每用一次需支付 **9.9 元**（或联系站长加群免费领码）。")
try:
    # 这里放你的收款码 pay.jpg
    st.sidebar.image("pay.jpg", caption="扫码支付 9.9 元/次", use_container_width=True)
except FileNotFoundError:
    st.sidebar.info("📷 提示：缺少 pay.jpg 图片")


# ==========================================
# 3. 主界面表单 (覆盖 10 大核心痛点)
# ==========================================
st.subheader("📝 填写案件详情")
reason = st.selectbox(
    "1. 请选择店铺被封/审核的核心原因：", 
    [
        "水电账单二审 (Utility Bill Verification)", 
        "消费者法案验证 (Consumer Inform Act)", 
        "儿童玩具/合规性/TIC审核 (Compliance/TIC Audit)", 
        "危险品/锂电池合规审核 (Hazmat/Battery)", 
        "视频面试/法人身份验证 (Identity/Video Verification)", 
        "被诉知识产权/版权侵权 (IP/Copyright Infringement)", 
        "商品真伪性/真实性申诉 (Product Authenticity)", 
        "品牌滥用/品牌移除申诉 (Brand Abuse)", 
        "欧洲站 KYC/受益人审核 (EU KYC Audit)", 
        "二手当新品售卖投诉 (Used Sold as New)"
    ]
)

details = st.text_area("2. 用中文描述你的实际情况与委屈：", placeholder="描述越具体，生成的POA通过率越高。例如：虽然是房东账单但有租赁合同...")

st.markdown("---")

# ==========================================
# 4. 生成逻辑：带引流文案的按钮
# ==========================================
# 判定是否可以生成
can_generate = st.session_state.is_unlocked or (st.session_state.usage_count < 2)

if not can_generate:
    st.error("🛑 您的免费额度已用完！")
    st.info("👉 请联系左侧边栏站长微信，免费领取激活码解锁。")
    st.button("🚀 联系站长免费获取激活码解锁", disabled=True)
else:
    # 动态按钮文案：如果没解锁，就提示还剩几次+免费领码
    if st.session_state.is_unlocked:
        btn_label = "🚀 一键生成 (尊享无限次模式)"
    else:
        btn_label = f"🚀 一键生成 (剩 {2 - st.session_state.usage_count} 次免费) | 联系站长免费获取激活码"
    
    if st.button(btn_label):
        if not details:
            st.warning("请详细描述你的情况！")
        else:
            with st.spinner("🧠 跨境法务 AI 正在为您撰写专业申诉信..."):
                try:
                    # 初始化客户端，从 secrets 读取配置
                    client = OpenAI(api_key=MY_API_KEY, base_url=MY_BASE_URL)
                    
                    prompt = f"""
                    你现在是亚马逊申诉专家。
                    审核原因：{reason}。
                    客户情况：{details}。
                    请根据最新政策，按 Root Cause, Actions, Prevention 三段式输出一封专业、诚恳、有逻辑的英文 POA。
                    直接输出正文，不要有任何开场白。
                    """
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat", # 这里可以根据实际使用的模型修改
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    # 只有未解锁时才累加次数
                    if not st.session_state.is_unlocked:
                        st.session_state.usage_count += 1
                    
                    st.success("🎉 生成成功！")
                    st.markdown("### 📄 Plan of Action (POA)")
                    st.info(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"❌ 请求失败，可能是接口余额不足。报错：{e}")

# 底部声明
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("© 2026 跨境救星 - 联系站长获取更多运营黑科技")