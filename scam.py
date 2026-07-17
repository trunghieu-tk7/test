import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai  # Thư viện chuẩn mới nhất từ năm 2026 của Google

# Tải API Key từ file .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Cho phép file index.html truy cập dữ liệu liên cổng mạng (CORS)

# Khởi tạo Client Gemini mới.
# Hệ thống sẽ tự động đọc biến môi trường GEMINI_API_KEY trong file .env của bạn.
client = genai.Client()

@app.route("/api/check", methods=["POST"])
def check_scam():
    try:
        # Nhận dữ liệu tin nhắn từ giao diện gửi lên
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dữ liệu không hợp lệ"}), 400
            
        user_content = data.get("content", "")
        if not user_content.strip():
            return jsonify({"error": "Nội dung tin nhắn trống"}), 400

        # Cấu trúc Prompt chuyên gia để AI trả về câu trả lời phân tách rõ ràng
        prompt = (
            f"Bạn là chuyên gia an ninh mạng phân tích tin nhắn lừa đảo thuộc dự án ScamCheck.\n"
            f"Hãy phân tích và đánh giá mức độ tin cậy của tin nhắn sau đây:\n"
            f"\"\"\"\n{user_content}\n\"\"\"\n\n"
            f"Yêu cầu phản hồi bằng tiếng Việt ngắn gọn, rõ ràng và chia cụ thể thành 3 phần:\n"
            f"1. CHẤM ĐIỂM NGHI NGỜ: [Nêu rõ mức độ Thấp / Trung bình / Cao]\n"
            f"2. DẤU HIỆU VI PHẠM: [Liệt kê ngắn gọn bằng các gạch đầu dòng các điểm bất thường như link lạ, hối thúc, giả mạo cơ quan...]\n"
            f"3. HƯỚNG DẪN XỬ LÝ: [Đưa ra 1-2 câu lời khuyên hành động thiết thực cho người dùng]"
        )

        # Gọi mô hình gemini-1.5-flash tối ưu tốc độ thông qua SDK mới
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )

        # Trả kết quả văn bản phân tích về cho giao diện index.html
        return jsonify({"result": response.text})

    except Exception as e:
        # Trả về mã lỗi chi tiết nếu có sự cố xảy ra ở Backend
        return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500

if __name__ == "__main__":
    # Ép đọc cổng do Render cấp tự động
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)