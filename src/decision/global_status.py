
# 全局状态


class GlobalStatus(object):
    def __init__(self):
        # 应急处置阶段 normal 正常态, on_urgent 应急态
        self.global_status_period = 'normal'  

    def get_global_status_period(self):
        return self.global_status_period
    
    def set_global_status_period(self, new_status):
        self.global_status_period = new_status

GLOBAL_STATUS = GlobalStatus()