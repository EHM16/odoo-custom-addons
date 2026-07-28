# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
import re
from datetime import datetime, date, timezone
import odoo.tools.date_utils

_original_parse_iso_date = odoo.tools.date_utils.parse_iso_date


def _patched_parse_iso_date(value: str) -> date | datetime:
    try:
        return _original_parse_iso_date(value)
    except ValueError:
        s_val = str(value).strip()
        s_val = re.sub(r'\s+([+-]\d{2}:?\d{2}|Z)$', r'\1', s_val)
        if s_val.endswith('Z'):
            s_val = s_val[:-1] + '+00:00'
        try:
            now = datetime.fromisoformat(s_val)
            if now.tzinfo is not None:
                now = now.astimezone(timezone.utc).replace(tzinfo=None)
            return now
        except Exception:
            clean_date = s_val.split('+')[0].split('Z')[0].strip()
            if len(clean_date) <= 10:
                return date.fromisoformat(clean_date[:10])
            return datetime.fromisoformat(clean_date)


odoo.tools.date_utils.parse_iso_date = _patched_parse_iso_date

from . import models
from . import wizard
from . import controllers

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
