import PySimpleGUI as sg
from randomizer import Randomizer

# this is clobbering the print command, and replacing it with sg's Print()
# print = sg.Print

layout_settings = [
    [
        sg.Text("Recruitment order:"),
        sg.Radio('Normal', "settings_recruitment", key="option_recruitment_0", default=True),
        sg.Radio('Random', "settings_recruitment", key="option_recruitment_1"),
        sg.Radio('Reverse', "settings_recruitment", key="option_recruitment_2")
    ],
    [
        sg.Text("Randomize classes:"),
        sg.Radio("Don't randomize", "settings_class", key="option_class_0", default=True),
        sg.Radio('Randomize', "settings_class", key="option_class_1"),
    ],
    [
        sg.Text("Randomize bases:"),
        sg.Radio("Don't randomize", "settings_bases", key="option_bases_0", default=True),
        sg.Radio('Randomize', "settings_bases", key="option_bases_1"),
    ],
    [
        sg.Text("Swap Str/Mag and Def/Res:", tooltip="Swap offensive and defensive stats to match the new class"),
        sg.Radio("Don't swap", "settings_swap", key="option_swap_0", default=True),
        sg.Radio('Swap', "settings_swap", key="option_swap_1"),
    ],

]

layout = [
    [
        sg.Text("Romfs path"),
        sg.In(size=(25, 1), enable_events=True, disabled=False, key="path_romfs"),
        sg.FolderBrowse()
    ], 
    [
        sg.Text("Output path"),
        sg.In(size=(25, 1), enable_events=True, disabled=True, key="path_output"),
        sg.FolderBrowse()
    ],
    layout_settings,
    [sg.Text('Log:', visible=False, key="log_title")],
    [sg.Output(size=(50,10), visible=False, key='log_text')], 
    [
        sg.Button("Randomize", disabled=True, key="btn_randomize")
    ]
]


window = sg.Window(title="Engage Randomizer", layout=[layout], icon='Images/icon.ico')

def get_setting(values, setting, amount):
    setting_value = 0
    for index in range(0, amount):    
        setting_key = f"{setting}{index}"
        if values[setting_key]:
            setting_value = index
            break
    return setting_value

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

    if values["path_romfs"] and values["path_output"]:
        isDisabled = values["path_romfs"] == values["path_output"]
        window["btn_randomize"].update(disabled=isDisabled)

    if event == "btn_randomize":
        window["log_title"].update(visible=True)
        window['log_text'].update(visible=True)
        setting_recruitment = get_setting(values, "option_recruitment_", 3)
        setting_class = get_setting(values, "option_class_", 2)
        setting_bases = get_setting(values, "option_bases_", 2)
        setting_swap = get_setting(values, "option_swap_", 2)

        randomizer = Randomizer()
        randomizer.randomize(
            input_path = values["path_romfs"], 
            output_path = values["path_output"],
            recruitment = setting_recruitment,
            bases = setting_bases,
            unit_job = setting_class,
            swap_stat = setting_swap
        )