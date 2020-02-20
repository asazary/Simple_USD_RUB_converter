import re
import json
from typing import Optional

import cbr_courses_funcs

from config import log_file_name, log_c_format, log_f_format
import logging
import http.server
import urllib.parse

logger = logging.getLogger(__name__)
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(log_file_name)
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)
c_format = logging.Formatter(log_c_format)
f_format = logging.Formatter(log_f_format)
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.setLevel(logging.INFO)


def service_worker():
    pass


def usd_to_rub(handler) -> str:  # json
    value_usd_str = urllib.parse.unquote(handler.path[len("rub_to_usd")+2:])
    if len(value_usd_str) > 0:
        try:
            value_usd = float(value_usd_str.replace(",", "."))
            course_data: dict = cbr_courses_funcs.get_course()
            value_rub: Optional[float] = course_data["course"] * value_usd
            result: str = cbr_courses_funcs.build_result_json(requested_value=value_usd,
                                                              result_value=value_rub,
                                                              date_of_course=course_data["date_of_course"],
                                                              course=course_data["course"],
                                                              valute="USD"
                                                              )
        except ValueError:
            logger.error("Error during convert %s to float" % value_usd_str)
            value_rub = None
            raise
    else:
        raise ValueError("No data to convert")

    return result


def get_usd_course(handler) -> str:
    course_data: dict = cbr_courses_funcs.get_course(valute_charcode="USD")
    return json.dumps(course_data)


routes = {
    r"^/$": {"GET": get_usd_course, "media_type": "application/json"},
    r"^/usd_to_rub/": {"GET": usd_to_rub, "media_type": "application/json"}
}


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.routes = routes
        http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def do_HEAD(self):
        self.handle_method("HEAD")

    def do_GET(self):
        self.handle_method("GET")

    def handle_method(self, method):
        logger.info("Handle method %s" % method)
        route: dict = self.get_route()
        if route is None:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(cbr_courses_funcs.build_error_result_json(error_text="Route not found").encode())
            logger.error("Route not found")
        else:
            if method == "HEAD":
                self.send_response(200)
                if "media_type" in route:
                    self.send_header("Content-type", route["media_type"])
                self.end_headers()

            else:
                if method in route:
                    try:
                        content = route[method](self)
                    except ValueError as e:
                        logger.error(str(e))
                        content = json.dumps({"error": str(e)})

                    if content is not None:
                        self.send_response(200)
                        if "media_type" in route:
                            self.send_header("Content-type", route["media_type"])
                        self.end_headers()
                        self.wfile.write(content.encode())

                else:
                    self.send_response(405)
                    self.end_headers()
                    self.wfile.write(method + " is not supported\n".encode())
                    logger.error(method + " is not supported")

    def get_route(self) -> dict:
        for path, route in self.routes.items():
            if re.match(path, self.path):
                return route


poll_interval = 0.1


def server(port: int):
    http_server = http.server.HTTPServer(("", port), RequestHandler)
    http_server.service_actions = service_worker
    logger.info("Starting HTTP server on port %d" % port)

    try:
        http_server.serve_forever(poll_interval)
    except KeyboardInterrupt:
        pass
    logger.info("Stopping HTTP server")
    http_server.server_close()


if __name__ == "__main__":
    server(8080)
