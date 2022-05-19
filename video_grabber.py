import cv2
from threading import Thread, Lock
import time
import sys


import utils

class VideoGrabber(Thread):

    def __init__(self, jpeg_quality, jpeg_lib):

        Thread.__init__(self)
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.buffer = None
        self.lock = Lock()

        self.jpeg_encode_func = lambda img, jpeg_quality=jpeg_quality: utils.cv2_encode_image(img, jpeg_quality)


    def stop(self):
        self.running = False

    def get_buffer(self):

        if self.buffer is not None:
            self.lock.acquire()
            cpy = self.buffer
            self.lock.release()
            return cpy

    def run(self):
        while self.running:
            success, img = self.cap.read()
            if not success:
                continue

            # JPEG compression
            # Protected by a lock
            # As the main thread may asks to access the buffer
            self.lock.acquire()
            self.buffer = self.jpeg_encode_func(img)
            self.lock.release()


if __name__ == '__main__':

    jpeg_quality = 100

    grabber = VideoGrabber(jpeg_quality, jpeg_lib='turbo')
    grabber.start()
    time.sleep(1)

    cv2.namedWindow("Image")

    keep_running = True
    idx = 0
    t0 = time.time()

    while keep_running:
        data = grabber.get_buffer()
        if data is None:
            time.sleep(1)
            continue
        cv2.imshow("Image")
        keep_running = not(cv2.waitKey(1) & 0xFF == ord('q'))

        idx += 1
        if idx == 100:
            t1 = time.time()
            sys.stdout.write("\r {:04} images/second    ".format(100/(t1-t0)))
            sys.stdout.flush()
            t0 = t1
            idx = 0

    print()
    print("Quitting")
    grabber.stop()

