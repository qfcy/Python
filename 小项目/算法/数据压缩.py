# 部分来自其他项目
import struct

# 压缩的元组的第一项是一个索引，引用之前已在字典中的旧子串，为-1则表示不引用
# 元组的第二项表示增加的新字符，可以为空值
# 解压时拼接第一项的旧子串和第二项的新字符串，加入解压结果中
def compress(message):
    tree_dict, m_len, i = {}, len(message), 0
    while i < m_len:
        # 不在已有字符中
        if message[i] not in tree_dict.keys():
            yield (-1, message[i]) # -1 表示没有引用前面的子串
            tree_dict[message[i]] = len(tree_dict)
            i += 1
        # 最后一个字符
        elif i == m_len - 1:
            yield (tree_dict.get(message[i]), '')
            i += 1
        else:
            for j in range(i + 1, m_len):
                # 增长子串并判断子串是否在字典出现，直到子串不在字典为止
                if message[i:j + 1] not in tree_dict.keys():
                    yield (tree_dict.get(message[i:j]), message[j])
                    tree_dict[message[i:j + 1]] = len(tree_dict)
                    i = j + 1
                    break
                # 最后一个字符
                elif j == m_len - 1:
                    yield (tree_dict.get(message[i:j + 1]), '')
                    i = j + 1
        #print(i,tree_dict)

def decompress(packed):
    unpacked, tree_dict = '', {}
    for index, ch in packed:
        if index == -1:
            unpacked += ch
            tree_dict[len(tree_dict)] = ch
        else:
            term = tree_dict.get(index) + ch
            unpacked += term
            tree_dict[len(tree_dict)] = term
        #print(index,ch,unpacked,tree_dict)
    return unpacked

def to_binary(packed_data):
    # 将压缩后的数据转换为二进制格式，要求字符范围必须为0~255
    # 找到所有正索引
    indices = [index for index, ch in packed_data if index >= 0]
    max_index = max(indices) if indices else 0

    # 判断使用 signed char 还是 short
    if max_index < 128:
        fmt = 'b';header = b'\x01'
    else:
        fmt = 'h';header = b'\x02'

    binary_data = bytearray()
    binary_data += header

    for index, ch in packed_data:
        if ch != '':
            # 如果有新增字符，先存储索引
            binary_data += struct.pack(fmt, index)
            # 再存储字符，假设为单字节字符
            binary_data += bytes((ord(ch),))
        else:
            # 如果没有新增字符，存储 -(index + 2)
            packed_index = -(index + 2)
            binary_data += struct.pack(fmt, packed_index)

    return bytes(binary_data)

def from_binary(binary_data):
    # 从二进制数据还原压缩后的 (index, char) 元组。
    if not binary_data:return []

    type_byte = binary_data[0]
    if type_byte == 1:
        fmt = 'b';size = 1
    elif type_byte == 2:
        fmt = 'h';size = 2
    else:
        raise ValueError("Unknown type mark")

    packed_data = []
    i = 1
    while i < len(binary_data):
        # 解压索引
        index = struct.unpack(fmt, binary_data[i:i+size])[0]
        if index >= -1:
            # 有新增字符，读取下一个字节作为字符
            if i >= len(binary_data):
                raise ValueError("Bad data format")
            ch = chr(binary_data[i+size])
            packed_data.append((index, ch))
            i += size + 1
        else:
            # 没有新增字符，原先的索引为 -(index + 2)，如-2表示原来的0
            original_index = - (index + 2)
            packed_data.append((original_index, ''))
            i += size
    return packed_data

if __name__ == '__main__':
    test_cases = ["abab","a"*16, # 1+2+3+4+5+1=16, (对于重复的字符串，字典内的子串长度会逐渐增加）
                  "中文"]
    binary_msg = [''.join(chr(char) for char in message.encode("utf-8"))
                  for message in test_cases] # 确保在0-255范围内，便于转为二进制
    for i in range(len(test_cases)):
        s = binary_msg[i]
        packed = list(compress(s))
        binary = to_binary(packed)
        print(test_cases[i], ":", packed,binary,
              "压缩率: %.2f%%" % (len(binary)/len(s)*100))
        unpacked = decompress(from_binary(binary))
        assert unpacked == s
