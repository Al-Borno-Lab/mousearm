# STEP 1: Install Anaconda
Download the executable from [this link](https://www.anaconda.com/download) then follow the instructions there to install Anaconda.

# STEP 2: Install DeepLabCut
Go to [their website](https://deeplabcut.github.io/DeepLabCut/docs/installation.html) and follow the instructions to install DeepLabCut. When you are done, try running the command `python -m deeplabcut` to open up the deeplabcut GUI. You should see the following window pop up:
![deeplabcut intro page](/images/deeplabcut_intro.png)

# STEP 3: Analyze your video files
## Creating the Project
Now that you installed DeepLabCut, it's time to use it. Go ahead and click on the "Create New Project" button on the screen.

Fill in the "Project" and "Experimenter" sections, then enter the bodyparts to track in this exact order: paw, wrist, shoulder, elbow. Now, click on the "Browse for videos" button and select the folder that contains your raw .mp4 files that were recorded. Click "Open," then deselect all the files except for the videos you want to analyze. I recommend selecting "Copy videos to project folder" because it makes the process easier and avoids future errors. When you're done, the window should look something like the below image. You can go ahead and click the "Create" button to create the project now.
![deeplabcut project creation](/images/deeplabcut_project_creation.png)

## Extracting and Labeling Frames
Now click on the "Extract frames" tab at the top of the screen. Click "Select videos" and then select the video you want to label (only select one). You don't have to change any of the other settings if you don't want to, so now just press "Extract Frames" at the bottom right. This may take up to a couple minutes to run, depending on the size of the video and your processor's speed. When it is done, a friendly window will pop up telling you so.

For labeling, head over to the "Label frames" tab (the third tab from the left). Click the "Label frames" button on the screen that pops up and you will see this open in a separate window:
![deeplabcut labeling screen](/images/deeplabcut_labeling.png)

You can either use their tutorial or follow along here.

There are only a few important things you need to know for labeling frames:
1. Add labels: Located in the top left, there is a plus sign in a circle. Clicking this will switch you to adding labels mode, and wherever you click it will add a label.
2. Move labels: If you ever place a label wrong, or want to adjust it, clicking the cursor icon next to the add labels button will switch you to moving labelc mode. You can click and drag to adjust the labels as you wish.
3. Switching between frames: At the bottom there is a play bar like the ones on youtube videos. You can use the buttons on the left and right of this to move left and right by a frame, respectively.
4. Switching keypoints: At the bottom right, there is a dropdown menu with a bodypart name in it. This shows you which label the program is asking you to place next. You can click on this and select a different one from the dropdown menu if you wish.

It will ask you to label 20 frames by default (you can always change this later, and will likely want to for more complex models). Make sure to ctrl+s when you are done to save them before closing this window. 

## Training the Model
Deeplabcut uses pytorch and tensorflow to train a model that labels the rest of the points for you. Click on the "Create training dataset" tab (4th from the left) and click "Create Training Dataset." It should tell you pretty much immediately that it is done.

Now move to the "Train network" tab (5th from the left). These should already be some default training parameters filled in for you, so you can click "Train Network" at the bottom right to start training. This may take a while, depending on your computer. My computer with an RTX 3070 Ti took around 10-15 minutes to train the minimum 200 epochs. Note it is 10-100x faster running this on a GPU, as opposed to a CPU. When it is done, it will pop up telling you so.

## Creating the Labeled Video
Go to the next tab, the "Evaluate network" tab (6th tab). I recommend checking "Compare all bodyparts", which will open a window when it is done showing you the difference between your labeled points and what the system labeled them as. This is a good way to know if you need to add more labeled frames early on. Now click "Evaluate Network" in the bottom right, and it will not let you know when it is done, but it text will show up at the bottom of the screen.

Now, you can move on to the "Analyze videos" tab (7th tab). The video should already be selected, but if it is not, you can re-add it. 

:warning: **Make sure to check the "Save result(s) as csv" box**. Now you can click "Analyze Videos" and wait for it to complete. 
