from charm.toolbox.pairinggroup import PairingGroup, GT
from __init__ import KPABE

# 1. 初始化
group = PairingGroup('SS512')
abe = KPABE(group, uni_size=5)

# 2. 系统初始化
pk, msk = abe.setup()

# 3. 明文消息
msg = group.random(GT)

# 4. 加密，属性集合为 ['1', '2']
print("加密前：", msg)
ctxt = abe.encrypt(pk, msg, ['1', '2'])

# 5. 生成密钥，策略为 '1 and 2'
key = abe.keygen(pk, msk, '1 and 2')
print("密钥：", key)

# 6. 解密
decrypted = abe.decrypt(pk, ctxt, key)
print("解密结果：", decrypted)
print("解密是否成功：", decrypted == msg)

# 7. 用不满足策略的密钥尝试解密
key_fail = abe.keygen(pk, msk, '1 and 3')
print("不满足策略的密钥：", key_fail)
decrypted_fail = abe.decrypt(pk, ctxt, key_fail)
print("解密结果：", decrypted_fail)
print("不满足策略时解密结果：", decrypted_fail)