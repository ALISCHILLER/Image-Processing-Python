# برای پیاده‌سازی این کار، شما به چند مرحله نیاز دارید:

# تشخیص عقربه در تصویر: برای این کار می‌توانید از کتابخانه‌هایی مانند OpenCV استفاده کنید که به شما اجازه می‌دهد تا اشیاء را در تصویر شناسایی و ردیابی کنید.
# محاسبه حرکت عقربه: با استفاده از تغییرات موقعیت عقربه در فریم‌های متوالی، می‌توانید حرکت آن را محاسبه کنید.
# تبدیل حرکت به میلی‌متر: این بستگی به مقیاس واقعی گیج دارد که باید به صورت دستی یا از طریق کالیبراسیون مشخص شود.
# در اینجا یک نمونه کد پایتون با استفاده از OpenCV برای شروع:


import cv2
import numpy as np

# تابعی برای کالیبراسیون مقیاس
def calibrate_scale(frame, known_distance, known_width):
    # اینجا باید یک شیء با عرض شناخته شده را در تصویر شناسایی کنید
    # برای سادگی، فرض کنیم یک خط به طول known_width را پیدا کرده‌ایم
    pixels_per_mm = known_width / known_distance
    return pixels_per_mm

# تابع برای پیدا کردن موقعیت عقربه
def find_needle(frame):
    # پردازش تصویر برای پیدا کردن عقربه
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # استفاده از تابعی مانند Canny برای کشف لبه‌ها
    edges = cv2.Canny(gray, 50, 150)
    # پیدا کردن خطوط که ممکن است عقربه باشند
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # انتخاب خطی که به عنوان عقربه در نظر گرفته شود
            return ((x1 + x2) / 2, (y1 + y2) / 2)  # میانگین مختصات برای موقعیت عقربه
    return None

# ویدئو کپچر
cap = cv2.VideoCapture('path_to_your_video.mp4')

# کالیبراسیون
_, first_frame = cap.read()
pixels_per_mm = calibrate_scale(first_frame, known_distance=100, known_width=100)  # مثال: 100 میلی‌متر فاصله واقعی

previous_position = None
while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break

    needle_position = find_needle(frame)
    if needle_position:
        if previous_position:
            # محاسبه حرکت در پیکسل
            movement_in_pixels = np.sqrt((needle_position[0] - previous_position[0])**2 + 
                                         (needle_position[1] - previous_position[1])**2)
            # تبدیل به میلی‌متر
            movement_in_mm = movement_in_pixels / pixels_per_mm
            print(f"حرکت عقربه: {movement_in_mm:.2f} میلی‌متر")
        
        previous_position = needle_position

    cv2.imshow('Frame', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# نکات مهم:

# این کد فقط یک چارچوب اولیه است و برای دقت بالا نیاز به تنظیمات و پیش‌پردازش‌های بیشتری دارد.
# شما باید مقدار known_distance و known_width را با مقادیر واقعی خود جایگزین کنید.
# تشخیص عقربه می‌تواند پیچیده‌تر باشد، به خصوص اگر گیج پیچیده باشد یا در شرایط نوری متغیر قرار داشته باشد. ممکن است نیاز به استفاده از مدل‌های یادگیری ماشین یا تکنیک‌های پیشرفته‌تر تشخیص شکل داشته باشید.

