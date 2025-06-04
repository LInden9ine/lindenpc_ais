from passlib.context import CryptContext

password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


password = "1111"  # Замените на желаемый пароль
hashed_password = get_hashed_password(password)
print(hashed_password)
