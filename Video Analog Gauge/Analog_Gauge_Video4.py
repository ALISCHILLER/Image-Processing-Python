import numpy as np
import cv2
import mss
import mss.tools

# Initial parameters
min_angle = float(input('Min angle (lowest possible angle of dial) - in degrees: '))
max_angle = float(input('Max angle (highest possible angle) - in degrees: '))
min_value = float(input('Min value: '))
max_value = float(input('Max value: '))
units = input('Enter units: ')

# Initialize MSS for screen capture
sct = mss.mss()
monitor = sct.monitors[1]  # Use monitor 1 (primary screen)

def avg_circles(circles, b):
    avg_x = avg_y = avg_r = 0
    for i in range(b):
        avg_x += circles[0][i][0]
        avg_y += circles[0][i][1]
        avg_r += circles[0][i][2]
    return int(avg_x / b), int(avg_y / b), int(avg_r / b)

def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

while True:
    try:
        # Capture the screen
        img = np.array(sct.grab(monitor))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Convert to BGR for OpenCV

        cv2.imshow('Analog Gauge Reader', img_rgb)

        # Image processing
        img_blur = cv2.GaussianBlur(img_rgb, (5, 5), 3)
        gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
        height, width = img_rgb.shape[:2]

        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50, int(height*0.35), int(height*0.48))
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            x, y, r = avg_circles(circles, len(circles))

            cv2.circle(img_rgb, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)
            cv2.circle(img_rgb, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)

            separation = 10.0
            interval = int(360 / separation)
            p1 = np.zeros((interval, 2))
            p2 = np.zeros((interval, 2))
            p_text = np.zeros((interval, 2))
            for i in range(interval):
                p1[i] = [x + 0.9 * r * np.cos(separation * i * np.pi / 180), y + 0.9 * r * np.sin(separation * i * np.pi / 180)]
                p2[i] = [x + r * np.cos(separation * i * np.pi / 180), y + r * np.sin(separation * i * np.pi / 180)]
                p_text[i] = [x - 10 + 1.2 * r * np.cos(separation * (i + 9) * np.pi / 180), y + 5 + 1.2 * r * np.sin(separation * (i + 9) * np.pi / 180)]

            for i in range(interval):
                cv2.line(img_rgb, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])), (0, 255, 0), 2)
                cv2.putText(img_rgb, '%s' % int(i * separation), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1, cv2.LINE_AA)

            gray2 = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            thresh = 175
            maxValue = 255
            th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)

            minLineLength = 10
            maxLineGap = 0
            lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100, minLineLength=minLineLength, maxLineGap=0)

            final_line_list = []
            diff1LowerBound = 0.15
            diff1UpperBound = 0.25
            diff2LowerBound = 0.5
            diff2UpperBound = 1.0
            if lines is not None:
                for x1, y1, x2, y2 in lines[:, 0]:
                    diff1 = dist_2_pts(x, y, x1, y1)
                    diff2 = dist_2_pts(x, y, x2, y2)
                    if diff1 > diff2:
                        diff1, diff2 = diff2, diff1
                    if (diff1 < diff1UpperBound * r and diff1 > diff1LowerBound * r and
                        diff2 < diff2UpperBound * r and diff2 > diff2LowerBound * r):
                        line_length = dist_2_pts(x1, y1, x2, y2)
                        final_line_list.append([x1, y1, x2, y2])

            if final_line_list:
                x1, y1, x2, y2 = final_line_list[0]
                cv2.line(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)

                dist_pt_0 = dist_2_pts(x, y, x1, y1)
                dist_pt_1 = dist_2_pts(x, y, x2, y2)
                if dist_pt_0 > dist_pt_1:
                    x_angle = x1 - x
                    y_angle = y - y1
                else:
                    x_angle = x2 - x
                    y_angle = y - y2
                res = np.arctan2(y_angle, x_angle)
                res = np.rad2deg(res)

                if x_angle > 0 and y_angle > 0:
                    final_angle = 270 - res
                elif x_angle < 0 and y_angle > 0:
                    final_angle = 90 - res
                elif x_angle < 0 and y_angle < 0:
                    final_angle = 90 - res
                elif x_angle > 0 and y_angle < 0:
                    final_angle = 270 - res

                old_range = max_angle - min_angle
                new_range = max_value - min_value
                new_value = (((final_angle - min_angle) * new_range) / old_range) + min_value

                print("Current reading: %s %s" % (("%.2f" % new_value), units))

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    except ValueError:
        pass
    except IndexError:
        pass

cv2.destroyAllWindows()
