import Register
from loguru import logger
from time import sleep

config = Register.init_config()
logger.debug(config.model_dump())
account = Register.init_account(config)
logger.debug(account.model_dump())

chrome = Register.init_chrome(config)
driver = Register.init_driver(
    config=config,
    chrome_options=chrome
)
driver.implicitly_wait(5)
driver.execute_script(config.reg.chrome.script)
driver.get(config.reg.links.register_link)


def captcha():
    Register.check_for_captcha(
        config=config,
        driver=driver
    )


def cookies():
    Register.check_for_cookies(
        config=config,
        driver=driver
    )


def register():
    Register.register(
        account=account,
        config=config,
        driver=driver
    )


try:
    captcha()
except Exception as e:
    logger.error(e)

sleep(5)
try:
    cookies()
except Exception as e:
    logger.error(e)

sleep(5)
try:
    register()
except Exception as e:
    logger.error(e)

sleep(5)
try:
    captcha()
except Exception as e:
    logger.error(e)

sleep(5)
try:
    cookies()
except Exception as e:
    logger.error(e)


#
# Register.register(
#     account=account,
#     driver=driver,
#     config=config
# )
