from flask_wtf import Form


class ModelForm(Form):
    """
    wtforms_components exposes a similar API but does not inherit
    from flask_wtf.Form
    It uses wtforms.Form

    To have CSRF Protection by default we need to inherit from flask_wtf.Form
    """

    def __init__(self, obj=None, prefix="", **kwargs):
        Form.__init__(self, obj=obj, prefix=prefix, **kwargs)
        self._obj = obj


def choices_from_dict(source, prepend_blank=True):
    """
    Convert dict() to WTForm's choices()

    :param source: Input source
    :type source: dict
    :param prepend_blank: Optional blank item
    :type prepend_block: bool
    :return: list
    """
    choices = []

    if prepend_blank:
        choices.append(("", "Please select one."))

    for key, value in source.items():
        choices.append((key, value))

    return choices


def choices_from_list(source, prepend_blank=True):
    """
    Convert list() to WTForm's choices()

    :param source: Input source
    :type source: list
    :param prepend_blank: Optional blank item
    :type prepend_block: bool
    :return: list
    """
    choices = []

    if prepend_blank:
        choices.append(("", "Please select one."))

    for item in source:
        choices.append((item, item))

    return choices
