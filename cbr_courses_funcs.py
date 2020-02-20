import urllib3
import config
import logging
import xml.etree.ElementTree as ET
from typing import Union, Optional
from datetime import date
import json


logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(config.log_file_name)
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)
c_format = logging.Formatter(config.log_c_format)
f_format = logging.Formatter(config.log_f_format)
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.setLevel(logging.INFO)


class CbrCoursesNotAvailableException(Exception):
    pass


class IncorrectXmlDataException(Exception):
    pass


def get_cbr_courses_xml(main_url: str = config.ext_cbr_site,
                        second_url: str = config.ext_cbr_site_2) -> bytes:
    http_pool = urllib3.PoolManager()
    resp = http_pool.request("GET", main_url)
    if resp.status == 200 and resp.geturl() == main_url:
        xml_data = resp.data
        logger.info("Main url available. Xml data taken.")
    else:
        logger.info("Main url not available. Trying second url...")
        resp = http_pool.request("GET", second_url)
        if resp.status == 200 and resp.geturl() == second_url:
            xml_data = resp.data
            logger.info("Second url available. Xml data taken.")
        else:
            http_pool.clear()
            logger.error("CBR courses not available")
            raise CbrCoursesNotAvailableException("CBR courses not available")
    http_pool.clear()
    return xml_data


def get_course_from_xml(xml_data: Union[bytes, str],
                        valute_charcode: Union[str, bytes] = config.valute_charcode) -> dict:
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        logger.error(e)
        raise

    if root.tag != "ValCurs":
        logger.error("Incorrect xml data")
        raise IncorrectXmlDataException("Incorrect xml data")

    # for ElementTree 1.3+
    valute_el = root.find("./Valute/CharCode[.='" + valute_charcode + "']/..")
    if valute_el is None:
        logger.error("Valute with charcode %s not found!" % valute_charcode)
        raise IncorrectXmlDataException("Valute with charcode %s not found!" % valute_charcode)

    valute_course_el = valute_el.find("./Value")

    try:
        valute_course = float(valute_course_el.text.replace(",", "."))
        date_of_course = root.get("Date")
    except ValueError as e:
        logger.error(e)
        raise

    logger.info("Got course from xml: %f (%s), date: %s" % (valute_course, valute_charcode, date_of_course))
    return {"course": valute_course, "date_of_course": date_of_course, "valute": valute_charcode}


def get_converted_value(value: Union[int, float], course: Union[int, float]) -> float:
    result = value * course
    logger.info("Request value: %f, course: %f, result: %f" % (value, course, result))
    return result


def get_converted_value_for_valute(value: Union[int, float], valute_charcode: str = config.valute_charcode) -> float:
    course = get_course(valute_charcode=valute_charcode)["course"]
    result = value * course
    logger.info("Request value: %f, course: %f, result: %f" % (value, course, result))
    return result


def get_course(valute_charcode: Union[str, bytes] = config.valute_charcode) -> dict:
    xml_data = get_cbr_courses_xml()
    course_data = get_course_from_xml(xml_data, valute_charcode)
    return course_data


def build_result_json(requested_value: Union[int, float, str],
                      result_value: Union[int, float],
                      date_of_course: Union[str, date],
                      course: Union[float, int],
                      valute: str) -> str:
    res = {"requested_value": requested_value,
           "result_value": result_value,
           "date_of_course": date_of_course,
           "course": course,
           "valute": valute
           }
    return json.dumps(res)


def build_error_result_json(error_text: str,
                            requested_value: Optional[Union[int, float, str]] = None,) -> str:
    if requested_value is not None:
        res = {"requested_value": requested_value,
               "error": error_text }
    else:
        res = {"error": error_text}
    return json.dumps(res)
