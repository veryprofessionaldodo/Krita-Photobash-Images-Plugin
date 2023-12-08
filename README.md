# Krita Photobash Plugin

An advanced Krita Plugin, laser-focused on improving productivity for photo-bashing and references!
Want to see this in action? Check out the [video](https://youtu.be/QX9jwhfpB_8)! Tested in Krita 4.4.8, 5.0 and 5.1.,5.2.1

## Changes
- Supports search by extra caption file (must be a text file with the same name as the image)
- Supports adding image with transparency layer
- Supports adding image grouped with an erase blending layer

## Installation

To download this plugin, download a zip from the [releases](https://github.com/veryprofessionaldodo/Krita-Photobash-Images-Plugin/releases). After extracting, place the it's contents in the correct folder:

- **Linux**: Place the folder inside "~/.local/share/krita/pykrita". 
- **Windows**: Place the folder inside "C:\Users\username\AppData\Roaming\krita\pykrita".

All that's left is to activate the plugin inside Krita! To do this, start Krita, and on the top bar go to Settings > Configure Krita > Python Plugin Manager. On the list, if the plugin was placed correctly, there should be a new entry named `Photobash Images`. Check it, click `OK`, and restart Krita. There is now a new docker named "Photobash Images"! Place wherever you prefer. 

The plugin is now correctly installed! Click on "Set References Folder", and set the folder that contains all your references. After that, you're good to go! The plugin will recursively look inside your folder, so all the photos, even those that are stored inside different folders will show up! To know more about how to use the plugin to it's full potential, read the next chapter.

## Using the Plugin (really well)

After setting the references folder, you now have a list of 9 images in the docker, sorted alphabetically. If your folder has more than 9 images in total, there are now multiple pages. There are different ways to scroll the list, such as:
- Clicking on the "next" and "previous" buttons on the bottom row of the docker;
- Scrolling the slider next to the pages indicator;
- Mouse Wheel Up and Down;
- Alt + Drag Left or Right, in case you're using a stylus. 

If the images in the folders are of large size, there may be some slowdown when scrolling quickly. However, the plugin is caching the previews, and stores up to 90 images, so you can scroll through them back more easily later. 

To add an image to the document, all you'll have to do is click on the image. That's it! You can also drag the image to a specific position using Shift + Drag. After adding, you'll notice that the image might be scaled. To reduce needing to always transform to the correct size, there are two elements to assist you:

- The "Scale To Canvas" checkbox. This does exactly what you expect, and scales the image to fit the canvas. If the image is larger than the canvas, it scales it down, and if it's smaller, it scales it up! This can work in tandem with the next assistant;
- The "Image Scale" slider controls how large the image will be when it's placed. If the scale is 50%, with "Scale To Canvas" enabled, it will add the image with the maximum size of half the canvas. If "Scale To Canvas" is disabled, the image scale will be respect the original resolutions of the image. If it's 100%, it will add the image in full resolution, if it's 50% it will add the image at half the original resolution. 

Dragging the image presents the same behaviour as clicking, with the only difference being that the image will be added in the position you specify! It will always preserve aspect ratio, so there's no need to worry with distortion.

If you want to filter the images, you can add words to the text prompt on top of the widget. This filter will work on the full path of the image, so if you have images with random names, but are inside a folder called "rocks", if you input "rocks", those images will still appear. There's also an extra feature, in which mulitple word search adds to the selection. For example, if you input "rocks marble", the images that contain either "rocks" or "marble" will appear!

## Context Menu

You can also have some extra features by right-clicking on an image. This will open up a small menu, with several options: 
- **Preview in Docker**: This will maximize the selected image on the docker, to do a quick preview. You can close the preview by left-clicking the preview;
- **Pin to Beginning / Unpin**: You can add "favourites" to an image, by pinning them to the beginning. This is useful if you have a select few images that you like to re-use, but are on different pages. This way you can have an easy way to access them, which will persist across restarts. It will only forget the favourite images if you decide to change the references folder. You can also unpin the images to send them to their original placement. A favourite will have a triangle in the top-left corner.
- **Open as New Document**: Opens the image as a new document, but keep in mind that this is the original image. If you save it, it will override the one you have on your references folder. 
- **Place as Reference**: You can add an image as reference, and place it wherever you want! If you want to remove a reference, you need to press the "Pushpin Icon" on your toolbox, and remove it using that tool.
- **Add with Transparency**: Add the image with a transparency mask. White is to keep the pixels and Black is to erase. The added mask is white filled but the default behavior is to remove pixels if moving the transparency layer.
- **Group with Erase Layer**: Adds an image in a group with an erase blending layer. Easier to move compared to **Add with Transparency** butcan't add any additional images to the group without having the erase layer affect all images in the group.

#### Hope you enjoy this plugin, and feel free to post your artworks over on [Krita Artists](https://krita-artists.org/)!
