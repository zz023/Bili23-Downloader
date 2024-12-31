import os
import wx
import json
import wx.adv

from utils.config import Config
from utils.tool_v2 import UniversalTool
from utils.common.exception import GlobalExceptionInfo

class ErrorInfoDialog(wx.Dialog):
    def __init__(self, parent, exception_info = GlobalExceptionInfo.info):
        self.exception_info = exception_info

        wx.Dialog.__init__(self, parent, -1, "错误日志")

        self.init_UI()

        self.Bind_EVT()

        self.CenterOnParent()

    def init_UI(self):
        def _set_dark_mode():
            if not Config.Sys.dark_mode:
                self.SetBackgroundColour("white")
                self.log_box.SetBackgroundColour("white")

        def _get_scale_size(_size: tuple):
            match Config.Sys.platform:
                case "windows":
                    return self.FromDIP(_size)
                
                case "linux" | "darwin":
                    return wx.DefaultSize

        err_icon = wx.StaticBitmap(self, -1, wx.ArtProvider().GetBitmap(wx.ART_ERROR, size = self.FromDIP((28, 28))))

        time_lab = wx.StaticText(self, -1, "记录时间：{}".format(UniversalTool.get_time_str_from_timestamp(self.exception_info.timestamp)))
        source_lab = wx.StaticText(self, -1, "来源：{}".format(self.exception_info.source))
        event_id_lab = wx.StaticText(self, -1, "错误 ID：{}".format(self.exception_info.id))
        return_code_lab = wx.StaticText(self, -1, "返回值：{}".format(self.exception_info.return_code))
        error_type = wx.StaticText(self, -1, "异常类型：{}".format(self.exception_info.exception_type))

        box_sizer = wx.FlexGridSizer(3, 2, 0, 75)
        box_sizer.Add(time_lab, 0, wx.ALL, 10)
        box_sizer.Add(source_lab, 0, wx.ALL, 10)
        box_sizer.Add(event_id_lab, 0, wx.ALL & (~wx.TOP), 10)
        box_sizer.Add(return_code_lab, 0, wx.ALL & (~wx.TOP), 10)
        box_sizer.Add(error_type, 0, wx.ALL & (~wx.TOP), 10)

        top_hbox = wx.BoxSizer(wx.HORIZONTAL)
        top_hbox.Add(err_icon, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        top_hbox.Add(box_sizer, 0, wx.ALL | wx.EXPAND, 10)

        top_border = wx.StaticLine(self, -1, style = wx.HORIZONTAL)

        font: wx.Font = self.GetFont()
        font.SetFractionalPointSize(int(font.GetFractionalPointSize() + 1))

        self.log_box = wx.TextCtrl(self, -1, str(self.exception_info.log), size = self.FromDIP((620, 250)), style = wx.TE_MULTILINE)
        self.log_box.SetFont(font)

        self.save_btn = wx.Button(self, -1, "保存到文件", size = _get_scale_size((100, 28)))
        self.close_btn = wx.Button(self, wx.ID_CANCEL, "关闭", size = _get_scale_size((80, 28)))

        bottom_border = wx.StaticLine(self, -1, style = wx.HORIZONTAL)

        bottom_hbox = wx.BoxSizer(wx.HORIZONTAL)
        bottom_hbox.AddStretchSpacer()
        bottom_hbox.Add(self.save_btn, 0, wx.ALL, 10)
        bottom_hbox.Add(self.close_btn, 0, wx.ALL & (~wx.LEFT), 10)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(top_hbox, 0, wx.EXPAND)
        vbox.Add(top_border, 0, wx.EXPAND)
        vbox.Add(self.log_box, 1, wx.EXPAND)
        vbox.Add(bottom_border, 0, wx.EXPAND)
        vbox.Add(bottom_hbox, 0, wx.EXPAND)

        self.SetSizerAndFit(vbox)

        _set_dark_mode()

    def Bind_EVT(self):
        self.save_btn.Bind(wx.EVT_BUTTON, self.onSaveJsonEVT)

    def onSaveJsonEVT(self, event):
        dialog = wx.FileDialog(self, "保存错误日志", os.getcwd(), wildcard = "错误日志|*.json", style = wx.FD_SAVE)

        if dialog.ShowModal() == wx.ID_OK:
            contens = json.dumps(self.get_error_log(), ensure_ascii = False, indent = 4)

            with open(dialog.GetPath(), "w", encoding = "utf-8") as f:
                f.write(contens)
    
    def get_error_log(self):
        return {
            "记录时间": UniversalTool.get_time_str_from_timestamp(self.exception_info.timestamp),
            "详细日志": self.exception_info.log,
            "来源": self.exception_info.source,
            "错误 ID": self.exception_info.id,
            "异常类型": self.exception_info.exception_type,
            "返回值": self.exception_info.return_code
        }