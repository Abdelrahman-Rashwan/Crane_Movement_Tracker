# Import used libraries
from tkinter import *
from tkinter import filedialog
import tkinter
import tkinter.messagebox
import cv2
import numpy as np


# Parameters Section
#------------------------------------------------------------------------------

# Parameters to change
count_time = 30  # Counts after 30 frame
movement_threshold = 0.5  # Movement threshold  in pixels

tracker_names = ["KCF", 
                 "MIL", 
                 "MEDIANFLOW", 
                 "GOTURN", 
                 "MOSSE", 
                 "CSRT"]
tracker_types = [cv2.TrackerMIL_create, cv2.TrackerKCF_create, cv2.TrackerGOTURN_create, cv2.TrackerCSRT_create]

#------------------------------------------------------------------------------

#Functions Section
#------------------------------------------------------------------------------

def Credits():
    tkinter.messagebox.showinfo("Credits", " عبدالرحمن سمير رشوان\n كلية الذكاء الاصطناعي كفر الشيخ")
    
# Function for opening the "Explorer File Window"
def browseFiles():
    browseFiles.var = filedialog.askopenfilename(initialdir = "D:", title = "Select a File", filetypes = (("MOV", ".mov"), ("MP4", ".mp4"), ("All Files", ".")))
    # Change label contents
    label_file_explorer.configure(text="File Opened: "+browseFiles.var)
    
def Tracker_Numbers():
    tkinter.messagebox.showinfo("Tracker Numbers", "1) KCF\n2) MIL\n3) MEDIANFLOW\n4) GOTURN\n5) MOSSE\n6) CSRT")
	
    
def Open_Video():
    name=name_var.get()
    name_var.set("1")
    
    mil = 0
    sec = 0
    miin = 0
    
    # Create a VideoCapture object and read from input file
    cap = cv2.VideoCapture(browseFiles.var)
    ret, frame = cap.read()

    # Get height and width of the video
    height, width, layers = frame.shape

    # Define new height and width for the video
    new_h = int(height / 1.5)
    new_w = int(width  / 1.5)
    dim = (new_w , new_h)

    # Resize The Video
    resize = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

    # Check if video opened successfully
    if (cap.isOpened()== False):
        print("Error opening video stream or file")

    tracker = name

    # Select tracker used
    tracker_name = tracker_names[tracker]
    tracker = tracker_types[tracker]()

    # Define an initial bounding box
    bbox = (287, 23, 86, 320)

    # Select Crane
    bbox = cv2.selectROI("Select Crane (press enter after selection)", resize, False)

    cv2.destroyAllWindows()

    # Select start region
    region = cv2.selectROI("Select Region (press enter after selection)", resize, False)

    cv2.destroyAllWindows()

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    # Check if video opened successfully
    if (cap.isOpened() == False):
        print("Error opening video stream or file")

    count = 0
    in_region = False
    last_in_region = False
    out_region_timer = count_time+1
    last_cur = (0, 0)

    # Read until video is completed
    while cap.isOpened():
        # Read a new frame
        ok, frame = cap.read()
        if not ok:
            break
        
        # The Timer
        mil = mil+1
                
        if (mil ==21):
            sec+=1
            mil = 0
                    
            if (sec==60):
                miin+=1
                sec = 0
        
        # Get height and width of the video
        height, width, layers = frame.shape

        # Define new height and width for the video
        new_h = int(height / 1.5)
        new_w = int(width  / 1.5)
        dim = (new_w , new_h)

        # Resize The Video
        Video = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)

        # Start timer
        timer = cv2.getTickCount()
        

        # Update tracker
        ok, bbox = tracker.update(Video)

        last_in_region = in_region
        cur = (bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2)
        in_region = region[0] < cur[0] < region[0] + region[2] and \
                    region[1] < cur[1] < region[1] + region[3]

        if not in_region:
            out_region_timer += 1
        else:
            out_region_timer = 0

        if out_region_timer == count_time:
            count += 1

        if pow(last_cur[0] - cur[0], 2) + pow(last_cur[1] - cur[1], 2) > pow(movement_threshold, 2):
            is_moving = True
        else:
            is_moving = False

        last_cur = cur

        # Calculate Frames per second (FPS)
        fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)

        p1 = (int(region[0]), int(region[1]))
        p2 = (int(region[0] + region[2]), int(region[1] + region[3]))
        cv2.rectangle(Video, p1, p2, (0, 255 * (in_region), 255 * (1 - in_region)), 2, 1)

        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(Video, p1, p2, (255, 0, 0), 2, 1)
        else:
            # Tracking failure
            cv2.putText(Video, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

        # Display tracker type on frame
        cv2.putText(Video, tracker_name + " Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (96, 66, 245), 2)

        # Display FPS on frame
        cv2.putText(Video, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (96, 66, 245), 2)

        # Display moving state
        cv2.putText(Video, "State : " + ("Moving" if is_moving else "Stopped"), (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                    (96, 66, 245), 2)

        # Display counter
        cv2.putText(Video, "Count : " + str(count), (100, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (96, 66, 245), 2)
        
        # Display counter
        cv2.putText(Video, "Timer ==> %d:%d" %(miin,sec) , (100, 140), cv2.FONT_HERSHEY_SIMPLEX,0.75, (96, 66, 245), 2)
        
        # Display result
        cv2.imshow("Tracking", Video)

        # Exit if Q pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):  # if press Q
            break

    # When everything done, release the video capture object
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()

#------------------------------------------------------------------------------    


# Program.exe Section
#------------------------------------------------------------------------------
 
# Create the root window
window = Tk()
# Set window title
window.title('Graduation Project')
# Set window size
window.geometry("500x250")
#Set window background color
window.config(background = "#eef2f3")
# Create a File Explorer label
label_file_explorer = Label(window, font=("Verdana",7), text = "Select A Video First")

# Create The Buttons
button_explore = Button(window, font=("Verdana",12,'bold'), text="Browse Files", 
                        width=21, height=4, bd=0, bg="#32de97", activebackground="#3c9d9b", 
                        fg='#ffffff', command = browseFiles)

button_openvid = Button(window, font=("Verdana",12,'bold'), text="Open Video", 
                        width=21, height=4, bd=0, bg="#32de97", activebackground="#3c9d9b", 
                        fg='#ffffff', command = Open_Video)

button_credits = Button(window, font=("Verdana",7), text="Credits", 
                        bd=0, bg="#eef2f3", activebackground="#eef2f3", 
                        fg='black', command = Credits)

# Tracker Number Input
name_var=IntVar()
name_label = Label(window, text = 'Tracker Number:', font=('calibre',10, 'bold'))
name_entry = Entry(window, font=('calibre',10,'normal'))
name_entry.insert(0, "1")
button_trackernumber = Button(window, font=("Verdana",7,'bold') ,text=" ? ", command=Tracker_Numbers)

# Place Objects on The Screen
button_explore.place(x=3, y=145)
button_openvid.place(x=260, y=145)
button_credits.place(x=450, y=230)
name_entry.place(x=8, y=80)
button_trackernumber.place(x=155, y=79)
name_label.place(x=3, y=60)
label_file_explorer.place(x=3 ,y=20)

# Let the window wait for any events
window.mainloop()

#------------------------------------------------------------------------------