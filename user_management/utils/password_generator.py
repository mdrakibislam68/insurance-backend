import random
import string


def generate_password(length=12):
    all_characters = string.ascii_letters + string.digits + string.punctuation
    password = []
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.digits))
    password.append(random.choice(string.punctuation))
    password += random.choices(all_characters, k=length - 4)
    random.shuffle(password)

    return ''.join(password)
