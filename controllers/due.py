# coding: utf8
# This controller is intended for extended view of income and expense planning

@auth.requires_login()
def index():
    return {}

@auth.requires_login()
def list():
    return locals()
