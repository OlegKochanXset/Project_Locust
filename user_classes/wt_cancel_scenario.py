from locust import task, SequentialTaskSet, FastHttpUser, HttpUser, constant_pacing, events, between
from config.config import cfg, logger
import sys, re
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_field, processCancelRequestBody
import random
from urllib.parse import unquote_plus
from bs4 import BeautifulSoup


class PurchaseFlightTicket2(SequentialTaskSet):  # класс с задачами (содержит основной сценарий)

    test_user_csv_file_path = './test_data/user_data_test.csv'

    test_users_data = open_csv_field(test_user_csv_file_path)

    def on_start(self) -> None:
        @task
        def uc02_01_getHomePage(self) -> None:
            with self.client.get(
                    '/WebTours/',
                    name='REQ02_01_1_/WebTours/',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    #  debug_stream = sys.stderr
            ) as req02_01_1_response:
                check_http_response(req02_01_1_response, "Web Tours")
            # ==========================================================================================================================================================================================================
            with self.client.get(
                    '/cgi-bin/welcome.pl?signOff=true',
                    name='REQ02_01_2_/cgi-bin/welcome.pl?signOff=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    # debug_stream = sys.stderr
            ) as req02_01_2_response:
                check_http_response(req02_01_2_response,
                                    "A Session ID has been created and loaded into a cookie called MSO")
            # ==========================================================================================================================================================================================================
            with self.client.get(
                    '/cgi-bin/nav.pl?in=home',
                    name='REQ02_01_3_/cgi-bin/nav.pl?in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req02_01_3_response:
                check_http_response(req02_01_3_response, "name=\"userSession\"")
            self.userSession = re.search(r'name=\"userSession\" value=\"(.*)\"/>', req02_01_3_response.text).group(1)

        @task
        def uc02_02_getLogin(self) -> None:
            self.user_data_row = random.choice(self.test_users_data)

            self.userName = self.user_data_row['username']
            self.password = self.user_data_row['password']

            req_body02_02_1 = f'userSession={self.userSession}&username={self.userName}&password={self.password}&login.x=0&login.y=0&JSFormSubmit=off'

            with self.client.post(
                    '/cgi-bin/login.pl',
                    name='REQ02_02_1_/cgi-bin/login.pl',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    data=req_body02_02_1,
                    catch_response=True,
                    # debug_stream=sys.stderr
            ) as req02_02_1_response:
                check_http_response(req02_02_1_response, "User password was correct")

                # ==============================================================================================================================================================================================================

            with self.client.get(
                    '/cgi-bin/nav.pl?page=menu&in=home',
                    name='REQ02_02_2_/cgi-bin/nav.pl?page=menu&in=home',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    catch_response=True,
                    # debug_stream = sys.stderr
            ) as req02_02_2_response:
                check_http_response(req02_02_2_response, "<title>Web Tours Navigation Bar</title>")

            with self.client.get(
                    '/cgi-bin/login.pl?intro=true',
                    name='REQ02_02_3_/cgi-bin/login.pl?intro=true',
                    headers={
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-encoding': 'gzip, deflate, br, zstd',
                        'content-type': 'application/x-www-form-urlencoded'
                    },
                    allow_redirects=False,
                    catch_response=True,
                    # debug_stream = sys.stderr
            ) as req02_02_3_response:
                check_http_response(req02_02_3_response,
                                    f"Welcome, <b>{self.userName}</b>, to the Web Tours reservation pages")

        uc02_01_getHomePage(self)
        uc02_02_getLogin(self)

    @task
    def uc02_03_openItinerary(self):
        with self.client.get(
                '/cgi-bin/welcome.pl?page=itinerary',
                name='REQ02_03_1_/cgi-bin/welcome.pl?page=itinerary',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                debug_stream=sys.stderr
        ) as req02_03_1_response:
            check_http_response(req02_03_1_response, "User wants the intineraries.")

        with self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=itinerary',
                name='REQ02_03_2_/cgi-bin/nav.pl?page=menu&in=itinerary',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                debug_stream=sys.stderr
        ) as req02_03_2_response:
            check_http_response(req02_03_2_response, "<title>Web Tours Navigation Bar</title>")

        with self.client.get(
                '/cgi-bin/itinerary.pl',
                name='REQ02_03_3_/cgi-bin/itinerary.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd'
                },
                allow_redirects=False,
                catch_response=True,
                debug_stream=sys.stderr
        ) as req02_03_3_response:
            check_http_response(req02_03_3_response, "Flights List")

        self.flightsID = re.findall(r'name="flightID" value="(.*?)"\s*/>', req02_03_3_response.text)
        self.cgifields = re.findall(r'name="\.cgifields" value="(\d{1,4})"\s*/>', req02_03_3_response.text)

        logger.info(f'Flights found: {self.flightsID}')
        logger.info(f'CGI fields: {self.cgifields}')

        # Инициализируем переменную перед использованием
        total_flights = 0

        # Используем регулярное выражение для поиска текста с количеством билетов
        match = re.search(r'A total of (\d+) scheduled flights', req02_03_3_response.text)

        if match:
            total_flights = int(match.group(1))
            if total_flights > 0:
                logger.info(f"[Itinerary] Найдено билетов: {total_flights}")
                req02_03_3_response.success()
            else:
                req02_03_3_response.failure("Количество билетов = 0")
        else:
            req02_03_3_response.failure("Не удалось найти информацию о количестве билетов")

        print(f"[DEBUG] Общее количество билетов: {total_flights}")
        self.total_flights = total_flights

    @task
    def uc02_04_deleteTickets(self) -> None:
        """Удаление билетов и проверка, что количество уменьшилось"""

        if not hasattr(self, 'total_flights') or self.total_flights <= 0:
            logger.error("Нет билетов для удаления")
            return

        flights_before = self.total_flights

        # Формируем тело запроса для отмены всех билетов, которые есть
        req_body_04_01 = processCancelRequestBody(self.flightsID, self.cgifields)
        logger.info(f"Тело запроса на удаление: {req_body_04_01}")

        with self.client.post(
                '/cgi-bin/itinerary.pl',
                name='REQ02_04_1_/cgi-bin/itinerary.pl',
                headers={
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-encoding': 'gzip, deflate, br, zstd',
                    'content-type': 'application/x-www-form-urlencoded'
                },
                data=req_body_04_01,
                catch_response=True,
                debug_stream=sys.stderr
        ) as delete_response:
            if delete_response.status_code == 200:
                logger.info("Запрос на удаление билетов выполнен")

                # Проверяем обновленное количество билетов
                with self.client.get(
                        '/cgi-bin/itinerary.pl',
                        name='REQ02_04_2_/cgi-bin/itinerary.pl [Проверка удаления]',
                        catch_response=True,
                        debug_stream=sys.stderr
                ) as check_response:
                    match = re.search(r'A total of (\d+) scheduled flights', check_response.text)
                    if match:
                        flights_after = int(match.group(1))
                        logger.info(f"[Проверка] Кол-во билетов после удаления: {flights_after}")

                        if flights_after < flights_before:
                            self.total_flights = flights_after  # Обновляем значение
                            delete_response.success()
                            logger.info("[Проверка] Билеты успешно удалены")
                        else:
                            delete_response.failure(
                                f"[Ошибка] Количество билетов не уменьшилось: было {flights_before}, стало {flights_after}")

    # @task
    # def uc02_03_openItinerary(self):
    #     with self.client.get(
    #             '/cgi-bin/welcome.pl?page=itinerary',
    #             name='REQ02_03_1_/cgi-bin/welcome.pl?page=itinerary',
    #             headers={
    #                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #                 'accept-encoding': 'gzip, deflate, br, zstd'
    #             },
    #             debug_stream=sys.stderr
    #     ) as req02_03_1_response:
    #         check_http_response(req02_03_1_response, "User wants the intineraries.")
    #
    #     with self.client.get(
    #             '/cgi-bin/nav.pl?page=menu&in=itinerary',
    #             name='REQ02_03_2_/cgi-bin/nav.pl?page=menu&in=itinerary',
    #             headers={
    #                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #                 'accept-encoding': 'gzip, deflate, br, zstd'
    #             },
    #             allow_redirects=False,
    #             debug_stream=sys.stderr
    #     ) as req02_03_2_response:
    #         check_http_response(req02_03_2_response, "<title>Web Tours Navigation Bar</title>")
    #
    #     with self.client.get(
    #             '/cgi-bin/itinerary.pl',
    #             name='REQ02_03_3_/cgi-bin/itinerary.pl',
    #             headers={
    #                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #                 'accept-encoding': 'gzip, deflate, br, zstd'
    #             },
    #             allow_redirects=False,
    #             catch_response=True,
    #             debug_stream=sys.stderr
    #     ) as req02_03_3_response:
    #         check_http_response(req02_03_3_response, "Flights List")
    #
    #     self.flightsID = re.findall(r'name="flightID" value="(.*?)"\s*/>', req02_03_3_response.text)
    #     self.cgifields = re.findall(r'name="\.cgifields" value="(\d{1,4})"\s*/>', req02_03_3_response.text)

    # @task
    # def uc02_04_deleteTickets(self) -> None:
    #     """Запросы как вджеметре"""
    #
    #     req_body02_04_01 = processCancelRequestBody(self.flightsID, self.cgifields)
    #     # logger.info(f'Body-Cancel-: {req_body02_04_01}')
    #
    #     with self.client.post(
    #             '/cgi-bin/itinerary.pl',
    #             name='REQ02_04_1_/cgi-bin/itinerary.pl',
    #             headers={
    #                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #                 'accept-encoding': 'gzip, deflate, br, zstd',
    #                 'content-type': 'application/x-www-form-urlencoded'
    #             },
    #             data=req_body02_04_01,
    #             catch_response=True,
    #             debug_stream=sys.stderr
    #     ) as req02_04_1_response:
    #         check_http_response(req02_04_1_response, "Flights List")



    # @task
    # def uc02_04_deleteTickets(self) -> None:
    #     """Запросы как вджеметре"""
    #
    #     req_body02_04_01 = processCancelRequestBody(self.flightsID, self.cgifields)
    #     # logger.info(f'Body-Cancel-: {req_body02_04_01}')
    #
    #     with self.client.post(
    #             '/cgi-bin/itinerary.pl',
    #             name='REQ02_04_1_/cgi-bin/itinerary.pl',
    #             headers={
    #                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    #                 'accept-encoding': 'gzip, deflate, br, zstd',
    #                 'content-type': 'application/x-www-form-urlencoded'
    #             },
    #             data=req_body02_04_01,
    #             catch_response=True,
    #             debug_stream=sys.stderr
    #     ) as req02_04_1_response:
    #         check_http_response(req02_04_1_response, "Flights List")


class WebToursCancelUserClass(FastHttpUser):  # юзер-класс, принимающий в себя основные параметры теста
    wait_time = constant_pacing(cfg.webtours_cancel.pacing)
    host = cfg.url

    logger.info(f'WebToursBaseClass started. Host: {host}')
    tasks = [PurchaseFlightTicket2]
