import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# 可选字符集，用于生成随机字符串
_AES_CHARS = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"


def random_string(n):
    return ''.join(random.choice(_AES_CHARS) for _ in range(n))


def get_aes_string(plain, key_str, iv_str):
    # 去除左右空格
    key_str = key_str.strip()
    # 将key和iv转换成utf-8字节
    key_bytes = key_str.encode('utf-8')
    iv_bytes = iv_str.encode('utf-8')
    # 根据CryptoJS处理，要求key为16字节，如果不足则右侧补0，多余则截取前16字节
    if len(key_bytes) != 16:
        key_bytes = (
            key_bytes[:16] if len(key_bytes) > 16 else key_bytes.ljust(16, b'\0')
        )
    # AES CBC模式
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    # PKCS7填充
    padded_text = pad(plain.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_text)
    # 返回Base64字符串，与CryptoJS的输出格式一致，总以"="结尾
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def encrypt_aes(plain, salt):
    if salt:
        # 随机字符串64位加上明文，使用salt作为加密key，随机16位字符串作为初始向量
        new_plain = random_string(64) + plain
        iv = random_string(16)
        return get_aes_string(new_plain, salt, iv)
    else:
        return plain


def encrypt_password(password, salt):
    try:
        return encrypt_aes(password, salt)
    except Exception:
        return password


# 示例调用
if __name__ == "__main__":
    # 假设salt为16位字符串，实际可直接传入（例如："ofiW5m3MizLRuhNA"）
    salt = "ofiW5m3MizLRuhNA"
    plain_password = str(input("请输入密码:"))
    encrypted = encrypt_password(plain_password, salt)
    print("加密结果:", encrypted)
