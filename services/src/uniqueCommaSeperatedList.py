# Used for comma seperated lists where contents
#  need to be unique


class uniqueCommaSeperatedListClass():
  data = None

  def __init__(self, initialList):
    self.data = {}
    self.addList(initialList)

  def addList(self, listOrCommaSeperatedListToAdd):
    if isinstance(listOrCommaSeperatedListToAdd, list):
      return self._addList(listOrCommaSeperatedListToAdd)
    a = listOrCommaSeperatedListToAdd.split(",")
    return self._addList(a)

  def _addList(self, listToAdd):
    for x in listToAdd:
      xx = x.strip()
      if len(xx)>0:
        self.data[xx] = xx

  def addItem(self, item):
    if "," in item:
      raise Exception("Can't add items with commas")
    self.data[item] = item

  def toString(self):
    res = ""
    fir = True
    for a in self.data:
      if not fir:
        res += ", "
      res += a
      fir = False
    return res
