# Krita Photobash Plugin

Want to see this in action? Check out the [video](https://youtu.be/QX9jwhfpB_8)!
A simple Krita Plugin that lists the images you have on a folder you specify, with the ability to filter by words in the path. 

# Features

- To add an image to the document simply click on them! Control their scale with the Slider, and fit it to the canvas. If the slider is at 100%, without fitting to canvas, the image will be added with it's full resolution. If fitting is enabled, it will be scaled to match the width or height of the document, depending on the aspect ratio of both the image and the document. When you try it, you'll see that it's pretty easy to understand :)  
- Filter your images based on what you text on the search field. You can even use multiple words like "rocks marble", and it will show all images that have rock OR marble in the name! 
- Right-click on any image to access a quick pop-up menu. There you can preview the image in the docker, open as a new document, or even pin to beginning of the list. This last feature remembers your favourites, even after you close Krita! As long as you don't change the base directory for the references, it will always remember your favourites, and place them in the correct order you specified. This is especially useful when you have dozens of images, but really use a small number of them all the time.
- You can also add an image as a reference using the quick menu. If you want to delete a reference later, you need to press the "Pushpin Icon" on your toolbox, and remove it there.
- Change the page by clicking on the arrow keys in the bottom tray, or for extra productivity, scroll using the middle-mouse wheel. If you're using a stylus, you can do "ALT" + Click and Drag to scroll through the pages. 
- Drag an image to the canvas using "SHIFT" + Drag. It's a Qt shorcut, so it's going to add the image in it's original size, but a fix is being worked on! 

# Installation

To use this all you need to do is first [install](https://docs.krita.org/en/user_manual/python_scripting/krita_python_plugin_howto.html) this plugin. A tl;dr of this is: 
- If you're on Linux, drag all the contents of this repository to "~/.local/share/krita/pykrita". On Windows that path is "C:\Users\username\AppData\Roaming\krita\pykrita". 
- When inside Krita, activate the docker by going to Settings > Dockers > Photobash Images, and drag it to where you want. 
- Set the references directory. This can be any folder on your drive, and inside of it you can have whatever folders you want, so you can stay organized.
- When you have a document open, click on an image, and it will automatically create a new centered paintable layer with that image.