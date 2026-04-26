import streamlit as st
import qrcode
from PIL import Image
import io

st.set_page_config(page_title="QR Code Generator", page_icon="🏷️", layout="centered")

st.title("🏷️ Product QR Code Generator")
st.write("Generate QR codes containing only the **Product ID** for faster and more accurate scanning.")

product_id = st.text_input("Enter Product ID (e.g., 1, 2, 3)", value="1")

if st.button("Generate QR Code"):
    if product_id.strip():
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(product_id.strip())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.image(byte_im, caption=f"QR Code for Product ID: {product_id.strip()}")
        
        st.download_button(
            label="Download QR Code",
            data=byte_im,
            file_name=f"product_{product_id.strip()}_qr.png",
            mime="image/png"
        )
    else:
        st.error("Please enter a valid Product ID.")
