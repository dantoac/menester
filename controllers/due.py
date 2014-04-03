# coding: utf8
# This controller is intended for extended view of income and expense planning

@auth.requires_membership('admin')
def index():
    return {}

@auth.requires_membership('admin')
def list():
    return locals()
