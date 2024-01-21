import os

from controller import Controller

if __name__ == "__main__":
    controller = Controller(
        open_msx_path=os.environ["OPENMSX_PATH"],
        macros={
            "switch on": [
                "machine Sanyo_PHC-70FD",
                # "machine Sanyo_PHC-23JB",
                # "ext AVT_DPF-550",
                "set renderer SDL",
                "set power on",
            ],
            "reload": [
                "toggle power",
                "diska eject",
                "toggle power",
                "debug set_watchpoint -once write_mem 0xfffe {[debug read \"memory\" 0xfffe] == 0} {diska insert $disk}",
                "type_via_keybuf \\r\\r",
                "type_via_keybuf poke-2,0\\r",
                "type_via_keybuf cls\\r",
                "type_via_keybuf run\"$file\"\\r"
            ]
        },
        variables={
            "disk": "msxDisk",
            "file": "GAME.BAS"
        }
    )
    controller.interact()
    controller.terminate()
