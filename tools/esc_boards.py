def get_esc_board_description(hardware_version):
    hardware_name = 'Unknown Board'
    if hardware_version == 30:
        hardware_name = 'ModalAi 4-in-1 ESC V2 RevA'
    elif hardware_version == 31:
        hardware_name = 'ModalAi 4-in-1 ESC V2 RevB'

    return hardware_name
