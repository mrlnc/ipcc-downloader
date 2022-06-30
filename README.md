# iOS Carrier Profiles (IPCC)

Carrier Profiles configure your iOS smartphone for mobile networks. They control e.g. availability of VoLTE, Cell Broadcasts, and so on.

* **Carrier Bundles** configure the iPhone for specific networks.
* **Country Bundles** apply for a whole country, e.g., for common configuration for EU-ALERT Cell Broadcasts.

Apple distributes the iOS carrier profiles on behalf of the carriers:

* the *iOS system image* includes most profiles, with updates through the usual iOS system update progress.
* some are pulled from `itunes.com`

I built a little download script to fetch those profiles available online at `itunes.com`.

# Download IPCCs from `itunes.com`

Download and unzip all files (thousands, might take some time) to `data/`:
```
./download_ipccs.py -d
```

Convert all `plist` files to XML:
```
for i in $(find . | grep plist); do plistutil -i $i -o $i.xml; done
```

# IPCC walkthrough

(just my notes on carrier profiles, might be wrong :-))

## IPCC files

* IPCC itself is a ZIP archive; simply use `unzip` to extract

Contents (example):
```
.
└── Payload
    └── CARRIER.bundle
        ├── carrier.plist
        ├── carrier.pri
        ├── carrier.prl
        ├── ERI.plist
        ├── Info.plist
        ├── version.plist
```

* `plist` files can be converted to XML with `plistutil`, or directly use the `plistlib` module in Python
* `prl` means "Preferred Roaming List"
* `pri` seems to configure baseband parameters

## Download Specific IPCC

If you're looking for a specific carrier, download the index here:

```
wget https://itunes.com/version
```

Then use your favorite editor and search for either carrier name or MCCMNC:
```xml
<key>26201</key>
<dict>
  <key>BundleName</key>
  <string>TMobile_Germany</string>
</dict>
```

Search for the bundle:
```xml
<key>TMobile_Germany</key>
		<dict>
			<key>12.2</key>
			<dict>
				<key>BuildVersion</key>
				<string>36.1</string>
				<key>BundleURL</key>
				<string>https://updates.cdn-apple.com/2019/carrierbundles/041-45476-2019325-3E5B6D80-4A7F-11E9-A857-5B76600891CB/TMobile_Germany_iPhone.ipcc</string>
				<key>Digest</key>
				<data>
				4X/b60btXMxdPAF9xnC4xB+75rU=
				</data>
			</dict>
```

So a three year old bundle is the most current here. I'm not sure if they rarely change or IPCCs are just not the main mechanism anymore. But you can go and download that IPCC now:

```
wget https://updates.cdn-apple.com/2019/carrierbundles/041-45476-2019325-3E5B6D80-4A7F-11E9-A857-5B76600891CB/TMobile_Germany_iPhone.ipcc
```

The resulting file is a ZIP that you can extract:
```
$ file TMobile_Germany_iPhone.ipcc 
TMobile_Germany_iPhone.ipcc: Zip archive data, at least v1.0 to extract
$ unzip TMobile_Germany_iPhone.ipcc
Archive:  TMobile_Germany_iPhone.ipcc
   creating: Payload/
   creating: Payload/TMobile_Germany.bundle/
  inflating: Payload/TMobile_Germany.bundle/carrier.plist  
  inflating: Payload/TMobile_Germany.bundle/Info.plist
  …
```

The `plist` files are binary-packed and can be extracted with `plistutil`

```
$ sudo apt install libplist-utils
$ plistutil -i Payload/TMobile_Germany.bundle/carrier.plist
$ plistutil -i Payload/TMobile_Germany.bundle/carrier.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>OTASoftwareUpdate</key>
        <dict>
                <key>MaxBytesOverCellular</key>
                <integer>62914560</integer>
        </dict>
        <key>StockSymboli</key>
```
