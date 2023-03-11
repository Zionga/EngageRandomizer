import xml.etree.ElementTree as ET
import UnityPy
import random
from enum import Enum

from items import ItemType

class Proficiency(Enum):
    NONE = 0
    SWORD = 2
    LANCE = 4
    AXE = 8
    BOW = 16
    DAGGER = 32
    TOME = 64
    STAFF = 128
    ART = 256

class Job():
    def __init__(self, **kwargs) -> None:
        self.Jid = kwargs.get("Jid", None)
        self.Aid = kwargs.get("Aid", None)
        self.Name = kwargs.get("Name", None)
        self.Help = kwargs.get("Help", None)
        self.UnitIconID_M = kwargs.get("UnitIconID_M", None)
        self.UnitIconID_F = kwargs.get("UnitIconID_F", None)
        self.UnitIconWeaponID = kwargs.get("UnitIconWeaponID", None)
        self.Rank = kwargs.get("Rank", None)
        self.StyleName = kwargs.get("StyleName", None)
        self.MoveType = kwargs.get("MoveType", None)
        self.StepFrame = kwargs.get("StepFrame", None)
        self.MaxLevel = kwargs.get("MaxLevel", None)
        self.InternalLevel = kwargs.get("InternalLevel", None)
        self.Sort = kwargs.get("Sort", None)
        self.Flag = kwargs.get("Flag", None)
        self.WeaponNone = kwargs.get("WeaponNone", None)
        self.WeaponSword = kwargs.get("WeaponSword", None)
        self.WeaponLance = kwargs.get("WeaponLance", None)
        self.WeaponAxe = kwargs.get("WeaponAxe", None)
        self.WeaponBow = kwargs.get("WeaponBow", None)
        self.WeaponDagger = kwargs.get("WeaponDagger", None)
        self.WeaponMagic = kwargs.get("WeaponMagic", None)
        self.WeaponRod = kwargs.get("WeaponRod", None)
        self.WeaponFist = kwargs.get("WeaponFist", None)
        self.WeaponSpecial = kwargs.get("WeaponSpecial", None)
        self.WeaponTool = kwargs.get("WeaponTool", None)
        self.MaxWeaponLevelNone = kwargs.get("MaxWeaponLevelNone", None)
        self.MaxWeaponLevelSword = kwargs.get("MaxWeaponLevelSword", None)
        self.MaxWeaponLevelLance = kwargs.get("MaxWeaponLevelLance", None)
        self.MaxWeaponLevelAxe = kwargs.get("MaxWeaponLevelAxe", None)
        self.MaxWeaponLevelBow = kwargs.get("MaxWeaponLevelBow", None)
        self.MaxWeaponLevelDagger = kwargs.get("MaxWeaponLevelDagger", None)
        self.MaxWeaponLevelMagic = kwargs.get("MaxWeaponLevelMagic", None)
        self.MaxWeaponLevelRod = kwargs.get("MaxWeaponLevelRod", None)
        self.MaxWeaponLevelFist = kwargs.get("MaxWeaponLevelFist", None)
        self.MaxWeaponLevelSpecial = kwargs.get("MaxWeaponLevelSpecial", None)
        self.BaseHp = kwargs.get("BaseHp", None)
        self.BaseStr = kwargs.get("BaseStr", None)
        self.BaseTech = kwargs.get("BaseTech", None)
        self.BaseQuick = kwargs.get("BaseQuick", None)
        self.BaseLuck = kwargs.get("BaseLuck", None)
        self.BaseDef = kwargs.get("BaseDef", None)
        self.BaseMagic = kwargs.get("BaseMagic", None)
        self.BaseMdef = kwargs.get("BaseMdef", None)
        self.BasePhys = kwargs.get("BasePhys", None)
        self.BaseSight = kwargs.get("BaseSight", None)
        self.BaseMove = kwargs.get("BaseMove", None)
        self.LimitHp = kwargs.get("LimitHp", None)
        self.LimitStr = kwargs.get("LimitStr", None)
        self.LimitTech = kwargs.get("LimitTech", None)
        self.LimitQuick = kwargs.get("LimitQuick", None)
        self.LimitLuck = kwargs.get("LimitLuck", None)
        self.LimitDef = kwargs.get("LimitDef", None)
        self.LimitMagic = kwargs.get("LimitMagic", None)
        self.LimitMdef = kwargs.get("LimitMdef", None)
        self.LimitPhys = kwargs.get("LimitPhys", None)
        self.LimitSight = kwargs.get("LimitSight", None)
        self.LimitMove = kwargs.get("LimitMove", None)
        self.BaseGrowHp = kwargs.get("BaseGrowHp", None)
        self.BaseGrowStr = kwargs.get("BaseGrowStr", None)
        self.BaseGrowTech = kwargs.get("BaseGrowTech", None)
        self.BaseGrowQuick = kwargs.get("BaseGrowQuick", None)
        self.BaseGrowLuck = kwargs.get("BaseGrowLuck", None)
        self.BaseGrowDef = kwargs.get("BaseGrowDef", None)
        self.BaseGrowMagic = kwargs.get("BaseGrowMagic", None)
        self.BaseGrowMdef = kwargs.get("BaseGrowMdef", None)
        self.BaseGrowPhys = kwargs.get("BaseGrowPhys", None)
        self.BaseGrowSight = kwargs.get("BaseGrowSight", None)
        self.BaseGrowMove = kwargs.get("BaseGrowMove", None)
        self.DiffGrowHp = kwargs.get("DiffGrowHp", None)
        self.DiffGrowStr = kwargs.get("DiffGrowStr", None)
        self.DiffGrowTech = kwargs.get("DiffGrowTech", None)
        self.DiffGrowQuick = kwargs.get("DiffGrowQuick", None)
        self.DiffGrowLuck = kwargs.get("DiffGrowLuck", None)
        self.DiffGrowDef = kwargs.get("DiffGrowDef", None)
        self.DiffGrowMagic = kwargs.get("DiffGrowMagic", None)
        self.DiffGrowMdef = kwargs.get("DiffGrowMdef", None)
        self.DiffGrowPhys = kwargs.get("DiffGrowPhys", None)
        self.DiffGrowSight = kwargs.get("DiffGrowSight", None)
        self.DiffGrowMove = kwargs.get("DiffGrowMove", None)
        self.DiffGrowNormalHp = kwargs.get("DiffGrowNormalHp", None)
        self.DiffGrowNormalStr = kwargs.get("DiffGrowNormalStr", None)
        self.DiffGrowNormalTech = kwargs.get("DiffGrowNormalTech", None)
        self.DiffGrowNormalQuick = kwargs.get("DiffGrowNormalQuick", None)
        self.DiffGrowNormalLuck = kwargs.get("DiffGrowNormalLuck", None)
        self.DiffGrowNormalDef = kwargs.get("DiffGrowNormalDef", None)
        self.DiffGrowNormalMagic = kwargs.get("DiffGrowNormalMagic", None)
        self.DiffGrowNormalMdef = kwargs.get("DiffGrowNormalMdef", None)
        self.DiffGrowNormalPhys = kwargs.get("DiffGrowNormalPhys", None)
        self.DiffGrowNormalSight = kwargs.get("DiffGrowNormalSight", None)
        self.DiffGrowNormalMove = kwargs.get("DiffGrowNormalMove", None)
        self.DiffGrowHardHp = kwargs.get("DiffGrowHardHp", None)
        self.DiffGrowHardStr = kwargs.get("DiffGrowHardStr", None)
        self.DiffGrowHardTech = kwargs.get("DiffGrowHardTech", None)
        self.DiffGrowHardQuick = kwargs.get("DiffGrowHardQuick", None)
        self.DiffGrowHardLuck = kwargs.get("DiffGrowHardLuck", None)
        self.DiffGrowHardDef = kwargs.get("DiffGrowHardDef", None)
        self.DiffGrowHardMagic = kwargs.get("DiffGrowHardMagic", None)
        self.DiffGrowHardMdef = kwargs.get("DiffGrowHardMdef", None)
        self.DiffGrowHardPhys = kwargs.get("DiffGrowHardPhys", None)
        self.DiffGrowHardSight = kwargs.get("DiffGrowHardSight", None)
        self.DiffGrowHardMove = kwargs.get("DiffGrowHardMove", None)
        self.DiffGrowLunaticHp = kwargs.get("DiffGrowLunaticHp", None)
        self.DiffGrowLunaticStr = kwargs.get("DiffGrowLunaticStr", None)
        self.DiffGrowLunaticTech = kwargs.get("DiffGrowLunaticTech", None)
        self.DiffGrowLunaticQuick = kwargs.get("DiffGrowLunaticQuick", None)
        self.DiffGrowLunaticLuck = kwargs.get("DiffGrowLunaticLuck", None)
        self.DiffGrowLunaticDef = kwargs.get("DiffGrowLunaticDef", None)
        self.DiffGrowLunaticMagic = kwargs.get("DiffGrowLunaticMagic", None)
        self.DiffGrowLunaticMdef = kwargs.get("DiffGrowLunaticMdef", None)
        self.DiffGrowLunaticPhys = kwargs.get("DiffGrowLunaticPhys", None)
        self.DiffGrowLunaticSight = kwargs.get("DiffGrowLunaticSight", None)
        self.DiffGrowLunaticMove = kwargs.get("DiffGrowLunaticMove", None)
        self.HighJob1 = kwargs.get("HighJob1", None)
        self.HighJob2 = kwargs.get("HighJob2", None)
        self.LowJob = kwargs.get("LowJob", None)
        self.CCItems = kwargs.get("CCItems", None)
        self.ShortName = kwargs.get("ShortName", None)
        self.UniqueItems = kwargs.get("UniqueItems", None)
        self.Skills = kwargs.get("Skills", None)
        self.LearningSkill = kwargs.get("LearningSkill", None)
        self.LunaticSkill = kwargs.get("LunaticSkill", None)
        self.Attrs = kwargs.get("Attrs", None)

    # def get_proficiency(self) -> list[Proficiency]:
    #     """
    #     Gets the proficiencies of a class.
    #     Returns a list where the first value is the main proficiency and the second one is the sub proficiency (if applicable)
    #     """

    def get_job_weapons(self, pProficiencies:list[Proficiency] = None) -> list[ItemType]:
        job_weapons = []
        job_variant_weapons = [] # For jobs that have variant weapon types (General, Paladin, Hero, etc)
        job_tertiary_weapons = []
        proficiencies_names = [x.name for x in pProficiencies] if pProficiencies else None
        if self.WeaponSword != "0":
            weapon_type = ItemType.SWORD
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponSword == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponSword == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponSword == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponLance != "0":
            weapon_type = ItemType.LANCE
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponLance == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponLance == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponLance == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponAxe != "0":
            weapon_type = ItemType.AXE
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponAxe == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponAxe == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponAxe == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponBow != "0":
            weapon_type = ItemType.BOW
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponBow == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponBow == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponBow == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponDagger != "0":
            weapon_type = ItemType.DAGGER
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponDagger == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponDagger == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponDagger == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponMagic != "0":
            weapon_type = ItemType.TOME
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponMagic == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponMagic == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponMagic == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponRod != "0":
            weapon_type = ItemType.STAFF
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponRod == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponRod == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponRod == "3":
                    job_tertiary_weapons.append(weapon_type)
        if self.WeaponFist != "0":
            weapon_type = ItemType.ART
            if pProficiencies == None or weapon_type.name in proficiencies_names:
                if self.WeaponFist == "1":
                    job_weapons.append(weapon_type)
                elif self.WeaponFist == "2":
                    job_variant_weapons.append(weapon_type)
                elif self.WeaponFist == "3":
                    job_tertiary_weapons.append(weapon_type)

        # Randomly add a variant weapon to the main job_weapons array
        if job_variant_weapons:
            # Handle case for advanced classes where the main weapon is variant
            if not job_weapons:
                job_weapons = [x for x in job_variant_weapons if x.name == pProficiencies[0].name]
            else:
                job_weapons += [random.choice(job_variant_weapons)]
        
        if job_tertiary_weapons:
            job_weapons += job_tertiary_weapons

        return job_weapons
    