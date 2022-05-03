import xlrd
import math
import copy
 
def loaddataset(filename):
	wb = xlrd.open_workbook(filename)
	ws = wb.sheet_by_name('Sheet1')
	dataset = []
	for r in range(ws.nrows):
		co1 = []
		for c in range(1, ws.ncols):
			co1.append(ws.cell(r,c).value)
		dataset.append(co1)
 
	#记录所有的属性名
	attribute_name = dataset.pop(0)
	del(attribute_name[-1])
	return dataset, attribute_name
 
def EntD(dataset):
	#对正例数量计数
	count = 0
	for i in dataset:
		if i[-1] == '是':
			count += 1
 
	#计算正反例所占比例
	p0 = 1 - count / len(dataset)
	p1 = 1 - p0
 
	#当占比为0时，根据信息熵的公式趋近于正无穷
	#这里我们用999代替正无穷
	if p0 == 0:
		entd0 = 999
		entd1 = 0
	elif p1 == 0:
		entd0 = 0
		entd1 = 999
	else:
		entd0 = -p0 * math.log(p0, 2)
		entd1 = -p1 * math.log(p1, 2)
	return entd0 + entd1
 
#n表示统计的属性的位置
def statistics(dataset, n):
	#记录统计结果
	count = {}
	for i in dataset:
		if i[n] not in count:
			#列表第一个位置为正例个数，第二个位置是反例个数
			if i[-1] == '是':
				count[i[n]] = [1, 0]
			else:
				count[i[n]] = [0, 1]
		else:
			if i[-1] == '是':
				count[i[n]][0] += 1
			else:
				count[i[n]][1] += 1
	return count
 
def EntDv(count):
	#记录结果
	entdv = []
	for i in count:
		p0 = count[i][1] / sum(count[i])
		p1 = count[i][0] / sum(count[i])
 
		#根据信息熵的定义，占比为0是应该是正无穷，占比为1应该是0
		#但是我们认为在该情况下，我们可以忽略该取值的信息对属性整体信息量的影响
		#所以出现这种情况时，该取值的信息熵为0
		#所以这里不再使用if判断，而是使用差错控制语句实现
		try:
			entd0 = -p0 * math.log(p0, 2)
			entd1 = -p1 * math.log(p1, 2)
			entdv.append([entd0 + entd1, sum(count[i])])
		except:
			entdv.append([0, sum(count[i])])
	return entdv
 
def GainD(entd, entdv, n):
	m = 0
	for i in entdv:
		m += i[1] / n * i[0]
	return entd - m
 
def choose(dataset, attribute_name):
	#记录所有属性的信息增益
	gaind_set = []
	for i in range(len(attribute_name)):
		entd = EntD(dataset)
		count = statistics(dataset, i)
		entdv = EntDv(count)
		gaind_set.append(GainD(entd, entdv, len(dataset)))
 
	#找其中的最大值
	a = max(gaind_set)
 
	#确定最大值的位置，从而确定是哪个属性
	k = gaind_set.index(a)
 
	#记录属性名
	label = attribute_name[k]
 
	#更新数据集，根据选择的属性的不同取值，分为对个子数据集
	#使用字典类型存储
	data_set = {}
	for i in dataset:
		#选择过的属性，不再使用，所以我们把它删了
		if i[k] not in data_set:
			a = i.pop(k)
			data_set[a] = [i]
		else:
			a = i.pop(k)
			data_set[a].append(i)
 
	#属性标签的列表中也将选择的属性删除，不再使用
	#为了不改变原始的数据，使用deepcopy更新出新的属性标签列表
	attribute_name_new = copy.deepcopy(attribute_name)
	del(attribute_name_new[k])
	return data_set, attribute_name_new, label
 
def create_tree(tree, dataset, attribute_name):
	#当数据集的信息熵为正无穷大时，数据集分类唯一
	#创建叶子结点，结点数据为类别标签
	if EntD(dataset) == 999:
		tree.append(dataset[0][-1])
	else:
		#数据集不是唯一分类时，选择当前数据集的最优划分属性
		data_set, attribute_name_new, label = choose(dataset, attribute_name)
		if len(attribute_name_new) != 0:
			#划分后，每一个划分子集，对应一个中间结点，结点数据为属性标签
			for i in data_set:
				tree.append([label+i])
				create_tree(tree[-1], data_set[i], attribute_name_new)
 
if __name__ == '__main__':
	dataset , attribute_name = loaddataset('西瓜.xlsx')
	tree = []
	create_tree(tree, dataset, attribute_name)
	print(tree)