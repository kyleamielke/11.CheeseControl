from pydantic import BaseModel
import src.utils as utils

reg_file = 'reg'
cc_file = 'cc'


class Proxy(BaseModel):
    """
    Creates a proxy object.
    """
    uuid: str = None
    ip: str = None
    port: str = None
    username: str = None
    password: str = None


class DB(BaseModel):
    fps: int = None
    render: str = None
    width: int = None
    height: int = None


class Account(BaseModel):
    """
    Creates an account object to register & play runescape.
    """
    uuid: str = None
    email: str = None
    username: str = None
    password: str = None
    birthday: float = None
    creation_time: int = None
    created: bool = None
    email_verified: bool = None
    member: bool = None
    member_time: int = None
    proxy: Proxy = None
    db: DB = None


class _LoggingSettings(BaseModel):
    """
    Settings related to logging.
    """
    level: str
    sink: str
    enqueue: bool


class _DBSettings(BaseModel):
    """
    DreamBot Settings object.
    """

    class _User(BaseModel):
        username: str
        password: str

    userinfo: _User = _User(
        **utils.get_config_contents(utils.get_config_file_path(cc_file))['DB Settings']
    )


class _RegSettings(BaseModel):
    """
    Object for all registration related HTML elements on the RS website.
    """

    class _RS_Links(BaseModel):
        register_link: str = None
        verify_link: str = None
        membership_redemption_link: str = None

    class _Chrome_Options(BaseModel):
        file_path: str = None
        script: str = None
        headless: bool = None
        arguments: str = None
        subproc: bool = None

    class _CaptchaInfo(BaseModel):
        """
        Captcha info RS registration on RS website.
        """
        present_xpath: str = None
        button_xpath: str = None

    class _FormInfo(BaseModel):
        """
        Form info for RS registration on RS website.
        """
        email_field_id: str = None
        password_field_id: str = None
        day_field_class: str = None
        month_field_class: str = None
        year_field_class: str = None
        terms_field_class: str = None
        submit_button_id: str = None

    class _EmailInfo(BaseModel):
        """
        Email information used to verify the email received from RS
        """
        api: str = None
        app: str = None
        folder: str = None
        inbox: str = None
        regex: str = None

    class _RSLoginInfo(BaseModel):
        """
        Field information to log into the RS website
        """
        email_field_id: str = None
        continue_button_id: str = None
        password_field_id: str = None

    class _MembershipInfo(BaseModel):
        """
        Field information to activate a membership code on an account.
        """
        code_field_id: str = None
        redeem_button_id: str = None

    class _MISC(BaseModel):
        account_created_id: str = None
        cookies_element_id: str = None
        domains: list = None

    links: _RS_Links = _RS_Links(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['RS Links']
    )

    chrome: _Chrome_Options = _Chrome_Options(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['Chrome Options']
    )

    captcha: _CaptchaInfo = _CaptchaInfo(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['Captcha Info']
    )

    form: _FormInfo = _FormInfo(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['Form Info']
    )

    email: _EmailInfo = _EmailInfo(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['Email Info']
    )

    login: _RSLoginInfo = _RSLoginInfo(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['RS Login Info']
    )

    membership: _MembershipInfo = _MembershipInfo(
        **utils.get_config_contents(utils.get_config_file_path(reg_file))['Membership Info']
    )

    misc: _MISC = _MISC(
        account_created_id=utils.get_config_contents(utils.get_config_file_path(reg_file))['MISC']['Account_Created_ID'],
        cookies_element_id=utils.get_config_contents(utils.get_config_file_path(reg_file))['MISC']['Cookies_Element_ID'],
        domains=utils.get_config_contents(utils.get_config_file_path(reg_file))['MISC']['Domains'].split(',')
    )


class Config(BaseModel):
    """
    Settings for Cheese Control.
    """
    logging: _LoggingSettings = _LoggingSettings(
        **utils.get_config_contents(utils.get_config_file_path(cc_file))['Log Settings']
    )
    dreambot: _DBSettings = _DBSettings()
    reg: _RegSettings = _RegSettings()


class Params(BaseModel):
    flags: list[str] = None
    file_path: str = None
    # fps: Account.db.fps = None
    # render: Account.db.render = None
    # width: Account.db.width = None
    # height: Account.db.height = None


class DreamBot(BaseModel):
    account: Account = None
    username: str = None
    password: str = None
    script: str = None
    script_params: str = None
    params: Params = None
