import string
import random # Might upgrade to cryptographically safe random module
import math

# Variables
chars = {}
alphabet = list('abcdefghijklmnopqrstuvwxyz')
key = ""

# Method to convert numbers to base32 numerical system
def base32(n: int = 0, *, decrypt: bool = False, c: str = '') -> str:
    # Result array
    result = []

    # base32 key
    b32_key = list('0123456789abcdefghijklmnopqrstuv')

    # If decrypting
    if decrypt:
        if len(c) > 1:
            n += (b32_key.index(c[0])) * 32
            c = c[1:]
            n += b32_key.index(c)
            return n
        else:
            return b32_key.index(c)
    
    # If encrypting

    # Get number of times the passed number exceeds the max number a single character can hold
    m = math.floor(n / (len(b32_key)))

    # If the passed number exceeds the max number at least once handle accordingly
    if m > 0:
        # Append to result array for the 32nd place
        result.append(b32_key[m])

        # Append to result array in the ones place
        result.append(b32_key[n - (m * 32)])

        # Return result
        return ''.join(result)
    
    # Return result
    return b32_key[n]


# for x in range(101):
#     encoded = base32(x)
#     decoded = base32(decrypt = True, c = encoded)
#     if decoded != x:
#         print("Decoded value does not match expected result.")
#     print(f"Encoded: {encoded}")
#     print(decoded)
#     print("\n\n")

# quit()

# Method for random number generation (inclucive of end-points)
def rng(min: int, max: int) -> int:
    return random.randint(min, max)

# Method to add salt to output
def salt(s: str) -> str:
    # Make key global
    global key

    #Variables
    s1 = ""
    s2 = ""
    added = 0

    # Get random offset from key
    offset_n = base32(decrypt = True, c = key[-1])

    # Add random characters to string every offset_n characters
    for n in range(len(s)):
        # If the character is at the increment and isn't index 0
        if n % offset_n == 0 and n != 0:
            s1 = s[:n + added]
            s2 = s[n + added:]
            s = s1 + string.printable[rng(0,92)].upper() + s2
            
            added += 1
    return s

# Generate substitution array
def gen_sub_arr(k: str = "") -> None:
    # Bring key in as a global variable
    global key

    # Generate random characters from string.printable
    for i in range(26):
        # Generate random number
        n = rng(0, 92)
        
        # Get random character
        c = string.printable[n].upper()

        # If character has already been generated then generate a new one
        while c in chars:
            # print("Character already in dictionary")
            # Generate new character
            n = rng(0, 92)
            c = string.printable[n].upper()

        # Append new char to chars array
        chars[c] = n

        # Check if the generated number is greater than 31
        if n > 31:
            # Add character to indicate that next 2 characters summed give the index in string.printable of character
            key += '~'

            # Add base32 value to key
            key += base32(n)
        else:
            # Add the character to represent the index
            key += base32(n)

    return None

# Method to encrypt
def encrypt(message: str) -> str:
    # Convert message to lowercase for ease of encryption and decryption
    message = message.lower()

    # Convert message to array
    new_message = list(message)

    # Substitute characters
    for n in range(len(alphabet)):
        # Get letter
        letter = alphabet[n]

        # Loop through message and replace all occurances of letter with substitution character
        for i, c in enumerate(message):
            # If current character of index is the current letter
            if c == letter:
                # Replace character with substitution character
                new_message[i] = list(chars.keys())[n]

    return ''.join(new_message)

# Method to decrypt
def decrypt(message: str, k: str = "") -> str:
    # Variables
    s = message
    index_arr = []
    value_arr = []

    '''
    Removing salt from encrypted message
    '''

    # Get values real offset values from key
    salt_offset = base32(decrypt = True, c = k[-1])

    # Remove salt
    for n in range(len(message)):
        # If the character
        if n % salt_offset == 0 and n != 0:
            s = s[:n] + s[n + 1:]

    '''
    Grabbing decryption portion of key
    ''' 
    # print(k)
    # Remove padding from front of key
    padding_key = k[0]
    padding_amt = base32(decrypt = True, c = padding_key)
    k = k[padding_amt + 1:]

    # Remove padding from back of key
    decryption_key = k[:-padding_amt - 1]

    '''
    Populate index array
    '''
    
    done = False
    i = 0
    v = decryption_key[i]
    loops = 1

    # While not done
    while not done:
        # If value is not a indicator character
        if v != '~':
            index_arr.append(base32(decrypt = True, c = v))
            i += 1
        # If value indicates that next two values should be summed
        elif v == '~':
            index_arr.append(base32(decrypt = True, c = decryption_key[i+1:i+3]))
            i += 3

        # Check if index has surpassed the last index of the array
        if i > len(decryption_key) - 1:
            done = True
            continue

        # Get new value
        v = decryption_key[i]

        loops += 1

    '''
    Decrypt message
    '''
    # Turn message variable into list
    s = list(s)

    # Characters
    characters = string.printable[0:93].upper()

    # Loop through the indices in index_arr
    for i in index_arr:
        # Get the substitution character from the substitution array by looking at the index
        v = characters[i]

        # Append value to value array
        value_arr.append(v)


    new_s = s.copy()

    # Loop through value array to decrypt message
    for i, v in enumerate(value_arr):
        # Loop through characters in message
        for c in new_s:
            # If value coincides with character in message
            if v == c:
                # Get index of character
                j = s.index(c)

                # Replace character with real character
                s[j] = alphabet[i]

    return ''.join(s)

# Setup method
def setup() -> None:
    # Pull key in as a global variable
    global key

    # Generate random amount of padding
    n = rng(1,9)

    # Encrypt padding number
    padding = base32(n)

    # Add padding variable to key
    key += padding

    # Generate padding for key
    for _ in range(n):
        key += base32(rng(0,25))

    # Call method to generate substitution array
    gen_sub_arr()

    # Add padding between decryption portion and increment portion
    for _ in range(n):
        key += base32(rng(0,25))

    # Generate increment value
    offset = rng(1,10)

    # Encrypt increment value and add it to key
    key += base32(offset)

    return None


# Run
if __name__ == "__main__":
    # Ask user if they want to encrypt or decrypt a message
    if input("Would you like to (E)ncrypt or (D)ecrypt a message?\n>> ").lower() == 'e':
        # Get message from user
        message = input("Enter the message you would like to encrypt: ")
        
        # Setup the encryption
        setup()

        # Encrypt the message
        message = encrypt(message)

        # Salt the encrypted message
        message = salt(message)

        # Ask user if they want to output the key and encrypted message to a file or console
        if input("Would you like to output the message and key to a (F)ile or (C)onsole?\n>> ").lower() == 'f':
            # Open file to store message
            with open("encrypted_message.txt", "w") as msg_f:
                # Write message to file and close file
                msg_f.write(message)
                msg_f.close()
            
            # Open file to store key
            with open("encryption_key.txt", "w") as key_f:
                # Write key to file and close file
                key_f.write(key)
                key_f.close()
        else:
            # Print the encrypted message and key
            print(f"Encrypted Message: {message}")
            print(f"Key: {key}")
    else:
        # Ask user if they want to read in from files or input into the consoleD
        if input("How would you like to input the data? (F)ile or (C)onsole?\n>> ").lower() == 'f':
            # Open file where message is stored
            with open("encrypted_message.txt", "r") as msg_f:
                # Get message from file and close file
                message = msg_f.readline()
                msg_f.close()
            
            # Open file where key is stored
            with open("encryption_key.txt", "r") as key_f:
                # Get key from file and close file
                key = key_f.readline()
                key_f.close()
        else:
            # Get message and key from user through console
            message = input("Enter the encrypted message: ")
            key = input("Enter the key: ")

        # Decrypt the message
        message = decrypt(message, k = key)

        # Display decrypted message
        print(f"Decrypted Message: {message}")

