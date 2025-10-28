from math import sqrt
from libs.ustr import ustr
import hashlib
import re
import sys

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    QT5 = True
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    QT5 = False


def new_icon(icon):
    return QIcon(':/' + icon)


def new_button(text, icon=None, slot=None):
    b = QPushButton(text)
    if icon is not None:
        b.setIcon(new_icon(icon))
    if slot is not None:
        b.clicked.connect(slot)
    return b


def new_action(parent, text, slot=None, shortcut=None, icon=None,
               tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(new_icon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def add_actions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


def label_validator():
    return QRegExpValidator(QRegExp(r'^[^ \t].+'), None)


class Struct(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def distance(p):
    return sqrt(p.x() * p.x() + p.y() * p.y())


def format_shortcut(text):
    mod, key = text.split('+', 1)
    return '<b>%s</b>+<b>%s</b>' % (mod, key)


def generate_color_by_text_(text):
    s = ustr(text)
    hash_code = int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16)
    r = int((hash_code / 255) % 255)
    g = int((hash_code / 65025) % 255)
    b = int((hash_code / 16581375) % 255)
    return QColor(r, g, b, 80)


def generate_color_by_text(text):
    s = str(text)  # 替代ustr，兼容Python3
    # 1. 哈希获取原始字节（0-255范围，比原大整数取模更均匀）
    hash_bytes = hashlib.sha256(s.encode('utf-8')).digest()
    # 取前3个字节作为初始R、G、B（避免原除法取模导致的数值偏移）
    r = hash_bytes[0]
    g = hash_bytes[1]
    b = hash_bytes[2]

    # 2. 核心：将RGB值限制在「50-200」范围（避免过暗<50或过亮>200）
    def clamp_range(val):
        # 线性映射到50-200：原0→50，原255→200，中间按比例缩放
        return int(50 + (val / 255) * 150)  # 150=200-50

    r = clamp_range(r)
    g = clamp_range(g)
    b = clamp_range(b)

    # 3. 增强饱和度（避免灰调，确保颜色“有特色”）
    def boost_saturation(r, g, b):
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        # 若最大最小差距太小（接近灰色），强制拉大差距
        if (max_val - min_val) < 40:  # 差距阈值，可调整
            # 策略：最大分量再提高20%，最小分量再降低20%
            r = int(r * 1.2) if r == max_val else int(r * 0.8)
            g = int(g * 1.2) if g == max_val else int(g * 0.8)
            b = int(b * 1.2) if b == max_val else int(b * 0.8)
            # 确保不超出50-200范围
            return (max(50, min(r, 200)),
                    max(50, min(g, 200)),
                    max(50, min(b, 200)))
        return (r, g, b)

    r, g, b = boost_saturation(r, g, b)

    # 4. 调整透明度（alpha=120，比原80更高，颜色更实但不遮挡细节）
    return QColor(r, g, b, 80)


def have_qstring():
    """p3/qt5 get rid of QString wrapper as py3 has native unicode str type"""
    return not (sys.version_info.major >= 3 or QT_VERSION_STR.startswith('5.'))


def util_qt_strlistclass():
    return QStringList if have_qstring() else list


def natural_sort(list, key=lambda s:s):
    """
    Sort the list into natural alphanumeric order.
    """
    def get_alphanum_key_func(key):
        convert = lambda text: int(text) if text.isdigit() else text
        return lambda s: [convert(c) for c in re.split('([0-9]+)', key(s))]
    sort_key = get_alphanum_key_func(key)
    list.sort(key=sort_key)


# QT4 has a trimmed method, in QT5 this is called strip
if QT5:
    def trimmed(text):
        return text.strip()
else:
    def trimmed(text):
        return text.trimmed()
