from uniqueCommaSeperatedList import uniqueCommaSeperatedListClass
import unittest
from TestHelperSuperClass import testHelperSuperClass

class test_uniqueCommaSeperatedList(testHelperSuperClass):
  def test_emptyList(self):
    tl = "    "
    obj = uniqueCommaSeperatedListClass(tl)
    self.assertEqual(obj.toString(),"")

  def test_combineTwoEmptyLists(self):
    tl = "    "
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"")

  def test_singleItemList(self):
    tl = "aaa"
    tl2 = "bbb"
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"aaa")
    obj.addList(tl2)
    self.assertEqual(obj.toString(),"aaa, bbb")

  def test_itemsAreUnique(self):
    tl = "aaa"
    tl2 = "aaa"
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"aaa")
    obj.addList(tl2)
    self.assertEqual(obj.toString(),"aaa")

  def test_twoItemList(self):
    tl = "aaa, aaa2"
    tl2 = "bbb, bbb2"
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"aaa, aaa2")
    obj.addList(tl2)
    self.assertEqual(obj.toString(),"aaa, aaa2, bbb, bbb2")

  def test_threeItemList(self):
    tl = "aaa, aaa2, aaa3"
    tl2 = "bbb, bbb2,bbb3"
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"aaa, aaa2, aaa3")
    obj.addList(tl2)
    self.assertEqual(obj.toString(),"aaa, aaa2, aaa3, bbb, bbb2, bbb3")

  def test_addSingleItem(self):
    tl = "aaa, aaa2, aaa3"
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addItem("ffff ggggg") #items can have commas
    self.assertEqual(obj.toString(),"aaa, aaa2, aaa3, ffff ggggg")

  def test_addSingleItemCommaFails(self):
    tl = "aaa, aaa2, aaa3"
    obj = uniqueCommaSeperatedListClass(tl)
    with self.assertRaises(Exception) as context:
      obj.addItem("ffff,ggggg") #items can have commas
    self.checkGotRightExceptionType(context,Exception)

  def test_createAndAddFromListType(self):
    tl = ["aaa"]
    tl2 = ["bbb"]
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"aaa")
    obj.addList(tl2)
    self.assertEqual(obj.toString(),"aaa, bbb")

  def test_createAndAddFromListType(self):
    tl = ["aaa", "aaa2"]
    tl2 = ["bbb", "bbb2"]
    obj = uniqueCommaSeperatedListClass(tl)
    obj.addList("    ")
    self.assertEqual(obj.toString(),"aaa, aaa2")
    obj.addList(tl2)
    self.assertEqual(obj.toString(),"aaa, aaa2, bbb, bbb2")
