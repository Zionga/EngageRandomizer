import argparse
import os
import os.path
import shutil
import xml.etree.ElementTree as ET
import random
import UnityPy
import copy
from items import SID_SMASH, Item, ItemType
from jobs import Job
from settings import BANNED_WEAPONS, GenericSetting, RecruitmentOrder, BANNED_JIDS

from units import Unit

ALEAR_PID = "PID_リュール"
VEYLE_PID = "PID_ヴェイル"

class Randomizer():
    def __init__(self, **kwargs) -> None:
        self.input_path = None
        self.output_path = None
        self.recruitment = None
        self.unit_job = None
        self.bases = None
        self.swap_stat = None

        self.units:list[Unit] = None
        self.random_units = None
        self.jobs:list[Job] = None
        self.items:list[Item] = None

    def print_settings(self):
        recruitment_order = "Normal"
        if int(self.recruitment) == 1:
            recruitment_order = "Random"
        elif int(self.recruitment) == 2:
            recruitment_order = "Reversed"
    
        print("Recruitment order: ", recruitment_order)
        print("Unit class: ", "Random" if int(self.unit_job) else "Original")
        print("Bases: ", "Random" if int(self.bases) else "Original")
        print("Adjust Str/Mag and Def/Res: ", "Adjust" if int(self.swap_stat) else "Don't adjust")

    def randomize(self, **kwargs):
        try:
            self.input_path = kwargs.get("input_path", None)
            self.output_path = kwargs.get("output_path", None)
            self.unit_job = kwargs.get("unit_job", 0)
            self.recruitment = kwargs.get("recruitment", 0)
            self.bases = kwargs.get("bases", 0)
            self.swap_stat = kwargs.get("swap_stat", 0)

            if not self.output_path:
                print("No output path provided")
                return False
            
            if not self.input_path:
                print("No input path provided")
                return False
            
            if self.input_path == self.output_path:
                print("The input and output must be different")
                return False
            
            self.recruitment = int(self.recruitment)
            self.bases = int(self.bases)
            self.swap_stat = int(self.swap_stat)

            self.print_settings()
            
            self.output_path = self.output_path.strip()
            self.input_path = self.input_path.strip()
            self.jobs = self.get_playable_jobs(f"{self.input_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata\\job.xml.bundle", f"{self.output_path}\\temp")
            self.items = self.get_usable_items(f"{self.input_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata\\item.xml.bundle", f"{self.output_path}\\temp")
            self.units = self.get_playable_units(f"{self.input_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata\\person.xml.bundle", f"{self.output_path}\\temp")
            if self.units:
                self.random_units = self.randomize_units()
                self.edit_person_xml(f"{self.input_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata\\person.xml.bundle")
                self.replace_units()
                print("All done!")
                self.delete_temp_files()
                return True
        except Exception as err:
            print(f"[randomize]: {err}")
            self.delete_temp_files()
            return False

    def randomize_units(self):
        shuffle_alear = False
        shuffle_veyle = False

        # Shuffle order
        if self.recruitment != RecruitmentOrder.NORMAL.value:
            alear_info = self.units[0]
            shuffled = copy.deepcopy(self.units) if shuffle_alear else copy.deepcopy(self.units[1:])
            if self.recruitment == RecruitmentOrder.RANDOM.value:
                random.shuffle(shuffled)
            else:
                shuffled = list(reversed(shuffled))
            # Don't shuffle Alear... for now.
            if not shuffle_alear:
                shuffled = copy.copy([alear_info]) + shuffled
        else:
            shuffled = copy.deepcopy(self.units)
        
        # Randomize stats, class, etc.
        unit:Unit
        for index, unit in enumerate(shuffled):
            # Get the info of the original unit
            og_unit:Unit = self.units[index]
            unit.ReplacePid = og_unit.Pid
            unit.ReplaceName = og_unit.Name

            # Randomize class
            # Get the info of the original unit's class
            job_filter = [job for job in self.jobs if job.Jid == og_unit.Jid]
            if not job_filter:
                raise Exception(f"[randomize_units] Couldn't find Jid '{og_unit.Jid}'")
            og_job = job_filter[0]
            
            if self.unit_job == GenericSetting.RANDOM.value:
                # Pick a new class with the same rank
                new_job = random.choice([job for job in self.jobs if job.Rank == og_job.Rank and job.Jid != unit.Jid and job.Jid not in BANNED_JIDS])
            else:
                # Keep the same class line but promote or demote depending on the unit who is going to be replaced
                new_job = self.promote_demote_job(unit.Jid, og_job.Rank)
            
            unit.Jid = new_job.Jid
            unit.Job = new_job

            # Randomize proficiency
            # Coming soon™

            # Change stats
            # Level
            unit.Level = og_unit.Level
            unit.InternalLevel = og_unit.InternalLevel
            unit.SkillPoint = og_unit.SkillPoint
            
            # Bases
            stats = ["Hp", "Str", "Tech", "Quick", "Luck", "Def", "Magic", "Mdef", "Phys"]
            offset_types = ["N", "H", "L"]
            if self.bases == GenericSetting.RANDOM.value:
                new_bases = self.randomize_bases(og_unit)
                for stat_index, stat in enumerate(stats):
                    for offset_type in offset_types:
                        setattr(unit, f"Offset{offset_type}{stat}", new_bases[stat_index])
            else:
                for stat in stats:
                    for offset_type in offset_types:
                        offset_attr = f"Offset{offset_type}{stat}"
                        setattr(unit, offset_attr, getattr(og_unit, offset_attr))

            # Swap Str/Mag depending on the new class and the unit's growth rates
            # To determine this we compare the growth rates (at least for now)
            if self.swap_stat == GenericSetting.RANDOM.value:
                # jobIsPhysical = new_job.WeaponMagic == "0" or new_job.WeaponRod == "0"
                jobIsPhysical = new_job.LimitStr > new_job.LimitMagic
                unitIsPhysical = int(unit.GrowStr) > int(unit.GrowMagic)
                if unitIsPhysical != jobIsPhysical:
                    copy_unit = copy.copy(unit)
                    # Growth rates
                    unit.GrowStr = copy_unit.GrowMagic
                    unit.GrowDef = copy_unit.GrowMdef
                    unit.GrowMagic = copy_unit.GrowStr
                    unit.GrowMdef = copy_unit.GrowDef

                    # Bases Normal
                    unit.OffsetNStr = copy_unit.OffsetNMagic
                    unit.OffsetNDef = copy_unit.OffsetNMdef
                    unit.OffsetNMagic = copy_unit.OffsetNStr
                    unit.OffsetNMdef = copy_unit.OffsetNDef

                    # Bases Hard
                    unit.OffsetHStr = copy_unit.OffsetHMagic
                    unit.OffsetHDef = copy_unit.OffsetHMdef
                    unit.OffsetHMagic = copy_unit.OffsetHStr
                    unit.OffsetHMdef = copy_unit.OffsetHDef

                    # Bases Maddening
                    unit.OffsetLStr = copy_unit.OffsetLMagic
                    unit.OffsetLDef = copy_unit.OffsetLMdef
                    unit.OffsetLMagic = copy_unit.OffsetLStr
                    unit.OffsetLMdef = copy_unit.OffsetLDef

            # Randomize starting items (when applicable)
            if og_unit.Items:
                unit.Items = og_unit.Items
                new_items = self.randomize_unit_items(unit)
                # Apply changes
                new_items_str = ";".join([x.Iid for x in new_items]) + ";"
                unit.Items = new_items_str
            else:
                unit.Items = ""

        print("New order:")
        for x in shuffled:
            print(f"{x.ReplaceName} -> {x.Name}")

        return shuffled

    def randomize_bases(self, pUnit:Unit) -> list[int]:
        """
        Randomize the bases of the given unit
        """
        # Since i couldn't think of another way i'm just going to sum all the unit's bases and redistribute them
        stats = ["Hp", "Str", "Tech", "Quick", "Luck", "Def", "Magic", "Mdef", "Phys"]
        new_bases = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        bases_total = 0
        negative_bases_total = 0
        for stat in stats:
            stat_value = int(getattr(pUnit, f"OffsetN{stat}"))
            if stat_value > 0:
                bases_total += stat_value
            else:
                negative_bases_total += stat_value
        # bases_total += max(int(pUnit.OffsetNHp), 0)
        # bases_total += max(int(pUnit.OffsetNStr), 0)
        # bases_total += max(int(pUnit.OffsetNTech), 0)
        # bases_total += max(int(pUnit.OffsetNQuick), 0)
        # bases_total += max(int(pUnit.OffsetNLuck), 0)
        # bases_total += max(int(pUnit.OffsetNDef), 0)
        # bases_total += max(int(pUnit.OffsetNMagic), 0)
        # bases_total += max(int(pUnit.OffsetNMdef), 0)
        # bases_total += max(int(pUnit.OffsetNPhys), 0)

        # if bases_total <= 0:
        #     return new_bases

        # Randomly determine the order we're going to loop through the new_bases array
        bases_left = bases_total
        negative_bases_left = abs(negative_bases_total)
        order = list(range(len(new_bases)))
        
        # Redistribute positive bases
        while bases_left > 0:
            random.shuffle(order)
            for index in order:
                # Randomly assign value to the base stat
                random_value = random.randrange(0, bases_left + 1)
                new_bases[index] += random_value
                bases_left -= random_value
                if bases_left <= 0:
                    break

        # Redistribute negative bases
        while negative_bases_left > 0:
            random.shuffle(order)
            for index in order:
                # Randomly assign value to the base stat
                random_value = random.randrange(0, negative_bases_left + 1)
                new_bases[index] -= random_value
                negative_bases_left -= random_value
                if negative_bases_left <= 0:
                    break

        return new_bases

    def randomize_unit_items(self, pUnit:Unit, pItems:list[Item] = None) -> list[Item]:
        """
        Randomize a list of items for the given unit.
        If a list of items is not provided then this function will attempt to use the items from the "Items" attribute of the unit.
        """
        new_items = []
        if not pItems:
            # No items provided so we extract the unit's items from the Items attribute
            item_iids = [item for item in pUnit.Items.split(";") if item]
            pItems = [item for item in self.items if item.Iid in item_iids]

        # Get the unit's usable weapon types
        usable_weapon_types = pUnit.Job.get_job_weapons()
        # Loop through each item
        item:Item
        for item in pItems:
            # Only randomize weapons
            if item.get_item_type() != ItemType.CONSUMABLE:
                new_item = None
                # # # Randomize magical weapons
                # # if item.is_magic_weapon():
                # #     new_item = random.choice([x for x in self.items if x.get_item_type() in usable_weapon_types and x.WeaponLevel == item.WeaponLevel and x.Flag == "65536" and x not in new_items])
                # # # Randomize smash weapons
                # # elif item.is_smash_weapon():
                # #     new_item = random.choice([x for x in self.items if x.get_item_type() in usable_weapon_types and x.WeaponLevel == item.WeaponLevel and x.EquipSids.find(SID_SMASH) != -1 and x not in new_items])
                # # # Randomize by range
                # # elif int(item.RangeO) >= 2:
                # #     new_item = random.choice([x for x in self.items if x.get_item_type() in usable_weapon_types and x.WeaponLevel == item.WeaponLevel and int(x.RangeO) >= 2 and x not in new_items])

                # # # Generic randomize
                # # if not new_item:
                # # new_item = random.choice([x for x in self.items if x.get_item_type() in usable_weapon_types and x.WeaponLevel == item.WeaponLevel and x not in new_items])
                
                item_filter = [x for x in self.items if x.get_item_type() in usable_weapon_types and x.WeaponLevel == item.WeaponLevel and x.Iid not in BANNED_WEAPONS and x not in new_items]
                if not item_filter:
                    item_filter = [x for x in self.items if x.get_item_type() in usable_weapon_types and x.WeaponLevel == item.WeaponLevel]
                new_item = random.choice(item_filter)
                new_items.append(new_item)
                
            else:
                # Consumables won't be randomized (at least for now...)
                new_items.append(item)


        return new_items

    def replace_units(self, **kwargs):
        print("Replacing units...")
        dispos_path = os.fsencode(f"{self.input_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata\\dispos")
        scripts_path = f"{self.input_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_scripts"
        dispos_output_path = f"{self.output_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata\\dispos"
        temp_dispos_output_path = f"{self.output_path}\\temp\\dispos"
        scripts_output_path = f"{self.output_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_scripts"

        # Replace units in dispos
        # print("Reading dispos...")
        if not os.path.exists(dispos_output_path):
            os.makedirs(dispos_output_path)
        if not os.path.exists(temp_dispos_output_path):
            os.makedirs(temp_dispos_output_path)
        for file in os.listdir(dispos_path):
            filename = os.fsdecode(file)
            if (filename.startswith("m0") or filename.startswith("s0")) and filename.endswith(".xml.bundle"): 
                # print("------------------------")
                # print(f"Reading {filename}")
                unity_env = UnityPy.load(os.path.join(os.fsdecode(dispos_path), filename))
                # Read the bundle file
                for obj in unity_env.objects:
                    if obj.type.name == "TextAsset":
                        # Replace the units in the xml
                        dispos_data = obj.read()
                        dispos_text = dispos_data.text
                        # Create a temporary xml for this dispos in our output path
                        temp_file_path = f"{temp_dispos_output_path}\\{dispos_data.name}.xml"
                        with open(temp_file_path, 'wb') as temp_dispos_file:
                            temp_dispos_file.write(dispos_data.script)
                            temp_dispos_file.close()
                        # Open the temp dispos file and search for units to replace
                        tree = ET.parse(temp_file_path)
                        root = tree.getroot()
                        for child in root.findall(".//*[@Name='配置']/Data/Param"):
                            unit_filter = [x for x in self.random_units if child.attrib["Pid"] == x.ReplacePid]
                            if unit_filter:
                                unit = unit_filter[0]
                                # Replace the PID.
                                # print(f"Replacing {unit.ReplaceName} with {unit.Name}")
                                child.set("Pid", f"{unit.Pid}")
                                # Get items
                                unit_items = []
                                for item_index in range(1,7):
                                    current_item_iid = child.attrib[f"Item{item_index}.Iid"]
                                    if current_item_iid:
                                        item_filter = [x for x in self.items if x.Iid == current_item_iid]
                                        if item_filter:
                                            unit_items.append(item_filter[0])
                                if unit_items:
                                    # Randomize items
                                    new_items = self.randomize_unit_items(unit, unit_items)
                                    # Apply changes
                                    item:Item
                                    for item_index, item in enumerate(new_items):
                                        child.set(f"Item{item_index + 1}.Iid", item.Iid)

                        # Save the new dispos xml
                        new_dispos_path = f"{temp_dispos_output_path}\\{dispos_data.name}_new.xml"
                        tree.write(new_dispos_path, encoding="utf-8")

                        # Add the new dispos xml to the bundle
                        with open(new_dispos_path, "rb") as new_dispos_xml:
                            dispos_data.script = new_dispos_xml.read()
                            dispos_data.save()
                            new_dispos_xml.close()

                        # Create dispos file in output
                        file_path = dispos_output_path + "\\" + filename
                        with open(file_path, 'wb') as dispos_file:
                            dispos_file.write(unity_env.file.save())
                            dispos_file.close()

        # Replace units in scripts
        # print("**********************************************************************")
        # print("Reading scripts...")
        if not os.path.exists(scripts_output_path):
            os.makedirs(scripts_output_path)
        for file in os.listdir(scripts_path):
            filename = os.fsdecode(file)
            if (filename.startswith("m0") or filename.startswith("s0")) and filename.endswith(".txt.bundle"): 
                # print("------------------------")
                # print(f"Reading {filename}")
                unity_env = UnityPy.load(os.path.join(os.fsdecode(scripts_path), filename))
                # Read the bundle file
                for obj in unity_env.objects:
                    if obj.type.name == "TextAsset":
                        # Replace the units in the xml
                        script_data = obj.read()
                        script_text = script_data.text
                        for unit in self.random_units:
                            pid_value = f'"{unit.ReplacePid}"'
                            if script_text.find(pid_value) != -1:
                                # Replace the PID. We add __SWAP at the end to make sure the value won't be overwritten by another unit
                                # print(f"Replacing {unit.ReplaceName} with {unit.Name}")
                                script_text = script_text.replace(pid_value, f'"{unit.Pid}__SWAP"')
                        
                        # After we finished looping each unit we delete the __SWAP helper from the text
                        script_text = script_text.replace("__SWAP", "")

                        # Insert the new text on the bundled file and save it in our output
                        script_data.text = script_text
                        script_data.save()

                        # Create script file in output
                        file_path = scripts_output_path + "\\" + filename
                        with open(file_path, 'wb') as script_file:
                            script_file.write(unity_env.file.save())
                            script_file.close()
    
        print("Done replacing units.")

    def get_playable_units(self, input_path, output_path):
        print("Extracting person.xml...")

        unity_env = UnityPy.load(input_path)
        file_path = None
        unit_list = None
        # Read and extract the bundle file
        for obj in unity_env.objects:
            if obj.type.name == "TextAsset":
                # Replace the units in the xml
                person_data = obj.read()
                # Create person file in output
                file_path = output_path + "\\" + "person.xml"
                with open(file_path, 'wb') as person_file:
                    person_file.write(person_data.script)
                    person_file.close()
        
        if not file_path:
            print("Couldn't parse jobs.xml")
            return None

        # Read persons.xml
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Check if person is playable
        # a person is playable if NetRankingIndex != 0
        unit_list = []
        for child in root.findall(".//*[@NetRankingIndex!='0']"):
            unit = Unit(
                Pid = child.attrib["Pid"],
                Name = child.attrib["Name"],
                Jid = child.attrib["Jid"],
                Gender = child.attrib["Gender"],
                Level = child.attrib["Level"],
                InternalLevel = child.attrib["InternalLevel"],
                SkillPoint = child.attrib["SkillPoint"],
                Aptitude = child.attrib["Aptitude"],
                SubAptitude = child.attrib["SubAptitude"],
                OffsetNHp = child.attrib["OffsetN.Hp"],
                OffsetNStr = child.attrib["OffsetN.Str"],
                OffsetNTech = child.attrib["OffsetN.Tech"],
                OffsetNQuick = child.attrib["OffsetN.Quick"],
                OffsetNLuck = child.attrib["OffsetN.Luck"],
                OffsetNDef = child.attrib["OffsetN.Def"],
                OffsetNMagic = child.attrib["OffsetN.Magic"],
                OffsetNMdef = child.attrib["OffsetN.Mdef"],
                OffsetNPhys = child.attrib["OffsetN.Phys"],
                OffsetNSight = child.attrib["OffsetN.Sight"],
                OffsetNMove = child.attrib["OffsetN.Move"],
                OffsetHHp = child.attrib["OffsetH.Hp"],
                OffsetHStr = child.attrib["OffsetH.Str"],
                OffsetHTech = child.attrib["OffsetH.Tech"],
                OffsetHQuick = child.attrib["OffsetH.Quick"],
                OffsetHLuck = child.attrib["OffsetH.Luck"],
                OffsetHDef = child.attrib["OffsetH.Def"],
                OffsetHMagic = child.attrib["OffsetH.Magic"],
                OffsetHMdef = child.attrib["OffsetH.Mdef"],
                OffsetHPhys = child.attrib["OffsetH.Phys"],
                OffsetHSight = child.attrib["OffsetH.Sight"],
                OffsetHMove = child.attrib["OffsetH.Move"],
                OffsetLHp = child.attrib["OffsetL.Hp"],
                OffsetLStr = child.attrib["OffsetL.Str"],
                OffsetLTech = child.attrib["OffsetL.Tech"],
                OffsetLQuick = child.attrib["OffsetL.Quick"],
                OffsetLLuck = child.attrib["OffsetL.Luck"],
                OffsetLDef = child.attrib["OffsetL.Def"],
                OffsetLMagic = child.attrib["OffsetL.Magic"],
                OffsetLMdef = child.attrib["OffsetL.Mdef"],
                OffsetLPhys = child.attrib["OffsetL.Phys"],
                OffsetLSight = child.attrib["OffsetL.Sight"],
                OffsetLMove = child.attrib["OffsetL.Move"],
                LimitHp = child.attrib["Limit.Hp"],
                LimitStr = child.attrib["Limit.Str"],
                LimitTech = child.attrib["Limit.Tech"],
                LimitQuick = child.attrib["Limit.Quick"],
                LimitLuck = child.attrib["Limit.Luck"],
                LimitDef = child.attrib["Limit.Def"],
                LimitMagic= child.attrib["Limit.Magic"],
                LimitMdef= child.attrib["Limit.Mdef"],
                LimitPhys = child.attrib["Limit.Phys"],
                LimitSight = child.attrib["Limit.Sight"],
                LimitMove = child.attrib["Limit.Move"],
                GrowHp = child.attrib["Grow.Hp"],
                GrowStr = child.attrib["Grow.Str"],
                GrowTech = child.attrib["Grow.Tech"],
                GrowQuick = child.attrib["Grow.Quick"],
                GrowLuck = child.attrib["Grow.Luck"],
                GrowDef = child.attrib["Grow.Def"],
                GrowMagic = child.attrib["Grow.Magic"],
                GrowMdef = child.attrib["Grow.Mdef"],
                GrowPhys = child.attrib["Grow.Phys"],
                GrowSight = child.attrib["Grow.Sight"],
                GrowMove = child.attrib["Grow.Move"],
                Items = child.attrib["Items"],
                Hometown = child.attrib["Hometown"],
                NetRankingIndex = child.attrib["NetRankingIndex"],
            )

            unit_list.append(unit)
        
        return unit_list

    def get_playable_jobs(self, input_path, output_path):
        print("Creating jobs_playable.xml...")
        
        unity_env = UnityPy.load(input_path)
        file_path = None
        job_list = None
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # Read and extract the bundle file
        for obj in unity_env.objects:
            if obj.type.name == "TextAsset":
                # Replace the units in the xml
                jobs_data = obj.read()
                # Create jobs file in output
                file_path = output_path + "\\" + "jobs.xml"
                with open(file_path, 'wb') as jobs_file:
                    jobs_file.write(jobs_data.script)
                    jobs_file.close()
        
        if not file_path:
            print("Couldn't parse jobs.xml")
            return None
        
        # Read the jobs.xml and extract all playable classes
        tree = ET.parse(file_path)
        root = tree.getroot()
        job_list = []

        for child in root.findall(".//*[@Name='兵種']/Data/Param"):
            # A class is playable if sort is not 9999
            if child.attrib["Sort"] != "9999":
                job = Job(
                    Jid = child.attrib["Jid"],
                    Aid = child.attrib["Aid"],
                    Name = child.attrib["Name"],
                    Help = child.attrib["Help"],
                    UnitIconID_M = child.attrib["UnitIconID_M"],
                    UnitIconID_F = child.attrib["UnitIconID_F"],
                    UnitIconWeaponID = child.attrib["UnitIconWeaponID"],
                    Rank = child.attrib["Rank"],
                    StyleName = child.attrib["StyleName"],
                    MoveType = child.attrib["MoveType"],
                    StepFrame = child.attrib["StepFrame"],
                    MaxLevel = child.attrib["MaxLevel"],
                    InternalLevel = child.attrib["InternalLevel"],
                    Sort = child.attrib["Sort"],
                    Flag = child.attrib["Flag"],
                    WeaponNone = child.attrib["WeaponNone"],
                    WeaponSword = child.attrib["WeaponSword"],
                    WeaponLance = child.attrib["WeaponLance"],
                    WeaponAxe = child.attrib["WeaponAxe"],
                    WeaponBow = child.attrib["WeaponBow"],
                    WeaponDagger = child.attrib["WeaponDagger"],
                    WeaponMagic = child.attrib["WeaponMagic"],
                    WeaponRod = child.attrib["WeaponRod"],
                    WeaponFist = child.attrib["WeaponFist"],
                    WeaponSpecial = child.attrib["WeaponSpecial"],
                    WeaponTool = child.attrib["WeaponTool"],
                    MaxWeaponLevelNone = child.attrib["MaxWeaponLevelNone"],
                    MaxWeaponLevelSword = child.attrib["MaxWeaponLevelSword"],
                    MaxWeaponLevelLance = child.attrib["MaxWeaponLevelLance"],
                    MaxWeaponLevelAxe = child.attrib["MaxWeaponLevelAxe"],
                    MaxWeaponLevelBow = child.attrib["MaxWeaponLevelBow"],
                    MaxWeaponLevelDagger = child.attrib["MaxWeaponLevelDagger"],
                    MaxWeaponLevelMagic = child.attrib["MaxWeaponLevelMagic"],
                    MaxWeaponLevelRod = child.attrib["MaxWeaponLevelRod"],
                    MaxWeaponLevelFist = child.attrib["MaxWeaponLevelFist"],
                    MaxWeaponLevelSpecial = child.attrib["MaxWeaponLevelSpecial"],
                    BaseHp = child.attrib["Base.Hp"],
                    BaseStr = child.attrib["Base.Str"],
                    BaseTech = child.attrib["Base.Tech"],
                    BaseQuick = child.attrib["Base.Quick"],
                    BaseLuck = child.attrib["Base.Luck"],
                    BaseDef = child.attrib["Base.Def"],
                    BaseMagic = child.attrib["Base.Magic"],
                    BaseMdef = child.attrib["Base.Mdef"],
                    BasePhys = child.attrib["Base.Phys"],
                    BaseSight = child.attrib["Base.Sight"],
                    BaseMove = child.attrib["Base.Move"],
                    LimitHp = child.attrib["Limit.Hp"],
                    LimitStr = child.attrib["Limit.Str"],
                    LimitTech = child.attrib["Limit.Tech"],
                    LimitQuick = child.attrib["Limit.Quick"],
                    LimitLuck = child.attrib["Limit.Luck"],
                    LimitDef = child.attrib["Limit.Def"],
                    LimitMagic = child.attrib["Limit.Magic"],
                    LimitMdef = child.attrib["Limit.Mdef"],
                    LimitPhys = child.attrib["Limit.Phys"],
                    LimitSight = child.attrib["Limit.Sight"],
                    LimitMove = child.attrib["Limit.Move"],
                    BaseGrowHp = child.attrib["BaseGrow.Hp"],
                    BaseGrowStr = child.attrib["BaseGrow.Str"],
                    BaseGrowTech = child.attrib["BaseGrow.Tech"],
                    BaseGrowQuick = child.attrib["BaseGrow.Quick"],
                    BaseGrowLuck = child.attrib["BaseGrow.Luck"],
                    BaseGrowDef = child.attrib["BaseGrow.Def"],
                    BaseGrowMagic = child.attrib["BaseGrow.Magic"],
                    BaseGrowMdef = child.attrib["BaseGrow.Mdef"],
                    BaseGrowPhys = child.attrib["BaseGrow.Phys"],
                    BaseGrowSight = child.attrib["BaseGrow.Sight"],
                    BaseGrowMove = child.attrib["BaseGrow.Move"],
                    DiffGrowHp = child.attrib["DiffGrow.Hp"],
                    DiffGrowStr = child.attrib["DiffGrow.Str"],
                    DiffGrowTech = child.attrib["DiffGrow.Tech"],
                    DiffGrowQuick = child.attrib["DiffGrow.Quick"],
                    DiffGrowLuck = child.attrib["DiffGrow.Luck"],
                    DiffGrowDef = child.attrib["DiffGrow.Def"],
                    DiffGrowMagic = child.attrib["DiffGrow.Magic"],
                    DiffGrowMdef = child.attrib["DiffGrow.Mdef"],
                    DiffGrowPhys = child.attrib["DiffGrow.Phys"],
                    DiffGrowSight = child.attrib["DiffGrow.Sight"],
                    DiffGrowMove = child.attrib["DiffGrow.Move"],
                    DiffGrowNormalHp = child.attrib["DiffGrowNormal.Hp"],
                    DiffGrowNormalStr = child.attrib["DiffGrowNormal.Str"],
                    DiffGrowNormalTech = child.attrib["DiffGrowNormal.Tech"],
                    DiffGrowNormalQuick = child.attrib["DiffGrowNormal.Quick"],
                    DiffGrowNormalLuck = child.attrib["DiffGrowNormal.Luck"],
                    DiffGrowNormalDef = child.attrib["DiffGrowNormal.Def"],
                    DiffGrowNormalMagic = child.attrib["DiffGrowNormal.Magic"],
                    DiffGrowNormalMdef = child.attrib["DiffGrowNormal.Mdef"],
                    DiffGrowNormalPhys = child.attrib["DiffGrowNormal.Phys"],
                    DiffGrowNormalSight = child.attrib["DiffGrowNormal.Sight"],
                    DiffGrowNormalMove = child.attrib["DiffGrowNormal.Move"],
                    DiffGrowHardHp = child.attrib["DiffGrowHard.Hp"],
                    DiffGrowHardStr = child.attrib["DiffGrowHard.Str"],
                    DiffGrowHardTech = child.attrib["DiffGrowHard.Tech"],
                    DiffGrowHardQuick = child.attrib["DiffGrowHard.Quick"],
                    DiffGrowHardLuck = child.attrib["DiffGrowHard.Luck"],
                    DiffGrowHardDef = child.attrib["DiffGrowHard.Def"],
                    DiffGrowHardMagic = child.attrib["DiffGrowHard.Magic"],
                    DiffGrowHardMdef = child.attrib["DiffGrowHard.Mdef"],
                    DiffGrowHardPhys = child.attrib["DiffGrowHard.Phys"],
                    DiffGrowHardSight = child.attrib["DiffGrowHard.Sight"],
                    DiffGrowHardMove = child.attrib["DiffGrowHard.Move"],
                    DiffGrowLunaticHp = child.attrib["DiffGrowLunatic.Hp"],
                    DiffGrowLunaticStr = child.attrib["DiffGrowLunatic.Str"],
                    DiffGrowLunaticTech = child.attrib["DiffGrowLunatic.Tech"],
                    DiffGrowLunaticQuick = child.attrib["DiffGrowLunatic.Quick"],
                    DiffGrowLunaticLuck = child.attrib["DiffGrowLunatic.Luck"],
                    DiffGrowLunaticDef = child.attrib["DiffGrowLunatic.Def"],
                    DiffGrowLunaticMagic = child.attrib["DiffGrowLunatic.Magic"],
                    DiffGrowLunaticMdef = child.attrib["DiffGrowLunatic.Mdef"],
                    DiffGrowLunaticPhys = child.attrib["DiffGrowLunatic.Phys"],
                    DiffGrowLunaticSight = child.attrib["DiffGrowLunatic.Sight"],
                    DiffGrowLunaticMove = child.attrib["DiffGrowLunatic.Move"],
                    HighJob1 = child.attrib["HighJob1"],
                    HighJob2 = child.attrib["HighJob2"],
                    LowJob = child.attrib["LowJob"],
                    CCItems = child.attrib["CCItems"],
                    ShortName = child.attrib["ShortName"],
                    UniqueItems = child.attrib["UniqueItems"],
                    Skills = child.attrib["Skills"],
                    LearningSkill = child.attrib["LearningSkill"],
                    LunaticSkill = child.attrib["LunaticSkill"],
                    Attrs = child.attrib["Attrs"],
                )

                job_list.append(job)


        return job_list
    
    def get_usable_items(self, input_path, output_path):
        print("Extracting item.xml...")
        
        unity_env = UnityPy.load(input_path)
        file_path = None
        item_list = None
        # Read and extract the bundle file
        for obj in unity_env.objects:
            if obj.type.name == "TextAsset":
                # Replace the units in the xml
                items_data = obj.read()
                # Create items file in output
                file_path = output_path + "\\" + "items.xml"
                with open(file_path, 'wb') as items_file:
                    items_file.write(items_data.script)
                    items_file.close()
        
        if not file_path:
            print("Couldn't parse items.xml")
            return None
        
        # Read the items.xml and extract all playable classes
        tree = ET.parse(file_path)
        root = tree.getroot()
        item_list = []

        for child in root.findall(".//*[@Name='アイテム']/Data/Param"):
            # An item is a usable (not enemy or emblem exclusive) if...
            # * Kind value <= 8 and Kind value == 10
            # * Has a WeaponLevel
            # * EquipCondition is empty (this will remove all PRFs from the pool, will iron this out later...)
            # * Price is not 100
            is_weapon = int(child.attrib["Kind"]) <= 8 \
                and child.attrib["WeaponLevel"] != "" \
                and child.attrib["EquipCondition"] == "" \
                and child.attrib["Price"] != "100"
            is_consumable = int(child.attrib["Kind"]) == 10 \
                and child.attrib["Price"] != "100"
            if is_weapon or is_consumable:
                item = Item(
                    Out = child.attrib["Out"],
                    Iid = child.attrib["Iid"],
                    Name = child.attrib["Name"],
                    Help = child.attrib["Help"],
                    Tutorial = child.attrib["Tutorial"],
                    Aid = child.attrib["Aid"],
                    Kind = child.attrib["Kind"],
                    UseType = child.attrib["UseType"],
                    WeaponAttr = child.attrib["WeaponAttr"],
                    Icon = child.attrib["Icon"],
                    Endurance = child.attrib["Endurance"],
                    Power = child.attrib["Power"],
                    Weight = child.attrib["Weight"],
                    RangeI = child.attrib["RangeI"],
                    RangeO = child.attrib["RangeO"],
                    Distance = child.attrib["Distance"],
                    Hit = child.attrib["Hit"],
                    Critical = child.attrib["Critical"],
                    Avoid = child.attrib["Avoid"],
                    Secure = child.attrib["Secure"],
                    EnhanceHp = child.attrib["Enhance.Hp"],
                    EnhanceStr = child.attrib["Enhance.Str"],
                    EnhanceTech = child.attrib["Enhance.Tech"],
                    EnhanceQuick = child.attrib["Enhance.Quick"],
                    EnhanceLuck = child.attrib["Enhance.Luck"],
                    EnhanceDef = child.attrib["Enhance.Def"],
                    EnhanceMagic = child.attrib["Enhance.Magic"],
                    EnhanceMdef = child.attrib["Enhance.Mdef"],
                    EnhancePhys = child.attrib["Enhance.Phys"],
                    EnhanceMove = child.attrib["Enhance.Move"],
                    GrowRatioHp = child.attrib["GrowRatio.Hp"],
                    GrowRatioStr = child.attrib["GrowRatio.Str"],
                    GrowRatioTech = child.attrib["GrowRatio.Tech"],
                    GrowRatioQuick = child.attrib["GrowRatio.Quick"],
                    GrowRatioLuck = child.attrib["GrowRatio.Luck"],
                    GrowRatioDef = child.attrib["GrowRatio.Def"],
                    GrowRatioMagic = child.attrib["GrowRatio.Magic"],
                    GrowRatioMdef = child.attrib["GrowRatio.Mdef"],
                    GrowRatioPhys = child.attrib["GrowRatio.Phys"],
                    GrowRatioMove = child.attrib["GrowRatio.Move"],
                    Price = child.attrib["Price"],
                    WeaponLevel = child.attrib["WeaponLevel"],
                    RodType = child.attrib["RodType"],
                    RodExp = child.attrib["RodExp"],
                    RateArena = child.attrib["RateArena"],
                    ShootEffect = child.attrib["ShootEffect"],
                    HitEffect = child.attrib["HitEffect"],
                    CannonEffect = child.attrib["CannonEffect"],
                    AttackMotion = child.attrib["AttackMotion"],
                    OverlapTerrain = child.attrib["OverlapTerrain"],
                    EquipCondition = child.attrib["EquipCondition"],
                    Flag = child.attrib["Flag"],
                    EquipSids = child.attrib["EquipSids"],
                    PassiveSids = child.attrib["PassiveSids"],
                    GiveSids = child.attrib["GiveSids"],
                    AddTarget = child.attrib["AddTarget"],
                    AddRange = child.attrib["AddRange"],
                    AddType = child.attrib["AddType"],
                    AddPower = child.attrib["AddPower"],
                    AddSids = child.attrib["AddSids"],
                    AddEffect = child.attrib["AddEffect"],
                    AddHelp = child.attrib["AddHelp"],
                    HighRankItem = child.attrib["HighRankItem"],
                )

                item_list.append(item)


        return item_list
    
    def promote_demote_job(self, jid:str, rank:str):
        """
        Returns a basic or advanced job related to the give job and rank.
        If a basic job has multiple advanced jobs then one will be picked at random.
        If an avanced job has a basic job that has variant weapons then one will be picked at random. 
        """
        job_filter = [job for job in self.jobs if job.Jid == jid]
        if not job_filter:
            raise Exception(f"[promote_demote_job] Couldn't find Jid '{jid}'")
        job = job_filter[0]

        if job.Rank == rank:
            return job
        
        related_jobs = []
        
        if rank == "0":
            # Search basic jobs
            related_jobs = [x for x in self.jobs if x.Rank == rank and (x.HighJob1 == job.Jid or x.HighJob2 == job.Jid)]
        elif rank == "1":
            # Search advanced jobs
            related_jobs = [x for x in self.jobs if x.Rank == rank and (job.HighJob1 == x.Jid or job.HighJob2 == x.Jid)]

        if not related_jobs:
            # No jobs found. This may happen with special jobs such as Dancer and Thief
            related_jobs = [job]
        
        return random.choice(related_jobs)


    def edit_person_xml(self, input_path):
        print("Editing person.xml...")
        
        unity_env = UnityPy.load(input_path)
        person_output_path = f"{self.output_path}\\Data\\StreamingAssets\\aa\\Switch\\fe_assets_gamedata"
        file_path = None

        # Read and edit person.xml
        tree = ET.parse(f"{self.output_path}\\temp\\person.xml")
        root = tree.getroot()

        stats = ["Hp", "Str", "Tech", "Quick", "Luck", "Def", "Magic", "Mdef", "Phys", "Sight", "Move"]
        offset_types = ["N", "H", "L"]
        # A unit is playable if NetRankingIndex != 0
        for child in root.findall(".//*[@NetRankingIndex!='0']"):
            # Get the randomized unit
            unit_filter = [x for x in self.random_units if x.Pid == child.attrib["Pid"]]
            if not unit_filter:
                raise Exception(f"[edit_person_xml] Couldn't find unit with Pid '{child.attrib['Pid']}'")
            
            random_unit = unit_filter[0]
            # Apply changes to person.xml
            # Class
            child.set("Jid", random_unit.Jid)
            # Level
            child.set("Level", random_unit.Level)
            child.set("InternalLevel", random_unit.InternalLevel)
            child.set("SkillPoint", random_unit.SkillPoint)

            for stat in stats:
                # Growth rates
                attribute_grow = f"Grow{stat}"
                child.set(f"Grow.{stat}", str(getattr(random_unit, attribute_grow)))
                for offset_type in offset_types:
                    # Bases
                    attribute_offset = f"Offset{offset_type}{stat}"
                    child.set(f"Offset{offset_type}.{stat}", str(getattr(random_unit, attribute_offset)))

            # Items
            child.set("Items", random_unit.Items)

        # Save the new person.xml
        new_person_path = f"{self.output_path}\\temp\\person_new.xml"
        tree.write(new_person_path, encoding="utf-8")

        # Read and extract the bundle file
        for obj in unity_env.objects:
            if obj.type.name == "TextAsset":
                # Replace the units in the xml
                person_data = obj.read()

                # Add the new person xml to the bundle
                with open(new_person_path, "rb") as new_person_xml:
                    person_data.script = new_person_xml.read()
                    person_data.save()
                    new_person_xml.close()
                
                # Save changes in the output path
                if not os.path.exists(person_output_path):
                    os.makedirs(person_output_path)
                with open(person_output_path + "\\person.xml.bundle", "wb") as new_person_bundle:
                    new_person_bundle.write(unity_env.file.save())
                    new_person_bundle.close()

    def delete_temp_files(self):
        shutil.rmtree(f"{self.output_path}\\temp", ignore_errors=True)

if __name__ == "__main__":
    print("Engage Randomizer")
    parser = argparse.ArgumentParser()

    parser.add_argument("-rec", "--recruitment", dest = "recruitment", default = None, help="Recruitment order (0 - Normal, 1 - Random, 2 - Reverse)", required=False)
    parser.add_argument("-c", "--class", dest = "job", default = None, help="Randomize classes (0 - Keep original class, 1 - Randomize class).", required=False)
    parser.add_argument("-b", "--bases", dest = "bases", default = None, help="Randomize bases (0 - Don't randomize, 1 - Randomize)", required=False)
    parser.add_argument("-sms", "--sms", dest = "swapStat", default = None, help="Swap offensive and defensive stats to match the new class (0 - Don't swap, 1 - Swap)", required=False)
    parser.add_argument("-i", "--input", dest = "input", default = None, help="Path to input to the romfs folder.", required=True)
    parser.add_argument("-o", "--output", dest = "output", default = None, help="Where to save the randomized files. Files in the input folder won't be modified.", required=True)

    args = parser.parse_args()

    recruitment_order = "Normal"
    if args.recruitment == "1":
        recruitment_order = "Random"
    elif args.recruitment == "2":
        recruitment_order = "Reversed"
    
    print("Recruitment order: ", recruitment_order)
    # print("Unit class: ", "Random" if args.job else "Original")
    print("Bases: ", "Random" if args.bases else "Original")
    print("Adjust stats: ", "Random" if args.swapStat else "Don't adjust")
    # print("input", args.input)
    # print("output", args.output)

    randomizer = Randomizer()
    randomizer.randomize(
        input_path = args.input, 
        output_path = args.output,
        recruitment = args.recruitment,
        bases = args.bases,
        swap_stat = args.swapStat
    )