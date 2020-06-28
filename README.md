# Krita Photobash Plugin

A simple Krita Plugin that lists the images you have on a folder you specify, with the ability to filter by words in the path. 

To use this all you need to do is first [install](https://docs.krita.org/en/user_manual/python_scripting/krita_python_plugin_howto.html) this plugin. A tl;dr of this is: 
- If you're on Linux, drag all the contents of this repository to ~/.local/share/krita/pykrita. On Windows I'm not sure what's the folder is, but you can open the resources folder as highlighted on the link posted above. 
- When inside Krita, activate the docker by going to Settings > Dockers > Photobash Images, and drag it to where you want. 
- Set the references directory. This can be any folder on your drive, and inside of it you can have whatever folders you want, so you can stay organized.
- You can filter the images by what you input on the text field. You can even use multiple words like "rocks marble", and it will show all images that have rock OR marble in the name! 
- If you have more than 9 images, you can pass to the next page by using the arrow buttons in the bottom-left corner. 
- When you have a document open, click on an image, and it will automatically create a new centered paintable layer with that image.
- If you want to have finer control of the size of the image to be placed, you can tweak the variable of the image scale, and if you want to use the original image size, un-tick "Fit to Canvas".

### TODO

Mostly just improvements to performance and minor bug fixes related to the interface. 