# برای این کار، می‌توانیم از پردازش تصویر و کتابخانه OpenCV استفاده کنیم. ابتدا باید ویدئو را فریم به فریم پردازش کنیم، سپس موقعیت عقربه را در هر فریم تشخیص دهیم و حرکت آن را محاسبه کنیم. در اینجا یک نمونه کد پایتون برای شروع کار ارائه می‌دهم:

import cv2
import numpy as np

def detect_needle(frame):
    # تبدیل تصویر به سیاه و سفید
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # اعمال فیلتر برای کاهش نویز
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # تشخیص لبه‌ها
    edges = cv2.Canny(blurred, 50, 150)
    
    # یافتن خطوط با استفاده از تبدیل هاف
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
    
    if lines is not None:
        for rho, theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    
    return frame, (x1, y1, x2, y2)

def calculate_movement(prev_pos, curr_pos):
    # محاسبه فاصله بین دو نقطه
    dist = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
    return dist

# باز کردن ویدئو
cap = cv2.VideoCapture('gauge_video.mp4')

prev_pos = None
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame, needle_pos = detect_needle(frame)
    
    if prev_pos is not None:
        movement = calculate_movement(prev_pos[:2], needle_pos[:2])
        print(f"حرکت عقربه: {movement:.2f} پیکسل")
    
    prev_pos = needle_pos
    
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()

cv2.destroyAllWindows()

# این کد:

# ویدئو را فریم به فریم می‌خواند.
# در هر فریم، عقربه را با استفاده از تشخیص لبه و تبدیل هاف شناسایی می‌کند.
# موقعیت عقربه را در هر فریم ذخیره می‌کند.
# حرکت عقربه را بین دو فریم متوالی محاسبه می‌کند.
# مقدار حرکت را به پیکسل نمایش می‌دهد.
# نکات مهم:

# این کد نیاز به تنظیم پارامترها برای عملکرد بهتر با ویدئوی خاص شما دارد.
# برای تبدیل پیکسل به میلی‌متر، نیاز به کالیبراسیون دارید. باید یک مقیاس مشخص در تصویر داشته باشید و نسبت پیکسل به میلی‌متر را محاسبه کنید.
# الگوریتم تشخیص عقربه ممکن است نیاز به بهبود برای دقت بیشتر داشته باشد.
# برای تبدیل پیکسل به میلی‌متر، می‌توانید یک ضریب تبدیل اضافه کنید:


# # ضریب تبدیل پیکسل به میلی‌متر (این مقدار باید کالیبره شود)
# pixel_to_mm = 0.1  # مثال: هر پیکسل معادل 0.1 میلی‌متر

# movement_mm = movement * pixel_to_mm
# print(f"حرکت عقربه: {movement_mm:.2f} میلی‌متر")
# این کد یک نقطه شروع خوب است، اما ممکن است نیاز به تنظیم و بهبود برای کار با گیج آنالوگ خاص شما داشته باشد.