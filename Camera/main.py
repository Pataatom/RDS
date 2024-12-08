import pygame
import time
import cv2
import pigpio
import pyfiglet

pi = pigpio.pi()
pygame.mixer.init()

print(pyfiglet.figlet_format(text="RDS", font="big"))  # welcome text
print("\n")

if not pi.connected:
    print("Failed to connect to pigpio daemon!")
    time.sleep(1)
    exit()

print("Connecting to pigpio daemon was successful")
led_pin = 26
pir_pin = 13
pi.set_mode(led_pin, pigpio.OUTPUT)
pi.set_mode(pir_pin, pigpio.INPUT)


# ____CAMERA____
cap = cv2.VideoCapture(0)
confidence_threshold = 0.7  # if the confidence of the prediction is lower than this the prediction won't count
color_of_bbox = (0, 255, 0)
color_of_text = (0, 255, 0)
# count_of_people = 0
# averaged_num_of_people = 0
people_averaging_list = []
fps = cap.get(cv2.CAP_PROP_FPS)  # mostly 30

caffe_model = r"MobileNetSSD_deploy.caffemodel"  # Pre-trained model weights
prototxt = r"MobileNetSSD_deploy.prototxt"  # Model definition is stored in this file

net = cv2.dnn.readNetFromCaffe(prototxt, caffe_model)
classNames = {15: 'person'}
# ____CAMERA____

def alarm_sound(alarm_path):
    pygame.mixer.music.load(alarm_path)
    try:
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.5)  # Keep looping while alarm is playing
    except KeyboardInterrupt:
        pygame.mixer.music.stop()


def optical_human_recognition(show_video=False):
    global cap
    count_of_people = 0
    averaged_num_of_people = 0
    ret, frame = cap.read()

    if not ret:
        raise IOError("Cam not recording")
    width = frame.shape[1]
    height = frame.shape[0]

    # blob is for the model to understand
    blob = cv2.dnn.blobFromImage(frame, scalefactor=1 / 127.5, size=(300, 300), mean=(127.5, 127.5, 127.5), swapRB=True,
                                 crop=False)
    net.setInput(blob)

    detections = net.forward()

    for n in range(detections.shape[2]):  # detections.shape[2] contains the max possible num of detected bbox in frame
        confidence = detections[0, 0, n, 2]  # number 2 is the selector of which info from detection you want to access
        if confidence > confidence_threshold:

            class_id = int(detections[0, 0, n, 1])

            if class_id in classNames:
                count_of_people += 1
            if show_video:
                if class_id in classNames:
                    # scale to the frame
                    x_top_left = int(detections[0, 0, n, 3] * width)  # The coordinates are normalized to the range [0, 1],
                    y_top_left = int(detections[0, 0, n, 4] * height)  # where 0 is the leftmost position and 1 is the right
                    x_bottom_right = int(detections[0, 0, n, 5] * width)
                    y_bottom_right = int(detections[0, 0, n, 6] * height)

                    # draw bbox around the detected person
                    if count_of_people == 1:  # if there is only one person, then he becomes target
                        cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 0, 255), 2)
                    else:
                        cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), color_of_bbox, 2)

                    label = classNames[class_id] + ": " + str(int(confidence * 100)) + "%"
                    cv2.putText(frame, label, (x_top_left, y_top_left - 9),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, color_of_text, 2)
    if show_video:
        cv2.imshow("Turret", frame)

    if cv2.waitKey(1) >= 0:  # break with any key I suppose
        exit()
    # ____num of people on average____
    people_averaging_list.append(count_of_people)
    if len(people_averaging_list) == fps/2:  # averaging frames
        # averaged_num_of_people = 0  # I do realize that using this variable for more things is bad practice

        for num in people_averaging_list:
            averaged_num_of_people += num

        averaged_num_of_people = averaged_num_of_people / len(people_averaging_list)
        people_averaging_list.clear()
        # print(round(averaged_num_of_people)) # debug
        return round(averaged_num_of_people)
    else:
        return None
    # ____num of people on average____

# alarm_sound(r"Burglar Alarm Going off with Sirens.mp3")

try:
    '''
        while True:
            num_of_detected_people = optical_human_recognition()
            if num_of_detected_people is not None:
                if num_of_detected_people > 0:
                    pi.write(led_pin, 1)
                else:
                    pi.write(led_pin, 0)
    '''
    while True:
        if pi.read(pir_pin) == 1:
            pi.write(led_pin, 1)
        else:
            pi.write(led_pin, 0)
except KeyboardInterrupt:
    print("ya")
    time.sleep(1)
pi.stop()


