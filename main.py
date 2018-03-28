import sys
import argparse
from PIL import Image


# Number of pixels to store the length of the input text.
TEXT_LEN_PIXELS = 11

# Mask to extract least significant bit of an 8-bit binary number
MASK = 0b0000001

def encode(file_path, text):
    """
    Encodes text in an image. More specifically, the text is embedded in the least significant bit
    of each RGB value within each pixel of an image. The bottom right 11 pixels of the image are
    reserved for storing the length of the text.

    :param file_path: The relative path to the image.
    :param text: The text to encode into the image.
    :return: An image object, containing the embedded text.
    """
    if not file_path.endswith(".jpeg") and not file_path.endswith(".jpg"):
        raise InvalidImageTypeException("Error: image to encode must be .jpg format")
    if not text.strip():
        raise ValueError("Input text must be non-empty and non-null.")

    # Input image
    before = Image.open(file_path)
    pixmap_before = before.load()

    '''
    Verify that the input text will fit into the image. We subtract the number of pixels needed to 
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
    # TODO: merge this and the 'encode' function together.

    # Get length (in bits) of the input text represented in bits. Then place on the bottom right 11 pixels.
    text_bits_len = len(text_bits)
    len_bits = bin(text_bits_len)[2:]
    index = len(len_bits) - 1
    for x in range(TEXT_LEN_PIXELS):
        r_bin, g_bin, b_bin = get_pixels_bin(pixmap_before, before.size[0] - x - 1, before.size[1] - 1)

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

            r_bin, g_bin, b_bin = get_pixels_bin(pixmap_before, x, y)

            if index + 3 <= text_bits_len:
                r_bin = set_bit(r_bin, 0) if text_bits[index] == 1 else clear_bit(r_bin, 0)
                g_bin = set_bit(r_bin, 0) if text_bits[index + 1] == 1 else clear_bit(r_bin, 0)
                b_bin = set_bit(r_bin, 0) if text_bits[index + 2] == 1 else clear_bit(r_bin, 0)
                index += 3

            pixmap_after[x, y] = (r_bin, g_bin, b_bin)

    return after


def decode(file_path):
    """
    Decodes an image containing hidden text, if any hidden text exists.

    :param file_path: The relative path to the image.
    :return: The text embedded in the image. If no text exists, then an empty
    string will be returned.
    """
    if not file_path.endswith(".png"):
        raise InvalidImageTypeException("Error: image to decode must be .png format.")

    img = Image.open(file_path)
    pixmap = img.load()

    length_in_bits = ''
    for x in range(TEXT_LEN_PIXELS):
        r_bin, g_bin, b_bin = get_pixels_bin(pixmap, img.size[0] - x - 1, img.size[1] - 1)
        length_in_bits += str(b_bin & MASK)
        length_in_bits += str(g_bin & MASK)
        length_in_bits += str(r_bin & MASK)

    return int(length_in_bits)


def get_pixels_bin(pixmap, x, y):
    """ 
    Returns 3 RGB values from a pixel map at the specified x and y coordinates. Note that these values
    are returned as binary numbers.
    
    :param pixmap: A PIL image access object.
    :param x: The x coordinate of the pixel.
    :param y: The y coordinate of the pixel.
    :return: Three RGB values represented as binary numbers.
    """""

    r, g, b = pixmap[x, y]
    r_bin = int(bin(r), 2)
    g_bin = int(bin(g), 2)
    b_bin = int(bin(b), 2)
    return r_bin, g_bin, b_bin


def set_bit(value, bit):
    """
    Sets a single bit in 'value' to 1.
    :param value: The number.
    :param bit: The bit to set to 1.
    :return: The value with one of its bits set to 1.
    """
    return value | (1 << bit)


def clear_bit(value, bit):
    """
    Sets a single bit in 'value' to 0.
    :param value: The number.
    :param bit: The bit to set to 0.
    :return: The value with one of its bits set to 0.
    """
    return value & ~(1 << bit)


def tobits(s):
    """
    Converts a string into a list of bits. Note that the input string must be in UTF-8 format.
    :param s: The string to convert.
    :return: A list of bits.
    """
    result = []
    for c in s:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


def frombits(bits):
    """
    Converts an array of bits to an integer string.
    :param bits: The list of bits to convert.
    :return: A string with the integer value of the bits.
    """
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


# Driver function
if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='./PySteg [path] [-e string] [-d] [-h]')
    parser.add_argument('path', help='The relative path of the image to use')
    parser.add_argument('-e', '--encode', help='Text to encode in an image')
    parser.add_argument('-d', '--decode', help='Decode from an image', action='store_true')
    args = parser.parse_args()

    if args.encode:
        result = encode(args.path, args.encode)
        result.show()
        result.save('output.png')
    elif args.decode:
        length = decode(args.path)
        print(length)