import sys
from PIL import Image


'''

Implementation:
Encode & Decode functions

Encode function
input params: jpeg image, string of text
output params: png image with embedded text (with size of the text on bottom right 11 pixels)

details:
1). Validate params
2). Convert text and text length to binary
3). Use the bottom right 11 pixels to place text length
4). Use remaining pixels to store text

Decode function
input params: png image
output params: A string containing the embedded text in the png image

details:
1). Validate params
2). Extract text length from image - convert from binary to string
3). Extract text from image - convert from binary to string

'''

# Number of pixels to store the length of the input text.
TEXT_LEN_PIXELS = 11

# Enbeds text in an image
def encode(file_path, text):
    if not file_path.endswith(".jpeg") and not file_path.endswith(".jpg"):
        raise InvalidImageTypeException("Error: image to encode must be .jpg format")
    if not text.strip():
        raise ValueError("Input text must be non-empty and non-null.")

    # Input image
    before = Image.open(file_path)
    pixmap_before = before.load()

    '''
    Verify that the input text will fit into the image. We subtract the numer of pixels needed to 
    store the input text size, and then multiply the number of pixels by 3 because there are 3 RGB 
    values in each pixel, and each bit of input text will be placed in the LSB of each RGB value.
    '''
    text_bits = tobits(text)
    num_pixels = before.size[0] * before.size[1]
    if len(text_bits) > (num_pixels - 11) * 3:
        raise ValueError("Error: input text cannot fit in image.")

    # Result image
    after = Image.new(before.mode, before.size)
    pixmap_after = after.load()

    # Embed the input text in the image.
    after = encode_text(before, pixmap_before, after, pixmap_after, text_bits)

    return after


# Function to encode 'len bits' within the first 11 pixels starting from the bottom right of an image.
def encode_text(before, pixmap_before, after, pixmap_after, text_bits):

    # Get length (in bits) of the input text represented in bits. Then place on the bottom right 11 pixels.
    text_bits_len = len(text_bits)
    len_bits = bin(text_bits_len)[2:]
    index = len(len_bits) - 1
    for x in range(TEXT_LEN_PIXELS):
        # Get pixel values and convert them to their binary representations.
        r, g, b = pixmap_before[before.size[0] - x - 1, before.size[1] - 1]
        r_bin = int(bin(r), 2)
        g_bin = int(bin(g), 2)
        b_bin = int(bin(b), 2)

        if index - 2 >= 0:
            b_bin = set_bit(r_bin, 0) if len_bits[index] == 1 else clear_bit(r_bin, 0)
            g_bin = set_bit(r_bin, 0) if len_bits[index - 1] == 1 else clear_bit(r_bin, 0)
            r_bin = set_bit(r_bin, 0) if len_bits[index - 2] == 1 else clear_bit(r_bin, 0)
            index -= 2
        else:
            b_bin = clear_bit(b_bin, 0)
            g_bin = clear_bit(g_bin, 0)
            r_bin = clear_bit(r_bin, 0)

        pixmap_after[before.size[0] - x - 1, before.size[1] - 1] = (r_bin, g_bin, b_bin)

    # Encode remaining bits in the image.
    index = 0
    for x in range(before.size[0]):
        for y in range(before.size[1]):

            # Don't overwrite the input text length on the last 11 pixels.
            if y == before.size[1] -1 and x == before.size[0] - TEXT_LEN_PIXELS - 1:
                break

            # Get pixel values and convert them to their binary representations
            r, g, b = pixmap_before[x, y]
            r_bin = int(bin(r), 2)
            g_bin = int(bin(g), 2)
            b_bin = int(bin(b), 2)

            if index + 3 <= text_bits_len:
                r_bin = set_bit(r_bin, 0) if text_bits[index] == 1 else clear_bit(r_bin, 0)
                g_bin = set_bit(r_bin, 0) if text_bits[index + 1] == 1 else clear_bit(r_bin, 0)
                b_bin = set_bit(r_bin, 0) if text_bits[index + 2] == 1 else clear_bit(r_bin, 0)
                index += 3

            pixmap_after[x, y] = (r_bin, g_bin, b_bin)

    return after


# Decodes an image containing hidden text, if any exsits.
def decode(file_path):
    if not file_path.endswith(".png"):
        raise InvalidImageTypeException("Error: image to decode must be .png format")


# Function for extracting command line arguments.
def getopts(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


# Function to set a single bit in 'value' to 1.
def set_bit(value, bit):
    return value | (1 << bit)


# Function to set a single bit in 'value' to 0.
def clear_bit(value, bit):
    return value & ~(1 << bit)


# Function to convert a string into an array of bytes. Note that the input string must be in UTF-8 format.
def tobits(s):
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


# Function to convert from an array of bits to a String
def frombits(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)


# Custom exception class for invalid image types.
class InvalidImageTypeException(ValueError):
    def __init__(self, message):
        super().__init__(message)


# Custom exception class for invalid command line arguments
class IllegalArgumentError(ValueError):
    def __init__(self, message):
        super().__init__(message)


if __name__ == '__main__':
    from sys import argv
    args = getopts(argv)
    usage_msg = "Usage: ./file.py [-p <path to image>] [-e <text to insert>] [-d]"

    if '-p' not in args:
        raise IllegalArgumentError(usage_msg)
    if '-e' not in args and '-d' not in args:
        raise IllegalArgumentError(usage_msg)

    if '-e' in args:
        result = encode(args.get('-p'), args.get('-e'))
        result.show()
        result.save('output.png')

    elif '-d' in args:
        message = decode(args.get('-d'))
        print(message)