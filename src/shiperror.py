# shiperror

class ShipError(ValueError):
    pass

class GLimit(ShipError):
    pass

class ThrustLimit(ShipError):
    pass

class IllegalCommand(ShipError):
    pass
