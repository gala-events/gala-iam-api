from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(source):
    """Generates hash out of the source

    Arguments:
        source {unicode} -- any string or unicode that needs to be hashed

    Returns:
        [str] -- generated hash of the source
    """
    return pwd_context.hash(source)


def verify_hash(source, target):
    """Verifies if the hash generated by source matches the target

    Arguments:
        source {unicode} -- source that needs to be tested
        target {unicode} -- target hash that needs to be tested against

    Returns:
        bool -- Returns true if the generated hash matches the target
    """
    return pwd_context.verify(source, target)
