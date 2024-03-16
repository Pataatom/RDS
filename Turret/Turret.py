import cv2

confidence_threshold = 0.7  # if the confidence of the prediction is lower than this the prediction won't count
color_of_bbox = (0, 255, 0)
color_of_text = (0, 255, 0)
count_of_people = 0
averaged_num_of_people = 0
people_averaging_list = []
frames_for_averaging = 10

caffe_model = r"MobileNetSSD_deploy.caffemodel"  # Pre-trained model weights
prototxt = r"MobileNetSSD_deploy.prototxt"  # Model definition is stored in this file

# read a network model (pre-trained) stored in Caffe framework's format
net = cv2.dnn.readNetFromCaffe(prototxt, caffe_model)

# dictionary with the object class id and names on which the model is trained
classNames = {15: 'person'}

cap = cv2.VideoCapture(0)

while True:
    count_of_people = 0
    frames_for_averaging -= 1
    ret, frame = cap.read()

    if not ret:
        raise IOError("Cam not recording")

    width = frame.shape[1]
    height = frame.shape[0]

    blob = cv2.dnn.blobFromImage(frame, scalefactor=1 / 127.5, size=(300, 300), mean=(127.5, 127.5, 127.5), swapRB=True,
                                 crop=False)
    # blob is for the model to understand

    net.setInput(blob)
    detections = net.forward()

    # detections array is in the format 1,1,N,7, where N is the detected bounding boxes
    # for each detection, the description contains : [image_id, label, conf, x_min, y_min, x_max, y_max]
    for i in range(detections.shape[2]):  # detections.shape[2] contains the max possible num of detected bbox in frame
        confidence = detections[0, 0, i, 2]  # number 2 is the selector of which info from detection you want to access
        if confidence > confidence_threshold:

            class_id = int(detections[0, 0, i, 1])

            # scale to the frame
            x_top_left = int(detections[0, 0, i, 3] * width)  # The coordinates are normalized to the range [0, 1],
            y_top_left = int(detections[0, 0, i, 4] * height)  # where 0 is the leftmost position and 1 is the right pos
            x_bottom_right = int(detections[0, 0, i, 5] * width)
            y_bottom_right = int(detections[0, 0, i, 6] * height)

            if class_id in classNames:
                count_of_people += 1
                label = classNames[class_id] + ": " + str(int(confidence * 100)) + "%"

                # draw bbox around the detected person
                if averaged_num_of_people == 1:  # if there is only one person, then he becomes target
                    cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), (0, 0, 255), 2)
                else:
                    cv2.rectangle(frame, (x_top_left, y_top_left), (x_bottom_right, y_bottom_right), color_of_bbox, 2)

                # get width and text of the label string
                (w, h), t = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                # y_top_left = max(y_top_left, h) # don't understand this line fully, have to play with it

                '''
                draw bounding box around the text (OPTIONAL)
                cv2.rectangle(frame, (x_top_left - 1, y_top_left - h - 9),
                              (x_top_left + w, y_top_left + t - 9), (0, 0, 0), cv2.FILLED)
                '''
                cv2.putText(frame, label, (x_top_left, y_top_left - 9),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color_of_text, 2)

    people_averaging_list.append(count_of_people)
    if len(people_averaging_list) == 20:  # averaging frames
        averaged_num_of_people = 0

        for num in people_averaging_list:
            averaged_num_of_people += num

        averaged_num_of_people = averaged_num_of_people / len(people_averaging_list)
        print(round(averaged_num_of_people))
        people_averaging_list.clear()

    # fucking showing you what I got
    cv2.imshow("Turret", frame)

    if cv2.waitKey(1) >= 0:  # break with any key I suppose
        break

cap.release()
cv2.destroyAllWindows()
