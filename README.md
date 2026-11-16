# Battery percentage in the status bar for Motorola XT550 (Android 2.3.6)

Changes the stock status bar battery icon so it shows the exact number (0–100,
in 1 % steps), both on battery and while charging. It replaces a separate app
(BatteryBot) that added a second icon on the left of the status bar.

![levels](docs/levels.png)

## How

The phone's `framework-res.apk` has one battery picture per 5 %
(`stat_sys_battery_0.png` … `_100.png`). It also has the level-lists
`stat_sys_battery.xml`, `stat_sys_battery_charge.xml` and
`stat_sys_battery_charge_1.xml` (the XT550 uses `_charge_1` while charging on
USB). Adding resources would mean rebuilding `resources.arsc`, so the existing
entries are reused:

- `stat_sys_battery_0, _10, …, _100`: kept as they are, used as the battery body
  (10 % steps).
- `stat_sys_battery_5, _15, …, _95`: replaced by the digits 0–9, drawn in white
  with a dark outline in a 5×9 pixel font (`tool/MakeDigits.java`).
- The three level-lists are rewritten (`tool/make_xml.py`) with 101 items. Each
  item is a `layer-list` of:
  - the body (or, while charging, the stock charging animation with its own
    frames and timings);
  - one `<bitmap gravity="top|left">` per digit, placed with insets.

`tool/patch_framework_res.py` takes the phone's own file and outputs the
patched one. Only those 13 entries change. `AndroidManifest.xml`, `META-INF/`
(the signature) and `resources.arsc` stay byte-identical, which the script
checks.

### Why the phone accepts the file

On Android 2.3, for packages on the system partition, `PackageParser.collectCertificates`
only verifies `AndroidManifest.xml` (gingerbread `PackageParser.java`, the
`PARSE_IS_SYSTEM` branch). At boot the log shows
`framework-res.apk changed; collecting certs` and no error. This does **not**
hold on newer Android versions.

## Files

- Stock file (XT550, 2.3.6): SHA256 `670bd9f0d43bc6eea72110d4f6667dc639d5345b774f3c59d9d0da6e0f9ead9b`
- Patched file made by the script from it: SHA256 `70d8fe0730627ea8a61a7bceedca65c5c8f8e9d183e7adca82491768ea9555c2`

No Motorola file is in this repository; the script patches your own copy.

```
adb pull /system/framework/framework-res.apk stock.apk
python tool/patch_framework_res.py stock.apk framework-res.apk <jdk> <android build-tools>
```

## Install (root)

Keep a copy of the stock file on the phone **before** you install. adb + `su`
(for the shell user) keep working even if the phone does not finish booting,
so you can always put the stock file back.

```
mount -o remount,rw -t yaffs2 /dev/block/mtdblock11 /system
cp framework-res.apk /system/framework/framework-res.apk.new
chown 0.0 /system/framework/framework-res.apk.new; chmod 644 /system/framework/framework-res.apk.new
mv /system/framework/framework-res.apk.new /system/framework/framework-res.apk   # rename, do not overwrite in place
sync
```

Then restart the phone. To undo, do the same with the stock file.

## Tested

- All 303 drawables (101 levels × 3 level-lists) were rendered on the phone
  with its own drawable code, in a test app: `docs/levels.png`.
- Installed on the XT550: it boots normally, and the icon shows the number on
  the right of the status bar.
- Note: while charging near full, Motorola's BatteryService reports 100 (the
  kernel says 98). The icon shows what the system reports.

License: MIT for the scripts (`tool/`).
