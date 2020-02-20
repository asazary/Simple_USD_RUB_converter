import unittest
import cbr_courses_funcs
from xml.etree.ElementTree import ParseError

test_courses_file_name = "test_courses.xml"
test_courses_incorrect_xml_file_name = "test_incorrect_xml_file.xml"
test_courses_incorrect_xml_data_file_name = "test_incorrect_xml_data.xml"
test_courses_no_needed_valute_file_name = "test_courses_not_needed_valulte.xml"
test_courses_incorrect_value_file_name = "test_incorrect_course_value.xml"


class TestXmlGetter(unittest.TestCase):
    def testMainUrlDoesntWorkSecondOK(self):
        self.assertIsInstance(cbr_courses_funcs.get_cbr_courses_xml("http://www.cbr.ru/scripts/XML_daily00000000.asp"),
                              bytes)

    def testBothUrlsDontWork(self):
        self.assertRaises(cbr_courses_funcs.CbrCoursesNotAvailableException,
                          cbr_courses_funcs.get_cbr_courses_xml,
                          "http://www.cbr.ru/scripts/XML_daily00000000.asp",
                          "http://www.cbr.ru/scripts/XML_daily11111111.asp")


class TestXmlParser(unittest.TestCase):
    def testIncorrectXml(self):
        with open(test_courses_incorrect_xml_file_name, "r") as f:
            incorrect_xml = f.read()

        self.assertRaises(ParseError,
                          cbr_courses_funcs.get_course_from_xml, incorrect_xml)

    def testIncorrectXmlData(self):
        with open(test_courses_incorrect_xml_data_file_name, "r") as f:
            incorrect_xml_data = f.read()

        self.assertRaises(cbr_courses_funcs.IncorrectXmlDataException,
                          cbr_courses_funcs.get_course_from_xml, incorrect_xml_data)

    def testNoNeededValute(self):
        with open(test_courses_no_needed_valute_file_name, "r") as f:
            no_needed_valute_xml = f.read()

        self.assertRaises(cbr_courses_funcs.IncorrectXmlDataException,
                          cbr_courses_funcs.get_course_from_xml, no_needed_valute_xml, "AAA")

    def testIncorrectCourseValue(self):
        with open(test_courses_incorrect_value_file_name, "r") as f:
            incorrect_course_xml = f.read()

        self.assertRaises(ValueError,
                          cbr_courses_funcs.get_course_from_xml, incorrect_course_xml)

    def testGetCourseFromXml(self):
        with open(test_courses_file_name, "r") as f:
            xml_data = f.read()

        self.assertEquals({"course": 63.7698, "date_of_course": "19.02.2020", "valute": "USD"},
                          cbr_courses_funcs.get_course_from_xml(xml_data=xml_data, valute_charcode="USD"))


class TestConverter(unittest.TestCase):
    def testConvert(self):
        self.assertAlmostEqual(cbr_courses_funcs.get_converted_value(7, 63.7698), 446.3886)


if __name__ == "__main__":
    unittest.main()
