# 使用缓存优化算法
# 递归算法中有很多重复的计算，这些计算不仅占用额外资源，还会降低函数执行效率，因此需要对递归进行优化。这里选用缓存优化法提升函数执行效率。
# 基本思路是每次找到结点关系后将此条目的编号添加到一个列表中缓存起来，代表此条目已找到结点关系。当往复循环执行函数时再次遇到此条目可以跳过。
# 代码改动很简单，增加一个缓存列表和控制流语句即可：

#使用缓存优化算法，会出现数据为空的现象，暂时先不采用

#格式化树
def generate_tree(source, parent):
    tree = []
    for item in source:
        if item["parent_id"] == parent:
            item["children"] = generate_tree(source, item["id"])
            tree.append(item)
    return tree



"""
判断是否还有子分类，删除使用
返回True  表示下面没有子分类，可以删除
返回False 表示下面还有子分类，不能删除
"""
def has_parent_data(source, id, parent):

    print("函数里面的id值: " + str(id))
    print("函数里面的parent值: " + str(parent))


    for item in source:
        if item["parent_id"] == id:
            return False
            break

    return True
