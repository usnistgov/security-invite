import os
import hmac
import hashlib


### ---------------------------------------------------------------------------|

def interlace(array1:list, array2:list) -> list:
    """ Interlacing method only added to demonstrate that the custom 
        'clever improvements' of the existing standards of password 
        hashing do not significantly complicate hash search with 
        rainbow tables
    Args:
        array1 (list): the first array to interlace
        array2 (list): the second array to interlace
    Returns:
        list: the new list containing the two input arrays interlaced
    """
    result = []
    lesser_len = min(len(array1), len(array2))
    for i in range(lesser_len):
        result.append(array1[i])
        result.append(array2[i])
    if len(array1) > len(array2):
        result.extend(array1[lesser_len:])
    elif len(array1) < len(array2):
        result.extend(array2[lesser_len:])
    return result
### ---------------------------------------------------------------------------|


class PasswordOperations(object):
    """ Aggregator-Class for all Password Crypto operations
    Args:
        object (_type_): Bases on an object as base
    """

    def __init__(self, sha_version:str = 'sha256', iterations:int = 100_000) -> None:
        """ Builds object for password crypto operations
        Args:
            sha_version (str, optional): String 'sha256'| 'sha512'. Defaults to 'sha256'.
            iterations (int, optional): _description_. Defaults to 100,000.
        """
        super().__init__()
        sha_allowed = ['sha256','sha512',]
        self.sha_version = sha_version if sha_version in sha_allowed else 'sha256'
        self.iterations = iterations if iterations>20_000 else 20_000
    ### -----------------------------------------------------------------------|

    def is_password_same(self, input_password:str, db_password_hash: str, db_password_salt: str) -> bool:
        input_pwd_hash, _ = self.hash_password(input_password, db_password_salt)
        return (input_pwd_hash == db_password_hash)
    ### -----------------------------------------------------------------------|

    def hash_password(self, password:str, salt:str) -> tuple[str, str]:
        salt_bytes = bytes.fromhex(salt)          # FYI: bytes.fromhex(salt.hex()) == salt
        password_bytes = password.encode("utf-8")
        password_hash = hashlib.pbkdf2_hmac(
                                    self.sha_version, 
                                    password_bytes, 
                                    salt_bytes, 
                                    self.iterations)
        return (password_hash.hex(), salt_bytes.hex())
    ### -----------------------------------------------------------------------|

    def hash_new_password(self, password: str) -> tuple[str, str]:
        """ For the new password generate new salt and call has_password
        Args:
            password (str): the new password to hash
        Returns:
            tuple[PWD_HASH:str, SALT:str]: the tuple containing bytes.hex() representations of the password-hash and salt
        """
        salt = os.urandom(32)
        return self.hash_password( password, salt.hex() )
    ### -----------------------------------------------------------------------|
### ===========================================================================|

### ===========================================================================|
### ======================      TESTING FUNCTIONS       ======================
def print_arrays_stats(a, b, ab):
    print(f'{len(a)=}\n{len(b)=}\n{len(ab)=}\n{ab=}')

def test_interlace1() -> None:
    pwd = 'Password1!'
    salt = os.urandom(16)
    p256 = hashlib.pbkdf2_hmac('sha256', pwd.encode('utf-8'), salt,100_000)
    a, b = list(salt), list(p256)
    ab = interlace(a, b)
    print_arrays_stats(a, b, ab,)
    ba = interlace(b, a)
    print_arrays_stats(b, a, ba,)

def test_interlace2() -> None:
    a = [1,2,3,4,5,6,7,8,]
    b = [11, 12,0]
    ab = interlace(a, b)
    print_arrays_stats(a, b, ab,)
    ba = interlace(b, a)
    print_arrays_stats(b, a, ba,)

def print_pass_info(algo, password, pass_salt)->None:
    print(f'\n{algo=}\n\t{password=}\n\tpass_hash={pass_salt[0]}\n\tsalt={pass_salt[1]}')


def test_hashing() -> None:
    p512 = PasswordOperations('sha512',)
    p256 = PasswordOperations('sha256',)
    password = 'Password1!'
    print_pass_info('SHA-512', password, p512.hash_new_password(password))
    print_pass_info('SHA-256', password, p256.hash_new_password(password))
### ===========================================================================|

if __name__ == "__main__":
 
    test_interlace1()
    test_interlace2()
    test_hashing()