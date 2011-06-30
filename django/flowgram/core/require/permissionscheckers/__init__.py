from flowgram.core.require.permissionscheckers import authorized, edit_flowgram, edit_page, login, \
                                                          staff, view_flowgram, view_page

permission_funcs = {
    'authorized' : authorized.check,
    'edit_flowgram' : edit_flowgram.check,
    'edit_page' : edit_page.check,
    'login': login.check,
    'staff': staff.check,
    'view_flowgram' : view_flowgram.check,
    'view_page' : view_page.check,
}
