import cv2
import numpy as np
import time

def avg_circles(circles, b):
    avg_x = 0
    avg_y = 0
    avg_r = 0
    for i in range(b):
        avg_x += circles[0][i][0]
        avg_y += circles[0][i][1]
        avg_r += circles[0][i][2]
    avg_x = int(avg_x / b)
    avg_y = int(avg_y / b)
    avg_r = int(avg_r / b)
    return avg_x, avg_y, avg_r

def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calibrate_gauge(gauge_number, file_type):
    image_path = r'E:\project-zar\custom\image processing\python\Seconds\gauge-%s.%s' % (gauge_number, file_type)
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image '{image_path}'. Please check the file path.")
        return None, None, None, None, None, None, None, None

    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, np.array([]), 100, 50, int(height * 0.35), int(height * 0.48))
    if circles is None:
        print("Error: No circles were detected.")
        return None, None, None, None, None, None, None, None

    a, b, c = circles.shape
    x, y, r = avg_circles(circles, b)
    cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.circle(img, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)

    separation = 10.0
    interval = int(360 / separation)
    p1 = np.zeros((interval, 2))
    p2 = np.zeros((interval, 2))
    p_text = np.zeros((interval, 2))
    for i in range(0, interval):
        for j in range(0, 2):
            if j % 2 == 0:
                p1[i][j] = x + 0.9 * r * np.cos(separation * i * np.pi / 180)
            else:
                p1[i][j] = y + 0.9 * r * np.sin(separation * i * np.pi / 180)
    text_offset_x = 10
    text_offset_y = 5
    for i in range(0, interval):
        for j in range(0, 2):
            if j % 2 == 0:
                p2[i][j] = x + r * np.cos(separation * i * np.pi / 180)
                p_text[i][j] = x - text_offset_x + 1.2 * r * np.cos((separation) * (i + 9) * np.pi / 180)
            else:
                p2[i][j] = y + r * np.sin(separation * i * np.pi / 180)
                p_text[i][j] = y + text_offset_y + 1.2 * r * np.sin((separation) * (i + 9) * np.pi / 180)

    for i in range(0, interval):
        cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])), (0, 255, 0), 2)
        cv2.putText(img, '%s' % int(i * separation), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1, cv2.LINE_AA)

    calibration_image_path = r'E:\project-zar\custom\image processing\python\Seconds\gauge-%s-calibration.%s' % (gauge_number, file_type)
    cv2.imwrite(calibration_image_path, img)

    print('gauge number: %s' % gauge_number)
    min_angle = input('Min angle (lowest possible angle of dial) - in degrees: ')
    max_angle = input('Max angle (highest possible angle) - in degrees: ')
    min_value = input('Min value: ')
    max_value = input('Max value: ')
    units = input('Enter units: ')

    return min_angle, max_angle, min_value, max_value, units, x, y, r

def get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type):
    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = 175
    maxValue = 255

    th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)

    cv2.imwrite(r'E:\project-zar\custom\image processing\python\Seconds\gauge-%s-tempdst2.%s' % (gauge_number, file_type), dst2)

    minLineLength = 10
    maxLineGap = 0
    lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100, minLineLength=minLineLength, maxLineGap=0)

    final_line_list = []
    diff1LowerBound = 0.15
    diff1UpperBound = 0.25
    diff2LowerBound = 0.5
    diff2UpperBound = 1.0
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            diff1 = dist_2_pts(x, y, x1, y1)
            diff2 = dist_2_pts(x, y, x2, y2)
            if diff1 > diff2:
                temp = diff1
                diff1 = diff2
                diff2 = temp
            if (((diff1 < diff1UpperBound * r) and (diff1 > diff1LowerBound * r) and (diff2 < diff2UpperBound * r)) and (diff2 > diff2LowerBound * r)):
                line_length = dist_2_pts(x1, y1, x2, y2)
                final_line_list.append([x1, y1, x2, y2])

    x1 = final_line_list[0][0]
    y1 = final_line_list[0][1]
    x2 = final_line_list[0][2]
    y2 = final_line_list[0][3]
    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imwrite(r'E:\project-zar\custom\image processing\python\Seconds\gauge-%s-lines-2.%s' % (gauge_number, file_type), img)

    dist_pt_0 = dist_2_pts(x, y, x1, y1)
    dist_pt_1 = dist_2_pts(x, y, x2, y2)
    if dist_pt_0 > dist_pt_1:
        x_angle = x1 - x
        y_angle = y - y1
    else:
        x_angle = x2 - x
        y_angle = y - y2
    res = np.arctan(np.divide(float(y_angle), float(x_angle)))
    res = np.rad2deg(res)
    if x_angle > 0 and y_angle > 0:
        final_angle = 270 - res
    if x_angle < 0 and y_angle > 0:
        final_angle = 90 - res
    if x_angle < 0 and y_angle < 0:
        final_angle = 90 - res
    if x_angle > 0 and y_angle < 0:
        final_angle = 270 - res
    if final_angle < 0:
        final_angle += 360

    if final_angle > 360:
        final_angle -= 360

    final_value = (final_angle - float(min_angle)) * (float(max_value) - float(min_value)) / (float(max_angle) - float(min_angle)) + float(min_value)

    print("Gauge Reading Value: ", final_value)

def main():
    gauge_number = input('Enter gauge number: ')
    file_type = 'jpg'
    min_angle, max_angle, min_value, max_value, units, x, y, r = calibrate_gauge(gauge_number, file_type)
    if min_angle is None:
        return

    image_path = r'E:\project-zar\custom\image processing\python\Seconds\gauge-%s.%s' % (gauge_number, file_type)
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image '{image_path}'. Please check the file path.")
        return

    get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r, gauge_number, file_type)

if __name__ == '__main__':
    main()
