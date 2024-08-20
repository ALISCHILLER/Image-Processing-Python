import cv2
import numpy as np
import mss
import time

# تابعی برای کالیبره کردن مقیاس تصویر (تبدیل پیکسل به میلی‌متر)
def calibrate_scale(frame, known_distance, known_width):
    # تبدیل عرض واقعی به پیکسل
    pixels_per_width = known_width / known_distance
    return pixels_per_width

# تابعی برای یافتن موقعیت عقربه در تصویر
def find_needle(frame):
    # تبدیل تصویر به خاکستری
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # اعمال فیلتر بلور برای کاهش نویز
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # استفاده از الگوریتم Canny برای شناسایی لبه‌ها
    edges = cv2.Canny(blurred, 50, 150)

    # استفاده از تبدیل Hough برای شناسایی خطوط در تصویر
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=5)
    
    # بررسی وجود خطوط شناسایی شده
    if lines is not None and len(lines) > 0:
        # انتخاب طولانی‌ترین خط
        longest_line = max(lines, key=lambda line: np.sqrt((line[0][2] - line[0][0])**2 + (line[0][3] - line[0][1])**2))
        x1, y1, x2, y2 = longest_line[0]
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    return None

# تابعی برای انتخاب ناحیه‌ای از صفحه نمایش
def select_area():
    with mss.mss() as sct:
        # گرفتن تصویر از صفحه نمایش
        monitor = sct.monitors[1]  
        screen = np.array(sct.grab(monitor))
        # نمایش تصویر برای انتخاب ناحیه
        cv2.imshow('Select Area', screen)
        
        # انتخاب ناحیه با استفاده از رابط کاربری OpenCV
        bbox = cv2.selectROI('Select Area', screen, fromCenter=False, showCrosshair=True)
        cv2.destroyWindow('Select Area')
        
        return bbox

def main():
    # انتخاب ناحیه‌ای از صفحه نمایش برای پردازش
    bbox = select_area()  

    with mss.mss() as sct:
        # تعریف ناحیه‌ای که باید از صفحه نمایش گرفته شود
        monitor_area = {
            "top": bbox[1],
            "left": bbox[0],
            "width": bbox[2],
            "height": bbox[3],
        }

        # گرفتن اولین فریم برای کالیبره کردن مقیاس
        first_frame = np.array(sct.grab(monitor_area))
        # کالیبره کردن مقیاس بر اساس فاصله و عرض شناخته شده
        pixels_per_mm = calibrate_scale(first_frame, known_distance=100, known_width=100)

        previous_position = None
        recording = False  

        window_name = 'Frame'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  

        try:
            print("فشردن 's' برای شروع ضبط و 'q' برای توقف.")
            while True:
                start_time = time.time()
                # گرفتن فریم جدید از ناحیه انتخاب شده
                frame = np.array(sct.grab(monitor_area))
                
                if recording:
                    # پیدا کردن موقعیت عقربه در فریم
                    needle_position = find_needle(frame)
                    if needle_position:
                        if previous_position:
                            # محاسبه حرکت عقربه در پیکسل
                            movement_in_pixels = np.sqrt((needle_position[0] - previous_position[0])**2 + 
                                                         (needle_position[1] - previous_position[1])**2)
                            # تبدیل حرکت از پیکسل به میلی‌متر
                            movement_in_mm = movement_in_pixels / pixels_per_mm
                            
                            # نمایش حرکت عقربه اگر کمتر از حد معین باشد
                            if movement_in_mm < 1000:  
                                print(f"حرکت عقربه: {movement_in_mm:.2f} میلی‌متر")
                        
                        # ذخیره موقعیت فعلی به عنوان موقعیت قبلی
                        previous_position = needle_position

                # تغییر اندازه فریم برای نمایش در پنجره
                resized_frame = cv2.resize(frame, (bbox[2], bbox[3]))

                # نمایش فریم
                cv2.imshow(window_name, resized_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # تغییر وضعیت ضبط
                    recording = not recording

                # تنظیم زمان تأخیر برای حفظ نرخ فریم ثابت
                elapsed_time = time.time() - start_time
                time.sleep(max(0, 1/30 - elapsed_time))  
        except Exception as e:
            # نمایش خطا در صورت بروز مشکل
            print(f"خطا: {e}")
        finally:
            # بستن پنجره‌های OpenCV و آزادسازی منابع
            cv2.destroyAllWindows()
            sct.close()

if __name__ == "__main__":
    main()

