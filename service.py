import win32serviceutil
import win32service
import win32event
from services.background import start_background

class AntiRugService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AntiRugService"
    _svc_display_name_ = "antiRug Optimizer Service"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        start_background()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AntiRugService)