import os
import re
import urllib.request
from datetime import datetime
import pickle
from functools import wraps
from getpass import getpass
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import settings


class Kaede:

    def __init__(self):
        self.iroboard_operation = IrohaBoardOperation()

    def kaede_cli_main(self):
        print("-----------------------------------------------------")
        print("Kaede CLI")
        print(settings.COPYRIGHT)
        print("-----------------------------------------------------")

    def kaede_menu(self):
        while True:
            input("Press Enter to continue...")
            print("MENU")
            print("1. Login")
            print("2. Get Course List")
            print("3. Get Course Details")
            print("4. Get Course Contents")
            print("5. Exit")
            print("-----------------------------------------------------")
            menu_num = input("Select Menu Number: ")

            if menu_num == "1":
                username_input = input("Username: ")
                password_input = getpass("Password: ")
                self.iroboard_operation.login(username_input, password_input)

            elif menu_num == "2":
                self.iroboard_operation.get_course_list()
            elif menu_num == "3":
                self.iroboard_operation.get_course_details()
            elif menu_num == "4":
                self.iroboard_operation.get_course_contents()
            elif menu_num == "5":
                break
            else:
                print("Invalid Menu Number")
                continue


class IrohaBoardOperation:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_experimental_option('detach', True)
        self.driver = webdriver.Chrome(options=options)

    def login(self, is_diaplay_login_username: bool = True) -> None:
        """
        Login to Iroha Board

        Args:
            is_diaplay_login_username (bool): If True, display login username.

        Returns:
            None
        """
        self.driver.get(f"{settings.BASE_URI}/irohaboard/")

        # Check if already logged in
        if os.path.exists(os.path.join(settings.COOKIE_ROOTDIR, settings.COOKIES)):
            cookies = pickle.load(
                open(os.path.join(settings.COOKIE_ROOTDIR, settings.COOKIES), 'rb'))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        else:
            # Login
            user_id = input("User ID: ")
            password = getpass("Password: ")
            user_username_input = self.driver.find_element(
                by=By.XPATH, value='//*[@id="UserUsername"]')
            user_password_input = self.driver.find_element(
                by=By.XPATH, value='//*[@id="UserPassword"]')
            login_button = self.driver.find_element(
                by=By.XPATH, value='//*[@id="UserLoginForm"]/div[4]/input')
            user_username_input.send_keys(user_id)
            user_password_input.send_keys(password)
            login_button.click()
            # Save cookies
            pickle.dump(self.driver.get_cookies(), open(
                os.path.join(settings.COOKIE_ROOTDIR, settings.COOKIES), 'wb'))

        title = self.driver.find_element(
            by=By.XPATH, value="/html/body/div[1]/div/a")
        copyright = self.driver.find_element(
            by=By.XPATH, value="/html/body/div[3]")

        print("-----------------------------------------------------")
        print(title.text)
        print(copyright.text)
        if is_diaplay_login_username:
            print(f"Login Username: {self.get_login_username()}")
        print("-----------------------------------------------------")

    def get_login_username(self) -> str:
        """
        Returns:
            login_username (str) : Login username
        """
        self.driver.get(f"{settings.BASE_URI}/irohaboard/")
        login_username = self.driver.find_element(
            by=By.XPATH, value='/html/body/div[1]/div[6]')
        return login_username.text

    def get_course_list(self) -> list:
        """
        Returns:
            course_list (list) : Course list
        """
        self.driver.get(f"{settings.BASE_URI}/irohaboard/")
        course_title_list = []
        course_dict = {}

        course_list_num = self.driver.find_elements(
            by=By.XPATH, value='//*[@id="content"]/div/div[2]/div[2]/ul/a')

        for course_num in range(1, len(course_list_num) + 1):
            course_title = self.driver.find_element(
                by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/ul/a[{course_num}]/h4')
            course_dict = {"id": course_num, "title": course_title.text}
            course_title_list.append(course_dict)

        return course_title_list

    def get_course_details(self, *, course_id: int) -> dict:
        """
        Args:
            course_id (int) : Course ID

        Returns:
            course_details (dict) : Course details
        """
        self.driver.get(
            f"{settings.BASE_URI}/irohaboard/contents/index/{course_id}")
        course_title = self.driver.find_element(
            by=By.XPATH, value='//*[@id="content"]/div/div[2]/div[1]')
        course_description = self.driver.find_element(
            by=By.XPATH, value='//*[@id="content"]/div/div[2]/div[2]/div')
        course_description_dict = {
            "title": course_title.text, "description": course_description.text}
        return course_description_dict

    def get_course_contents(self, *, course_id) -> list:
        """
        Args:
            course_id (int) : Course ID

        Returns:
            course_contents (dict) : Course contents

        Example:
            >>> get_course_contents(course_id=1)
        """
        course_content_list = []
        self.driver.get(
            f"{settings.BASE_URI}/irohaboard/contents/index/{course_id}")

        contents_table_num = self.driver.find_elements(
            by=By.XPATH, value='//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr')

        for content_row in range(1, len(contents_table_num) + 1):
            try:
                content_title = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[1]').text
            except NoSuchElementException:
                content_title = None

            try:
                content_type = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[2]').text
            except NoSuchElementException:
                content_type = None

            try:
                content_learning_start_date = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[3]').text
            except NoSuchElementException:
                content_learning_start_date = None

            try:
                content_last_learning_date = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[4]').text
            except NoSuchElementException:
                content_last_learning_date = None

            try:
                content_learning_time = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[5]').text
            except NoSuchElementException:
                content_learning_time = None

            try:
                content_learning_count = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[6]').text
            except NoSuchElementException:
                content_learning_count = None

            try:
                content_understanding_degree = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[7]').text
            except NoSuchElementException:
                content_understanding_degree = None

            try:
                content_url = self.driver.find_element(
                    by=By.XPATH, value=f'//*[@id="content"]/div/div[2]/div[2]/table/tbody/tr[{content_row}]/td[1]/a').get_attribute("href")
            except NoSuchElementException:
                content_url = None

            course_contents_dict = {
                "title": content_title,
                "type": content_type,
                "learning_start_date": content_learning_start_date,
                "last_learning_date": content_last_learning_date,
                "learning_time": content_learning_time,
                "learning_count":  content_learning_count,
                "understanding_degree": content_understanding_degree,
                "url": content_url
            }

            course_content_list.append(course_contents_dict)
        return course_content_list

    def get_course_content(self, *, content_id):
        self.driver.get(
            f"{settings.BASE_URI}/irohaboard/contents/view/{content_id}")
        course_content = self.driver.find_element(
            by=By.XPATH, value=f'/html/body/div/div[2]')

        return course_content.get_attribute('innerHTML')

    def export_couse_content(self, content: any, content_id: str, export_type: str = "html", is_content_relative: bool = False, is_asset_save_pair: bool = True) -> str:
        """
        Args:
            content (any) : Course content
            export_type (str) : Export type

            Returns:
                export_file_path (str) : Export file path
        """
        domain = settings.BASE_URI.replace("https://", "")

        if not os.path.exists(f"{settings.EXPORT_DIR}/{domain}"):
            os.makedirs(f"{settings.EXPORT_DIR}/{domain}")

        if os.path.exists(f"{settings.EXPORT_DIR}/{domain}/{content_id}.{export_type}"):
            print("[INFO] Export file already exists. Do you overwrite it? (y/n)")
            overwrite = input()
            if overwrite == "y":
                pass
            elif overwrite == "n":
                exit()
            else:
                print("[ERROR] Invalid input")
                exit()

        # Export settings.
        if is_asset_save_pair:
            asset_export_dir = f"{settings.EXPORT_DIR}/{domain}/{content_id}/"
            content = content.replace(
                f"/irohaboard/uploads/", f"./{content_id}/")
        else:
            asset_export_dir = f"{settings.EXPORT_DIR}/{domain}/irohaboard/uploads/"
            content = content.replace(
                f"/irohaboard/uploads/", f"{settings.BASE_URI}/irohaboard/uploads/")

        if not os.path.exists(asset_export_dir):
            os.makedirs(asset_export_dir)

        if not is_content_relative:
            asset_url_list = re.findall(
                settings.BASE_URI + "/irohaboard/uploads/\d{1,}.\w+", content)

        for asset_url in asset_url_list:
            save_file_name = f"{asset_export_dir}{asset_url.split('/')[-1]}"
            urllib.request.urlretrieve(asset_url, save_file_name)

        export_file_header = f"""
        <!-- {settings.EXPORT_CONTENT_HEADER} -->
        <!-- ORIGINAL URL: {settings.BASE_URI}/irohaboard/contents/view/{content_id} -->
        <!-- EXPORT DATE: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->
        """

        if export_type == "html":
            export_file_path = f"{settings.EXPORT_DIR}/{domain}/{content_id}.html"
            with open(export_file_path, "w") as f:
                f.write(export_file_header)
                f.write(content)

        return export_file_path


if __name__ == '__main__':
    pass
