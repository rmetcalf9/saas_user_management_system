#tests the autoconfig steps
import TestHelperSuperClass
import autoConfigRunner as autoConfig
from appObj import appObj
from unittest.mock import Mock, patch, call

class helpers(TestHelperSuperClass.testHelperAPIClient):
  def assertNextLine(self, mocked_print, cur_line, expected):
    self.assertEqual(mocked_print.mock_calls[cur_line], call(expected))
    return cur_line + 1

  def assertHead(self, mocked_print):
    # returns number of lines
    l = 0
    l = self.assertNextLine(mocked_print, l, '\n----------------------------')
    l = self.assertNextLine(mocked_print, l, 'Running autoconfig...')
    l = self.assertNextLine(mocked_print, l, '----------------------------')
    return l

  def assertTail(self, mocked_print, l):
    l = self.assertNextLine(mocked_print, l, '----------------------------')
    l = self.assertNextLine(mocked_print, l, 'Autoconfig run complete')
    l = self.assertNextLine(mocked_print, l, '----------------------------\n\n')

    if len(mocked_print.mock_calls) == l:
      return
    self.assertEqual(l, len(mocked_print.mock_calls), msg="Not enough lines in output (next line=" + str(mocked_print.mock_calls[l]) + ")")

@TestHelperSuperClass.wipd
class test_appObjClass(helpers):
#Actual tests below

  def test_Echo(self):
    testType = "echo"
    testStepData = {"text": "Test Text To Echo"}
    autoConfigRunner = autoConfig.AutoConfigRunner(
      {"steps": [{ "type": testType, "data": testStepData}]}
    )
    with patch('builtins.print') as mocked_print:
      autoConfigRunner.run(appObj)
    l = self.assertHead(mocked_print)
    l = self.assertNextLine(mocked_print, l, 'Echo: Test Text To Echo')
    self.assertTail(mocked_print, l)
