from Models import Account, DB, Proxy, Config
import re
import win32com.client
import string
import random
import uuid
from loguru import logger

import undetected_chromedriver as uc
import datetime as dt
from time import gmtime, strftime, sleep, time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def init_config():
    logger.debug('Running...')
    return Config()


def _init_chrome(
        arguments: str = None,
        file_path: str = None,
        headless: bool = None
) -> uc.ChromeOptions:
    options = uc.ChromeOptions()
    options.add_argument(arguments)
    options.binary_location = file_path
    options.headless = headless

    return options


def init_chrome(
    config: Config() = None
) -> uc.ChromeOptions:
    logger.debug('Running...')
    return _init_chrome(
        arguments=config.reg.chrome.arguments,
        file_path=config.reg.chrome.file_path,
        headless=config.reg.chrome.headless
    )


def _init_driver(
        script: str = None,
        browser_options: uc.ChromeOptions = None,
        subproc: bool = None
) -> uc.Chrome:
    return uc.Chrome(use_subprocess=subproc, options=browser_options)


def init_driver(
        config: Config() = None,
        chrome_options: uc.ChromeOptions = None
) -> uc.Chrome:
    logger.debug('Running...')
    return _init_driver(
        script=config.reg.chrome.script,
        browser_options=chrome_options,
        subproc=config.reg.chrome.subproc
    )


def _check_for_captcha(
        captcha_present_xpath: str,
        captcha_button_xpath: str,
        driver: uc.Chrome = None
):
    """
    Checks to see if captcha is present on RS website.
    """
    logger.debug('Running...')
    try:
        logger.info('Checking for captcha...')
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
    except TimeoutException as e:
        logger.error(e)


def check_for_captcha(
        config: Config() = None,
        driver: uc.Chrome = None
):
    logger.debug('Running...')
    _check_for_captcha(
        captcha_present_xpath=config.reg.captcha.present_xpath,
        captcha_button_xpath=config.reg.captcha.button_xpath,
        driver=driver
    )


def _check_for_cookies(
        cookies_element_id: str,
        driver: uc.Chrome = None
):
    """
    Checks to see if cookies are present on RS website.
    """
    try:
        logger.info('Checking for cookies...')
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, cookies_element_id))
        )
        logger.info('Cookies found, solving...')
        driver.find_element(By.ID, cookies_element_id).click()
        logger.info('Successfully solved cookies')
    except TimeoutException as e:
        logger.error(e)


def check_for_cookies(
        config: Config() = None,
        driver: uc.Chrome = None
):
    _check_for_cookies(
        driver=driver,
        cookies_element_id=config.reg.misc.cookies_element_id
    )


def _apply_membership(
        driver: uc.Chrome = None,
        account: Account = None,
        membership_redemption_link: str = None,
        email_field_id: str = None,
        continue_button_id: str = None,
        password_field_id: str = None,
        code_field_id: str = None,
        redeem_button_id: str = None
):
    """
    Applies a membership code to an account on RS website.
    :param driver:
    :param account:
    :param membership_redemption_link:
    :param email_field_id:
    :param continue_button_id:
    :param password_field_id:
    :param code_field_id:
    :param redeem_button_id:
    """
    driver.get(membership_redemption_link)
    driver.find_element(By.ID, email_field_id).send_keys(account.email)
    driver.find_element(By.ID, continue_button_id).click()
    driver.find_element(By.ID, password_field_id).send_keys(account.password)
    driver.find_element(By.ID, continue_button_id).click()
    driver.find_element(By.ID, code_field_id).send_keys(account.membership_code)
    driver.find_element(By.ID, redeem_button_id).click()

    logger.debug('Setting account.member True')
    account.member = True
    logger.debug(f'Setting account.member_time {time()}')
    account.member_time = time()


def apply_membership(
        driver: uc.Chrome= None,
        account: Account() = None,
        config: Config() = None
):
    logger.debug('Running...')
    _apply_membership(
        driver=driver,
        account=account,
        membership_redemption_link=config.reg.links.membership_redemption_link,
        email_field_id=config.reg.login.email_field_id,
        continue_button_id=config.reg.login.continue_button_id,
        password_field_id=config.reg.login.password_field_id,
        code_field_id=config.reg.membership.code_field_id,
        redeem_button_id=config.reg.membership.redeem_button_id
    )


def _account_created(
        driver: uc.Chrome = None,
        account: Account = None,
        account_created_id: str = None
):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, account_created_id))
        )
        driver.find_element(By.ID, account_created_id).click()
    except TimeoutException as e:
        logger.error(e)
    driver.quit()
    logger.debug(f'Setting account.creation_time {strftime("%Y-%m-%d %H:%M:%S", gmtime())}')
    account.creation_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    logger.debug (f'Setting account.created to True')
    account.created = True


def account_created(
    driver: uc.Chrome = None,
    account: Account() = None,
    config: Config() = None
):
    _account_created(
        driver=driver,
        account=account,
        account_created_id=config.reg.misc.account_created_id
    )


def _get_verify_link(
        account: Account = None,
        email_api: str = None,
        email_app: str = None,
        email_folder: str = None,
        email_inbox: str = None,
        email_regex: str = None,
        website: str = None
) -> str:
    outlook = win32com.client.Dispatch(email_app).GetNamespace(email_api)
    inbox = outlook.Folders.Item(email_folder).Folders.Item(email_inbox)

    msgs = inbox.Items
    email_not_found = True
    search_criteria = f'[To] = "{account.email}"'
    msg = ""

    while email_not_found:
        if msgs.Find(search_criteria) is not None:
            msg = msgs.find(search_criteria)
            email_not_found = False
        else:
            sleep(5)

    match = re.findall(email_regex, msg.body)
    verify_link = ""
    for m in match:
        if m.startswith(website):
            verify_link = m

    return verify_link


def get_verify_link(
    account: Account() = None,
    config: Config() = None
):
    _get_verify_link(
        account=account,
        email_api=config.reg.email.api,
        email_app=config.reg.email.app,
        email_folder=config.reg.email.folder,
        email_inbox=config.reg.email.inbox,
        email_regex=config.reg.email.regex,
        website=config.reg.links.membership_redemption_link
    )


def _get_membership_code():
    import csv


def _rs_verify(
        driver: uc.Chrome = None,
        account: Account = None,
        link: str = None
):
    driver.get(link)
    driver.quit()
    logger.debug('Setting account.email_verified to True')
    account.email_verified = True


def rs_verify(
    driver: uc.Chrome = None,
    account: Account() = None,
    config: Config() = None
):
    logger.debug('Running...')
    _rs_verify(
        driver=driver,
        account=account,
        link=config.reg.links.verify_link
    )


def _register(
        driver: uc.Chrome = None,
        account: Account() = None,
        email_field_id: str = None,
        password_field_id: str = None,
        day_field_class: str = None,
        month_field_class: str = None,
        year_field_class: str = None,
        terms_field_class: str = None,
        submit_button_id: str = None
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


def register(
    driver: uc.Chrome = None,
    account: Account() = None,
    config: Config() = None
):
    logger.debug('Running...')
    _register(
        driver=driver,
        account=account,
        email_field_id=config.reg.form.email_field_id,
        password_field_id=config.reg.form.password_field_id,
        day_field_class=config.reg.form.day_field_class,
        month_field_class=config.reg.form.month_field_class,
        year_field_class=config.reg.form.year_field_class,
        terms_field_class=config.reg.form.terms_field_class,
        submit_button_id=config.reg.form.submit_button_id
    )


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


def init_account(
        config: Config() = None
) -> Account:
    logger.debug('Initializing account...')
    return _init_account(config)

# def register_new_account(
#     config: Config() = init_config(),
#     account: Account() = None
# ):
#     def _register(
#             driver: uc.Chrome = None,
#             email_field_id: str = None,
#             password_field_id: str = None,
#             day_field_class: str = None,
#             month_field_class: str = None,
#             year_field_class: str = None,
#             terms_field_class: str = None,
#             submit_button_id: str = None
#     ):
#         """
#         Fills out the registration form on RS website.
#         :param driver:
#         :param acc:
#         :param email_field_id:
#         :param password_field_id:
#         :param day_field_class:
#         :param month_field_class:
#         :param year_field_class:
#         :param terms_field_class:
#         :param submit_button_id:
#         """
#         logger.info('Solving registration form...')
#         driver.find_element_by_id(email_field_id).send_keys(account.email),
#         driver.find_element_by_id(password_field_id).send_keys(account.password),
#         driver.find_element_by_class_name(day_field_class).send_keys(account.birthday).strftime("%d"),
#         driver.find_element_by_class_name(month_field_class).send_keys(account.birthday).strftime("%m"),
#         driver.find_element_by_class_name(year_field_class).send_keys(account.birthday).strftime("%Y"),
#         driver.find_element_by_class_name(terms_field_class).click(),
#         driver.find_element_by_id(submit_button_id).click()
#
#     logger.debug(init_driver())
#
#     _register(
#         driver=init_driver(),
#         email_field_id=config.form.email_field_id,
#         password_field_id=config.form.password_field_id,
#         day_field_class=config.form.day_field_class,
#         month_field_class=config.form.month_field_class,
#         year_field_class=config.form.year_field_class,
#         terms_field_class=config.form.terms_field_class,
#         submit_button_id=config.form.submit_button_id
#     )


# register_new_account(
#     config=init_config(),
#     account=init_account(init_config())
# )
