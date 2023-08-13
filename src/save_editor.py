from fsm import *


def main():
    save_state = None
    try:
        next_state = state_start()
        while True:
            match next_state:
                case STATES.OPTIONS_START:
                    previous_state = STATES.OPTIONS_START
                    next_state = state_start(False)
                case STATES.OPTIONS_EDIT_START:
                    previous_state = STATES.OPTIONS_START
                    next_state = state_options_edit_start(previous_state)
                case STATES.OPTIONS_EDIT_AUTO_DISCOVER_SAVES:
                    previous_state = STATES.OPTIONS_EDIT_START
                    save_path = state_auto_discover_saves()
                    save_state = SaveState(save_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Save state loaded.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_MANUAL_SAVE:
                    previous_state = STATES.OPTIONS_EDIT_START
                    save_path = state_manual_save()
                    save_state = SaveState(save_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Save state loaded.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_RESTORE:
                    previous_state = STATES.OPTIONS_START
                    next_state = state_options_restore(previous_state)
                case STATES.OPTIONS_RESTORE_AUTO_DISCOVER_BACKUPS:
                    previous_state = STATES.OPTIONS_RESTORE
                    backup_path = state_auto_discover_backups()
                    restore_save(backup_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Backup was restored.")
                    next_state = STATES.OPTIONS_START
                case STATES.OPTIONS_RESTORE_MANUAL_BACKUP:
                    previous_state = STATES.OPTIONS_RESTORE
                    backup_path = state_manual_backup()
                    restore_save(backup_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Backup was restored.")
                    next_state = STATES.OPTIONS_START
                case STATES.OPTIONS_EDIT:
                    previous_state = STATES.OPTIONS_EDIT_START
                    next_state = state_options_edit(previous_state)
                    if next_state == previous_state:
                        save_state.rollback()
                        del save_state
                case STATES.OPTIONS_EDIT_DOORS:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_doors(save_state)
                    save_state.set_door(key, value)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Door state set.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_TIME:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_time(save_state)
                    save_state.set_time(key, value)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Time value set.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_RESOURCE:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_resource(save_state)
                    save_state.set_resource(key, value)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Resource value set.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_THOUGHTS:
                    previous_state = STATES.OPTIONS_EDIT
                    if state_edit_thoughts():
                        save_state.set_all_unknown_and_forgotten_thoughts()
                        print(
                            Fore.GREEN
                            + "[+]"
                            + Fore.RESET
                            + " All unknown and forgotten thought states set."
                        )
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_CHAR_SHEET:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_char_sheet(save_state)
                    save_state.set_char_sheet_stat(key, value)
                    print(
                        Fore.GREEN + "[+]" + Fore.RESET + " Character sheet stat set."
                    )
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_ROLLBACK:
                    previous_state = STATES.OPTIONS_EDIT
                    save_state.rollback()
                    print(Fore.GREEN + "[+]" + Fore.RESET + " All changes rolled back.")
                    next_state = STATES.OPTIONS_START
                case STATES.OPTIONS_EDIT_COMMIT:
                    previous_state = STATES.OPTIONS_EDIT
                    save_state.commit()
                    print(
                        Fore.GREEN
                        + "[+]"
                        + Fore.RESET
                        + " All changes committed to disk."
                    )
                    next_state = STATES.OPTIONS_START
    except (KeyboardInterrupt, Exception):
        if save_state is not None:
            save_state.rollback()
        raise


if __name__ == "__main__":
    main()
