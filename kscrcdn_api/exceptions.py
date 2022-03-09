
class GetOrderDataError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

class MakePlanError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class CheckIPError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class PlanSaveError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class PushPlanError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class BuildDocError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)


class InitError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)
