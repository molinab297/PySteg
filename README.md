# PySteg
A steganography tool to encode and decode hidden text in images. Requires Pillow (PIL fork) and Python 3.

## Author: Blake A. Molina (CWID: 890198401)

## Application Architecture: 
This program takes as input a path to a jpeg image and a string of characters. It then does three things before embedding the text in the image:

1). The input text is converted into an array of bits.
2). The number of pixels needed to store the array of bits is then computed. This information is later used by the decode function to loop over those pixels to read the text from.
3). The results from step 2 are converted to binary, and then stored in the bottom right 11 pixels.

Once all of this information has been computed, the program then loops through all of the pixels in the image and embedds the text in the least significant bit of each RGB value within each pixel. Pixels where no data is to be embedded are simply copied over from the original image.
 
## Execution Instructions:
usage: ./PySteg [path to image] [-e string] [-d] [-h]

positional arguments:
  path			The relative path of the image to use

optional arguments:
  -h, --help		show this help message and exit
  -e TEXT, --encode TEXT
			Text to encode in the image
  -d, --decode		Decode from an image

Example of embedding text in an image: python PySteg.py res/cat1.jpg -e "Steganography is fun :-)"
Example of decoding text from an image: python PySteg.py output.png -d

Note: the output image is saved to the same directory that you execute PySteg.py in.

