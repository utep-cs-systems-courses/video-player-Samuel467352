import cv2
import os
import threading
import time

#queue class
class ThreadingBuffer:
    def __init__(self, size):
        #baseline queue implements
        self.Q = [None] * size
        self.qSize = size
        self.puti = 0
        self.geti = 0
        #locks and semaphores
        self.full = threading.Semaphore(0)
        self.empty = threading.Semaphore(self.qSize)
        self.QLock = threading.Lock()

    def put(self, item):
        self.empty.acquire() #check if full
        with self.QLock: #check if being used then release once done
            self.Q[self.puti] = item
            self.puti = (self.puti + 1) % self.qSize
        self.full.release() #release semaphore
        

    def get(self):
        self.full.acquire() #check if empty
        try:
            self.QLock.acquire() #check if being used
            item = self.Q[self.geti]
            self.geti = (self.geti + 1) % self.qSize
        except Exception as e:
            print("currently busy")
        finally:
            self.QLock.release() #release after being used
        self.empty.release() #release empty check
        return item
        
        
#methods for file handling
def extractor(outQueue):
    clipFileName = 'clip.mp4'
    # initialize frame count
    count = 0

    # open the video clip
    vidcap = cv2.VideoCapture(clipFileName)

    # read one frame
    success,image = vidcap.read()

    print(f'Reading frame {count} {success}')
    while success and count < 72:

        # add the current frame to queue as a jpeg image
        outQueue.put(image)

        success,image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1
    #one last end value to end the threads
    outQueue.put(None)

def converter(inQueue, outQueue):
    count = 0

    #get frame from queue
    inputFrame = inQueue.get()

    while inputFrame is not None and count < 72:
        print(f'Converting frame {count}')

        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
    
        # send to output queue
        outputFrame = grayscaleFrame
        outQueue.put(outputFrame)

        count += 1

        #get next frame
        inputFrame = inQueue.get()
    #one last end value to end the threads
    outQueue.put(None)

def displayer(inQueue):
    frameDelay   = 42       # the answer to everything

    # initialize frame count
    count = 0

    # load the frame
    frame = inQueue.get()

    while frame is not None:
    
        print(f'Displaying frame {count}')
        # Display the frame in a window called "Video"
        cv2.imshow('Video', frame)

        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(frameDelay) and 0xFF == ord("q"):
            break    
    
        # get the next frame filename
        count += 1
        frame = inQueue.get()
        

    # make sure we cleanup the windows, otherwise we might end up with a mess
    cv2.destroyAllWindows()


#main area
buffer1 = ThreadingBuffer(10)
buffer2 = ThreadingBuffer(10)

exThread = threading.Thread(target=extractor, args=(buffer1,))
convThread = threading.Thread(target=converter, args=(buffer1, buffer2))
dispThread = threading.Thread(target=displayer, args=(buffer2,))

exThread.start()
convThread.start()
dispThread.start()

exThread.join()
convThread.join()
dispThread.join()




