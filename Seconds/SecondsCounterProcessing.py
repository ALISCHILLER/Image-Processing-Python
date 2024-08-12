import cv2
import numpy as np

def detect_second_hand_position(image_path):
    # خواندن تصویر
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found or path is incorrect.")
        return

    # تبدیل تصویر به خاکستری
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # شناسایی دایره‌ها (ساعت)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
                               param1=50, param2=30, minRadius=50, maxRadius=150)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            radius = i[2]

            # ایجاد ماسک برای ناحیه ساعت
            mask = np.zeros_like(gray)
            cv2.circle(mask, center, radius, 255, thickness=-1)
            roi = cv2.bitwise_and(gray, gray, mask=mask)

            # شناسایی خطوط (عقربه‌ها)
            lines = cv2.HoughLinesP(roi, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

            if lines is not None:
                second_hand_angle = None
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    # فرض بر اینکه عقربه ثانیه‌شمار بلندتر از بقیه است
                    if length > radius * 0.8:
                        # محاسبه زاویه عقربه ثانیه‌شمار
                        angle = np.degrees(np.arctan2(y2 - center[1], x2 - center[0]))
                        if angle < 0:
                            angle += 360
                        second_hand_angle = angle
                        break

                if second_hand_angle is not None:
                    # تبدیل زاویه به عدد ثانیه
                    second_hand_position = int(round((second_hand_angle / 360) * 60))
                    print(f"Second hand is pointing to: {second_hand_position} seconds")
                else:
                    print("Second hand not detected.")
    else:
        print("No circles detected in the image.")

    # نمایش تصویر با دایره‌های تشخیص داده شده و خطوط عقربه‌ها
    cv2.imshow('Detected Second Hand', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# استفاده از تابع
image_path = r'E:\project-zar\custom\image processing\python\Seconds\clock.jpg'
detect_second_hand_position(image_path)
