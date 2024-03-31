from enum import Enum


class Mode(Enum):
    Educational  = True
    Fun = False

class Toggle(Enum):
    LHCVelocity = 1
    SynchotronVelocity = 2
    FunMode = 3
    Fill = 4
    LightVelocity = 5
    MuonVelocity = 6
    TauVelocity = 7
    GammaVelocity = 8
    QuarkVelocity = 9
    ZBosonVelocity = 10
    HiggsBosonVelocity = 11
    WPlusVelocity = 12
