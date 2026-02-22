import streamlit as st
from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance

# -------------------------------
# Streamlit UI Setup
# -------------------------------
st.set_page_config(page_title="Local Image Effects", layout="centered")

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <h1 style="color:#1E3A8A;">Local Image Effects</h1>
        <h4 style="color:#475569;">Upload a photo and apply effects — no account or credentials needed</h4>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, use_container_width=True, caption="Original")

    with col2:
        effect = st.selectbox(
            "Choose effect",
            ["None", "Grayscale", "Blur", "Sharpen", "Contrast", "Brightness", "Small (256px)"],
        )

        if effect == "None":
            result = image
        elif effect == "Grayscale":
            result = image.convert("L").convert("RGB")
        elif effect == "Blur":
            result = image.filter(ImageFilter.GaussianBlur(radius=5))
        elif effect == "Sharpen":
            result = image.filter(ImageFilter.SHARPEN)
        elif effect == "Contrast":
            result = ImageEnhance.Contrast(image).enhance(1.5)
        elif effect == "Brightness":
            result = ImageEnhance.Brightness(image).enhance(1.2)
        else:  # Small
            result = image.resize((256, 256))

        st.image(result, use_container_width=True, caption=effect)

    # Download button
    buf = BytesIO()
    result.save(buf, format="PNG")
    st.download_button("Download result", data=buf.getvalue(), file_name="result.png", mime="image/png")
