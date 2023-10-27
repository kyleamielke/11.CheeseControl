from time import gmtime, strftime, sleep, time
import datetime as dt
import string
import random
import uuid

import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from loguru import logger

from Models import Config, Account, DB, Proxy

chrome = Config().reg.chrome
reg = Config().reg


def _check_for_captcha(
        captcha_present_xpath: str,
        captcha_button_xpath: str,
        driver
):
    logger.debug('Running...')
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, captcha_present_xpath))
    )
    logger.info('Captcha found, solving...')
    driver.switch_to.frame(0)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, captcha_button_xpath))
    )
    driver.find_element(By.XPATH, captcha_button_xpath).click()
    driver.switch_to.default_content()
    logger.info('Successfully solved the captcha')


def _check_for_cookies(
        cookies_element_id: str,
        driver
):
    """
    Checks to see if cookies are present on RS website.
    """
    logger.info('Checking for cookies...')
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, cookies_element_id))
    )
    logger.info('Cookies found, solving...')
    driver.find_element(By.ID, cookies_element_id).click()
    logger.info('Successfully solved cookies')


def _init_account(cfg: Config() = None) -> Account:
    from math import floor
    import re
    import names

    cfg = cfg.reg

    def _scrambol(unscrambled: str, symbol: str = r".") -> str:
        """Scramble a string by inserting a symbol at random positions."""
        assert len(symbol) == 1, "Symbol must be a single character."

        _scram = ""

        _max_qty = floor(len(unscrambled) / 5) + 1
        _pos = [random.randint(1, len(unscrambled) - 1) for p in range(0, _max_qty)]

        for i, char in enumerate(unscrambled):
            if i == 0 or (i == len(unscrambled)):
                pass
            elif i in _pos:
                _scram += symbol
            _scram += char

        # . Collapse repeated symbols
        _re = re.compile(rf"{symbol}{2,}")
        scrambled = re.sub(_re, rf"{symbol}", _scram)

        return scrambled

    def _email() -> str:
        """Generate a random email address."""
        return _scrambol(
            f"{names.get_first_name().lower()}"
            f"{names.get_last_name().lower()}"
        ) + '@' + cfg.misc.domains[random.randint(0, len(cfg.misc.domains) - 1)]

    def _password():
        letters = string.ascii_lowercase + string.digits + string.ascii_uppercase
        rnd = random.SystemRandom()
        password = ''.join(rnd.choice(letters) for i in range(random.randint(7, 12)))
        return password

    def _birthday() -> float:
        """Generate a random birthday."""
        now = time()
        year_s = 31556926

        age_min = now - (14 * year_s)
        age_max = now - (40 * year_s)
        age_range_days_n = int(age_min - age_max)

        random_day_s = age_min - random.randrange(age_range_days_n)
        random_day = random_day_s
        # random_day = strftime("%Y-%m-%d", gmtime(random_day_s))

        return random_day

    def _random_db_params(db: DB = DB()):
        db.fps = random.randint(5, 20)
        db.width = random.randint(760, 1200)
        db.height = random.randint(500, 900)
        db.render = 'all'
        return db

    return Account(
        uuid=uuid.uuid4().hex,
        email=_email(),
        username='',
        password=_password(),
        birthday=_birthday(),
        creation_time=0,
        created=False,
        email_verified=False,
        proxy=Proxy(),
        db=_random_db_params()
    )


def _register(
        driver,
        account: Account() = None,
        email_field_id: str = None,
        password_field_id: str = None,
        day_field_class: str = None,
        month_field_class: str = None,
        year_field_class: str = None,
        terms_field_class: str = None,
        submit_button_id: str = None,

):
    """
    Fills out the registration form on RS website.
    :param driver:
    :param acc:
    :param email_field_id:
    :param password_field_id:
    :param day_field_class:
    :param month_field_class:
    :param year_field_class:
    :param terms_field_class:
    :param submit_button_id:
    """
    logger.info('Solving registration form...')
    driver.find_element(By.ID, email_field_id).send_keys(account.email),
    driver.find_element(By.ID, password_field_id).send_keys(account.password),
    driver.find_element(
        By.CLASS_NAME, day_field_class
    ).send_keys(dt.datetime.fromtimestamp(account.birthday).strftime("%d")),
    driver.find_element(
        By.CLASS_NAME, month_field_class
    ).send_keys(dt.datetime.fromtimestamp(account.birthday).strftime("%m")),
    driver.find_element(
        By.CLASS_NAME, year_field_class
    ).send_keys(dt.datetime.fromtimestamp(account.birthday).strftime("%Y")),
    driver.find_element(By.CLASS_NAME, terms_field_class).click(),
    driver.find_element(By.ID, submit_button_id).click()


def check_for_captcha(driver):
    _check_for_captcha(
        captcha_present_xpath=reg.captcha.present_xpath,
        captcha_button_xpath=reg.captcha.button_xpath,
        driver=driver
    )


def check_for_cookies(driver):
    _check_for_cookies(
        cookies_element_id=reg.misc.cookies_element_id,
        driver=driver
    )


def chrome_options(
    config: Config() = None
) -> uc.ChromeOptions:
    options = uc.ChromeOptions()
    options.add_argument(config.reg.chrome.arguments)
    options.binary_location = config.reg.chrome.file_path
    options.headless = config.reg.chrome.headless
    return options


def init_account(
    config: Config() = None
) -> Account:
    logger.debug('Initializing account...')
    return _init_account(config)


def register(
    driver,
    account: Account() = None
):
    _register(
        driver=driver,
        account=account,
        email_field_id=reg.form.email_field_id,
        password_field_id=reg.form.password_field_id,
        day_field_class=reg.form.day_field_class,
        month_field_class=reg.form.month_field_class,
        year_field_class=reg.form.year_field_class,
        terms_field_class=reg.form.terms_field_class,
        submit_button_id=reg.form.submit_button_id
    )
