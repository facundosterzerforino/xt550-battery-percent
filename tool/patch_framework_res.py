#!/usr/bin/env python
"""Builds a framework-res.apk whose status bar battery icon shows the exact
percentage (1 % steps), from the phone's own stock framework-res.apk.

Only 13 entries change; AndroidManifest.xml, META-INF (signature) and
resources.arsc stay byte-identical. On Android 2.x, PackageManager only checks
the signature of AndroidManifest.xml for system packages, so the file is
accepted.

usage: patch_framework_res.py <stock framework-res.apk> <out.apk> <jdk> <build-tools>
"""
import hashlib, pathlib, shutil, subprocess, sys, tempfile, zipfile

STOCK_SHA256 = '670bd9f0d43bc6eea72110d4f6667dc639d5345b774f3c59d9d0da6e0f9ead9b'  # Motorola XT550, 2.3.6
HERE = pathlib.Path(__file__).resolve().parent


def main():
    stock, out, jdk, bt = (pathlib.Path(a) for a in sys.argv[1:5])
    sfx = '.exe' if sys.platform == 'win32' else ''
    if hashlib.sha256(stock.read_bytes()).hexdigest() != STOCK_SHA256:
        print('warning: not the XT550 file this was tested on; check the battery drawables first')
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        run = lambda *c: subprocess.run([str(x) for x in c], check=True)
        run(jdk / 'bin' / ('javac' + sfx), '-d', tmp / 'cls', HERE / 'MakeDigits.java')
        run(jdk / 'bin' / ('java' + sfx), '-Djava.awt.headless=true', '-cp', tmp / 'cls', 'MakeDigits', tmp / 'digits')
        (tmp / 'x' / 'res').mkdir(parents=True)
        run(sys.executable, HERE / 'make_xml.py', tmp / 'x' / 'res', '@*android:drawable/')
        (tmp / 'x' / 'AndroidManifest.xml').write_text(
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.xt550.batteryxml" />\n')
        run(bt / ('aapt' + sfx), 'package', '-f', '-M', tmp / 'x' / 'AndroidManifest.xml', '-S', tmp / 'x' / 'res',
            '-I', stock, '-F', tmp / 'xml.apk')

        new = {'res/drawable-mdpi/' + p.name: p.read_bytes() for p in (tmp / 'digits').glob('*.png')}
        with zipfile.ZipFile(tmp / 'xml.apk') as x:
            for n in ('stat_sys_battery.xml', 'stat_sys_battery_charge.xml', 'stat_sys_battery_charge_1.xml'):
                new['res/drawable/' + n] = x.read('res/drawable/' + n)
        src = zipfile.ZipFile(stock)
        missing = [k for k in new if k not in src.namelist()]
        if missing:
            raise SystemExit('stock file lacks %s' % missing)
        with zipfile.ZipFile(tmp / 'unaligned.apk', 'w') as z:
            for i in src.infolist():
                zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
                zi.compress_type, zi.external_attr, zi.create_system = i.compress_type, i.external_attr, i.create_system
                z.writestr(zi, new.get(i.filename) or src.read(i))
        run(bt / ('zipalign' + sfx), '-f', '4', tmp / 'unaligned.apk', out)
        with zipfile.ZipFile(out) as a:
            for n in ['AndroidManifest.xml', 'resources.arsc'] + [n for n in src.namelist() if n.startswith('META-INF')]:
                assert a.read(n) == src.read(n), n
        print(out, hashlib.sha256(out.read_bytes()).hexdigest())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
