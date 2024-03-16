import cv2
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
stream = cv2.VideoCapture(0)
if not stream.isOpened():
    raise IOError("Failed to open the camera")

while True:
    ret, frame = stream.read()
    if not ret:
        raise IOError("I don't know, something failed")

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # smaller minNeighbors the more sensitive it is to "faces"
    faces = face_cascade.detectMultiScale(grey, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, pt1=(x, y), pt2=(x+w, y+h), color=(0, 0, 255), thickness=2)

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == ord("q"):
        break
stream.release()
cv2.destroyAllWindows()