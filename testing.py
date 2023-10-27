from context import BraveDriver
from Register import utils as reg_utils
from Models import Config, Account
from loguru import logger
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

config = Config()
chrome = config.reg.chrome
reg = config.reg


def _register():
    with BraveDriver(uc.Chrome(use_subprocess=chrome.subproc, options=reg_utils.chrome_options(config))) as d:
        d.get(reg.links.register_link)
        d.implicitly_wait(5)
        reg_utils.check_for_captcha(d)
        reg_utils.check_for_cookies(d)
        account = reg_utils.init_account(config)
        reg_utils.register(
            driver=d,
            account=account
        )


_register()
