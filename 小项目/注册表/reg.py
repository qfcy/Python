import sys,os,winreg,ctypes
from warnings import warn
try:
    from shlex import join as join_args
except ImportError:
    def join_args(*args):
        return " ".join(f'"{arg}"' if ' ' in arg else arg for arg in args)
NoneType=type(None)


KEY = 0
VALUE = 1
DATA = 2
SEARCH_TYPE_MAP={0:"KEY",1:"VALUE",2:"DATA"}

TYPE_MAP={
    winreg.REG_EXPAND_SZ:str,
    winreg.REG_SZ:str,
    winreg.REG_DWORD:int,
    winreg.REG_QWORD:int,
    winreg.REG_QWORD_LITTLE_ENDIAN:int,
    winreg.REG_BINARY:bytes,
    winreg.REG_NONE:NoneType,
}
ROOT_KEYS = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
    "HKEY_USERS": winreg.HKEY_USERS,
    "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG,
}
SEARCH_IGNORES=[r"HKEY_LOCAL_MACHINE\Software\Classes", # 与HKEY_CLASSES_ROOT重复
                r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup" # 经测试，可能导致栈溢出 (Fatal Python error)
                ]

# 工具类 (utility)
class RedirectedOutput:
    def __init__(self,*streams):
        if not streams:raise ValueError("At least one stream should be provided")
        self._streams=streams
    def write(self,data):
        written=self._streams[0].write(data)
        result=written if written is not None else len(data)
        for stream in self._streams[1:]:
            written=stream.write(data)
            result=min(result,written if written is not None else result)
        return result
    def flush(self):
        for stream in self._streams:
            stream.flush()
    def isatty(self):
        return any(stream.isatty() for stream in self._streams)
class NotImplementedDict(dict):
    # pylint: disable=no-self-argument, no-member
    def notimp_wrapper(func_name):
        def notimplemented(self,*args,**kw):
            raise NotImplementedError(f"{func_name} not implemented in {type(self).__name__}")
        return notimplemented
    loc=locals()
    for attr in dict.__dict__:
        if attr in ("__new__","__getattribute__"):continue
        if callable(dict.__dict__[attr]):
            # pylint: disable=too-many-function-args
            loc[attr] = notimp_wrapper(attr)

    del loc,notimp_wrapper
    def __len__(self):
        return 0

def get_winreg_type(value):
    if isinstance(value, str):
        # 检测字符串类型（包括普通字符串和可扩展字符串）
        if '%' in value:  # 如果字符串中包含%，通常为可扩展字符串
            return winreg.REG_EXPAND_SZ
        return winreg.REG_SZ
    elif isinstance(value, bytes):
        return winreg.REG_BINARY
    elif isinstance(value, int):
        if value < (1 << 32) - 1:  # 32位整数范围
            return winreg.REG_DWORD
        elif value < (1 << 64) - 1:
            return winreg.REG_QWORD
        else:
            raise OverflowError("Value exceeds (1 << 64) - 1")
    elif isinstance(value, list):
        # 检测多字符串
        return winreg.REG_MULTI_SZ
    else:
        raise ValueError("Unsupported type: {}".format(type(value)))

class RegValue(NotImplementedDict):
    def __init__(self, node):
        self.node = node

    def __getitem__(self, name):
        try:
            value, type_id = winreg.QueryValueEx(self.node.key, name)
            if value is None:
                value = TYPE_MAP.get(type_id,NoneType)() # 默认值(如长度为0的二进制值等)
            return value
        except FileNotFoundError:
            raise KeyError(f"Value '{name}' not found in {self.node.path}") from None
    def get_type(self, name):
        try:
            _, type_id = winreg.QueryValueEx(self.node.key, name)
            return type_id
        except FileNotFoundError:
            raise KeyError(f"Value '{name}' not found in {self.node.path}") from None

    def __setitem__(self, name, value, reg_type=None):
        if reg_type is None:
            reg_type=get_winreg_type(value)
        winreg.SetValueEx(self.node.key, name, 0, reg_type, value)

    def __delitem__(self, name):
        try:
            winreg.DeleteValue(self.node.key, name)
        except FileNotFoundError:
            raise KeyError(f"Value '{name}' not found in {self.node.path}") from None

    def keys(self):
        return self
    def __iter__(self):
        i = 0
        while True:
            try:
                name, _, _ = winreg.EnumValue(self.node.key, i)
                if name != "": # 不包括default值("")
                    yield name
                i += 1
            except OSError:
                break
    def __contains__(self, name):
        try:
            # 尝试查询值以检查是否存在
            winreg.QueryValueEx(self.node.key, name)
            return True
        except FileNotFoundError:
            return False  # 值不存在
    def __eq__(self, other):
        if not isinstance(other,RegValue):
            return False
        keys1=list(self.keys())
        keys2=list(other.keys())
        if keys1!=keys2:return False
        for key in keys1:
            if self[key]!=other[key]: # 递归检查
                return False
        return True
    def __ne__(self, other):
        return not self == other
    def values(self):
        i = 0
        while True:
            try:
                name, data, _ = winreg.EnumValue(self.node.key, i)
                if name != "":
                    yield data
                i += 1
            except OSError:
                break

    def items(self):
        i = 0
        while True:
            try:
                name, data, _ = winreg.EnumValue(self.node.key, i)
                if name != "":
                    yield name, data
                i += 1
            except OSError:
                break
    def to_dict(self):
        dct={}
        for item in self:
            dct[item]=self[item]
        return dct
    def __str__(self):
        return f"<RegValue: {self.to_dict()}>"
    __repr__=__str__

class RegNode(NotImplementedDict):
    def __init__(self, path, readonly=False, create=True):
        self.path = path.replace('/', '\\').strip('\\')
        self.name = self.path.split('\\')[-1]
        self.key=None
        self.readonly=readonly
        permission = winreg.KEY_READ
        if not readonly:
            permission |= winreg.KEY_WRITE
        try:
            self.key = winreg.OpenKey(self._get_root_key(), self._get_subkey(), 0, permission)
        except FileNotFoundError:
            if create: # 键不存在时，自动创建新键
                self.key = winreg.CreateKey(self._get_root_key(), self._get_subkey())
            else:raise
        except ValueError:
            print(self.path)
            raise
    def _get_root_key(self):
        root = self.path.split('\\')[0]
        return ROOT_KEYS[root]

    def _get_subkey(self):
        return '\\'.join(self.path.split('\\')[1:])

    def __getitem__(self, subkey):
        try:
            return RegNode(f"{self.path}\\{subkey}",create=False)
        except FileNotFoundError:
            raise KeyError(f"Key {self.path}\\{subkey} not exist.") from None
    def __setitem__(self, subkey, node):
        if not isinstance(node,RegNode):
            raise TypeError("value should be a RegNode object")
        try:
            del self[subkey]
        except KeyError:pass
        newRegNode=self.create_key(subkey)
        if node.default is not None:
            newRegNode.default=node.default
        # 复制node到newRegNode
        for sub in node.keys():
            subRegNode=node[sub]
            newRegNode[sub]=subRegNode # 递归复制
        for name in node.values:
            newRegNode.values[name]=node.values[name]
    def __delitem__(self, subkey):
        try:
            subkey_node=self[subkey]
            for key in subkey_node.keys():
                del subkey_node[key] # 递归检查
            winreg.DeleteKey(self.key, subkey)
        except FileNotFoundError:
            raise KeyError(f"Key {self.path}\\{subkey} not exist.") from None
    def __contains__(self, subkey):
        try:
            key=winreg.OpenKey(self._get_root_key(), f"{self._get_subkey()}\\{subkey}", 0, winreg.KEY_READ)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
    def __eq__(self, other):
        if not isinstance(other,RegNode):
            return False
        if self.default != other.default:
            return False
        if self.values != other.values:
            return False
        keys1=list(self.keys())
        keys2=list(other.keys())
        if keys1!=keys2:return False
        for key in keys1:
            if self[key]!=other[key]: # 递归
                return False
        return True
    def __ne__(self, other):
        return not self == other

    def create_key(self,subkey): # 创建子键
        return RegNode(f"{self.path}\\{subkey}")
    def delete(self): # 删除自身
        self.release()
        parent=self.parent
        if parent is None:
            raise ValueError(f"cannot delete root node {self.path}")
        del parent[self.name]
    def release(self):
        if self.key:
            winreg.CloseKey(self.key)
        self.key=None
    __del__=release

    def to_dict(self):
        result={
            "default":self.default,
            "values":self.values.to_dict(),
            "subkeys":{}
        }
        for subkey in self.subkeys():
            result["subkeys"][subkey.name]=subkey.to_dict() # 递归
        return result
    @property
    def parent(self):
        split = self.path.split('\\')
        if len(split) == 1:
            return None # 已经是根节点
        return RegNode('\\'.join(split[:-1]))
    @property
    def default(self):
        try:
            value, type_id = winreg.QueryValueEx(self.key, '')
            if value is None:
                value = TYPE_MAP.get(type_id,NoneType)() # 默认值(如长度为0的二进制值等)
            return value
        except FileNotFoundError:
            return None

    @default.setter
    def default(self, value):
        if value is None:
            winreg.DeleteValue(self.key, '')
        else:
            winreg.SetValueEx(self.key, '', 0, winreg.REG_SZ, value)

    @property
    def values(self):
        return RegValue(self)
    def keys(self):
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(self.key, i)
                yield subkey_name
                i += 1
            except OSError:
                break
    __iter__ = keys
    def subkeys(self, readonly=False, suppress_error=False):
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(self.key, i)
                path = f"{self.path}\\{subkey_name}"
                try:
                    yield RegNode(path,create=False,readonly=readonly)
                except Exception as err:
                    if not suppress_error:
                        warn(f"Error opening key {path}: {err} ({type(err).__name__})")
                i += 1
            except OSError:
                break

    def __str__(self):
        result=", ".join(f"{key!r}: ..." for key in self.keys())
        return f"""<RegNode{" "+repr(self.default) if self.default is not None else ""}\
: {{{result}}} values: {self.values.to_dict()}>"""
    __repr__=__str__
    @classmethod
    def get_root_nodes(cls):
        nodes=[]
        for key in ROOT_KEYS:
            nodes.append(cls(key))
        return nodes

def _check_value(keyword, value, match_whole_str, case_sensitive):
    if not isinstance(value,str):
        return False
    if not case_sensitive:
        value=value.lower()
    return (match_whole_str and value == keyword) or \
           (not match_whole_str and keyword in value)
def _search_node(node, keyword, results, match_whole_str, case_sensitive,
                 cnt=0,show_progress=True):
    # 检查当前节点的默认值
    if _check_value(keyword,node.default,match_whole_str,case_sensitive):
        results.append((node.path,DATA,None))

    # 检查当前节点的值
    for name, value in node.values.items():
        if _check_value(keyword,name,match_whole_str,case_sensitive):
            results.append((node.path,VALUE,name))
        if _check_value(keyword,value,match_whole_str,case_sensitive):
            results.append((node.path,DATA,name))

    # 递归检查子节点
    for subkey in node.subkeys(suppress_error=True,readonly=True):
        cnt+=1
        if show_progress and cnt % 1000 == 0:
            print(f"已搜索 {cnt} 项, 找到 {len(results)} 个条目, 进度: {subkey.path}")
        ignore=False
        for item in SEARCH_IGNORES:
            if item.lower() in subkey.path.lower():
                ignore=True;break
        if ignore:continue

        if _check_value(keyword,subkey.name,match_whole_str,case_sensitive):
            results.append((subkey.path,KEY,None))
        cnt=_search_node(subkey, keyword, results, match_whole_str, case_sensitive,
                         cnt, show_progress)
    return cnt

def search_reg(keyword, start=None, match_whole_str=False, 
               case_sensitive=False,show_progress=True):
    results = [] # result的每一项为键路径、搜索类型、值名称的三元组
    start_nodes = []
    if start:
        start_nodes.append(RegNode(start))
    else:
        start_nodes.extend(RegNode.get_root_nodes())
    if not case_sensitive:
        keyword=keyword.lower()
    cnt=0
    for node in start_nodes:
        cnt=_search_node(node, keyword, results, match_whole_str, case_sensitive,
                     cnt,show_progress)

    return results

def run_doctest():
    r"""\
>>> node = RegNode(r"HKEY_CURRENT_USER\SOFTWARE\Python\pyregistry_doctest")
>>> node.default = "Default value"
>>> node.default
'Default value'
>>> reg_values = node.values
>>> reg_values["value1"] = "Hello"
>>> reg_values["value2"] = "World"
>>> # 检查值是否存在
>>> reg_values
<RegValue: {'value1': 'Hello', 'value2': 'World'}>
>>> assert "value1" in reg_values
>>> assert reg_values["value1"] == "Hello"
>>> assert reg_values["value2"] == "World"
>>> node.to_dict()
{'default': 'Default value', 'values': {'value1': 'Hello', 'value2': 'World'}, 'subkeys': {}}
>>>
>>> # 测试更新值
>>> reg_values["value1"] = "Changed"
>>> assert reg_values["value1"] == "Changed"
>>> assert list(reg_values.values()) == ["Changed", "World"]
>>> # 测试删除值
>>> del reg_values["value2"]
>>> assert "value2" not in reg_values
>>> assert list(reg_values.values()) == ["Changed"]  # 只剩下一个值
>>> # 测试值类型
>>> reg_values["value2"] = ["multi","sz"]
>>> reg_values["value2"]
['multi', 'sz']
>>>
>>> # 测试键复制
>>> subkey = node.create_key("subkey")
>>> subkey.create_key("subkey2").values["inner"]=42
>>> node2 = RegNode(r"HKEY_CURRENT_USER\SOFTWARE\Python\pyregistry_doctest2")
>>> node2["copied"] = node  # 复制 node
>>> assert node2["copied"] == node
>>> del node2["copied"].values["value1"]
>>> assert node2["copied"] != node
>>>
>>> node3 = RegNode(r"HKEY_CURRENT_USER")
>>> node3["pyregistry_doctest3"] = node
>>> assert node3["pyregistry_doctest3"] == node
>>>
>>> # 测试错误处理
>>> assert "non-existent" not in node2
>>> try: node2["non-existent"]
... except KeyError:print("success")
...
success
>>> try: node2.values["non-existent"]
... except KeyError:print("success")
...
success
>>> try: node3.delete()
... except ValueError:print("success")
...
success
>>>
>>> # 清理
>>> del node.parent["pyregistry_doctest"],node.parent["pyregistry_doctest2"]
>>> node3["pyregistry_doctest3"].delete()
"""
    pass  # doctest 的占位符

def test_search():
    while True:
        keyword=input("输入搜索关键词: ").strip()
        result=search_reg(keyword)
        with open("result.txt","w",encoding="utf-8") as f:
            output=RedirectedOutput(sys.stdout,f)
            for item,search_type,value_name in result:
                print(f"""{item} ({SEARCH_TYPE_MAP[search_type]}\
{' value: '+repr(value_name) if value_name is not None else ''})""",file=output)

def test_gui():
    from pyobject import browse
    browse(RegNode("HKEY_CURRENT_USER"))

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

if __name__ == "__main__":
    if not is_admin(): # 自动以管理员身份运行
        print("Re-run with admin ...")
        pauser=os.path.join(os.path.split(__file__)[0],"console_pauser.py")
        ctypes.windll.shell32.ShellExecuteW(None,"runas", sys.executable,
                                            join_args(*([pauser]+sys.argv)), None, 1)
        sys.exit()

    import doctest
    doctest.run_docstring_examples(run_doctest, globals(),
                                   optionflags=doctest.ELLIPSIS)
    test_search()