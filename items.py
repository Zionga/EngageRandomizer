from enum import Enum

SID_SMASH = "SID_スマッシュ"

class ItemType(Enum):
    SWORD = 1
    LANCE = 2
    AXE = 3
    BOW = 4
    DAGGER = 5
    TOME = 6
    STAFF = 7
    ART = 8
    CONSUMABLE = 10

class Item():
    def __init__(self, **kwargs) -> None:
        self.Out = kwargs.get("Out", None)
        self.Iid = kwargs.get("Iid", None)
        self.Name = kwargs.get("Name", None)
        self.Help = kwargs.get("Help", None)
        self.Tutorial = kwargs.get("Tutorial", None)
        self.Aid = kwargs.get("Aid", None)
        self.Kind = kwargs.get("Kind", None)
        self.UseType = kwargs.get("UseType", None)
        self.WeaponAttr = kwargs.get("WeaponAttr", None)
        self.Icon = kwargs.get("Icon", None)
        self.Endurance = kwargs.get("Endurance", None)
        self.Power = kwargs.get("Power", None)
        self.Weight = kwargs.get("Weight", None)
        self.RangeI = kwargs.get("RangeI", None)
        self.RangeO = kwargs.get("RangeO", None)
        self.Distance = kwargs.get("Distance", None)
        self.Hit = kwargs.get("Hit", None)
        self.Critical = kwargs.get("Critical", None)
        self.Avoid = kwargs.get("Avoid", None)
        self.Secure = kwargs.get("Secure", None)
        self.EnhanceHp = kwargs.get("EnhanceHp", None)
        self.EnhanceStr = kwargs.get("EnhanceStr", None)
        self.EnhanceTech = kwargs.get("EnhanceTech", None)
        self.EnhanceQuick = kwargs.get("EnhanceQuick", None)
        self.EnhanceLuck = kwargs.get("EnhanceLuck", None)
        self.EnhanceDef = kwargs.get("EnhanceDef", None)
        self.EnhanceMagic = kwargs.get("EnhanceMagic", None)
        self.EnhanceMdef = kwargs.get("EnhanceMdef", None)
        self.EnhancePhys = kwargs.get("EnhancePhys", None)
        self.EnhanceMove = kwargs.get("EnhanceMove", None)
        self.GrowRatioHp = kwargs.get("GrowRatioHp", None)
        self.GrowRatioStr = kwargs.get("GrowRatioStr", None)
        self.GrowRatioTech = kwargs.get("GrowRatioTech", None)
        self.GrowRatioQuick = kwargs.get("GrowRatioQuick", None)
        self.GrowRatioLuck = kwargs.get("GrowRatioLuck", None)
        self.GrowRatioDef = kwargs.get("GrowRatioDef", None)
        self.GrowRatioMagic = kwargs.get("GrowRatioMagic", None)
        self.GrowRatioMdef = kwargs.get("GrowRatioMdef", None)
        self.GrowRatioPhys = kwargs.get("GrowRatioPhys", None)
        self.GrowRatioMove = kwargs.get("GrowRatioMove", None)
        self.Price = kwargs.get("Price", None)
        self.WeaponLevel = kwargs.get("WeaponLevel", None)
        self.RodType = kwargs.get("RodType", None)
        self.RodExp = kwargs.get("RodExp", None)
        self.RateArena = kwargs.get("RateArena", None)
        self.ShootEffect = kwargs.get("ShootEffect", None)
        self.HitEffect = kwargs.get("HitEffect", None)
        self.CannonEffect = kwargs.get("CannonEffect", None)
        self.AttackMotion = kwargs.get("AttackMotion", None)
        self.OverlapTerrain = kwargs.get("OverlapTerrain", None)
        self.EquipCondition = kwargs.get("EquipCondition", None)
        self.Flag = kwargs.get("Flag", None)
        self.EquipSids = kwargs.get("EquipSids", None)
        self.PassiveSids = kwargs.get("PassiveSids", None)
        self.GiveSids = kwargs.get("GiveSids", None)
        self.AddTarget = kwargs.get("AddTarget", None)
        self.AddRange = kwargs.get("AddRange", None)
        self.AddType = kwargs.get("AddType", None)
        self.AddPower = kwargs.get("AddPower", None)
        self.AddSids = kwargs.get("AddSids", None)
        self.AddEffect = kwargs.get("AddEffect", None)
        self.AddHelp = kwargs.get("AddHelp", None)
        self.HighRankItem = kwargs.get("HighRankItem", None)

    def is_smash_weapon(self):
        """
        Checks if the item can smash targets
        """
        if self.EquipSids:
            return self.EquipSids.find(SID_SMASH) != -1
        return False

    def is_magic_weapon(self):
        """
        Checks if the item is a non-tome weapon that deals magical damage
        """
        if self.Flag:
            return self.Flag == "65536"
        return False
    
    def get_item_type(self):
        if self.Kind:
            return ItemType(int(self.Kind))
        return None
    
    def is_physical(self):
        return self.get_item_type in [ItemType.SWORD, ItemType.LANCE, ItemType.AXE, ItemType.BOW, ItemType.DAGGER, ItemType.ART]