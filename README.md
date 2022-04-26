# Inspect iOS Carrier Profiles (IPCC)

Carrier Profiles configure your smartphone for mobile networks. I'm not sure if Carrier Profiles are just a legacy or are actually required nowadays, since all configuration should be done through the mobile network itself.

You'll find things in there like:
* enable VoLTE for specific carriers
* disable some bands (makes sense if your carrier isn't transmitting there)
* …

Download the *index* here:
```
wget http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/com.apple.jingle.appserver.client.MZITunesClientCheck/version -I ipcc_index.xml
```

## Download Specific IPCC

If you're looking for a specific carrier, just use your favorite editor and search for either carrier name or MCCMNC:
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

# Download all IPCCs

Download the *index* here:
```
wget http://ax.phobos.apple.com.edgesuite.net/WebObjects/MZStore.woa/wa/com.apple.jingle.appserver.client.MZITunesClientCheck/version -I ipcc_index.xml
```

Extract all URLs to `data/ipcc_urls.txt`:
```
./download_ipccs.py -i IPCC_index.xml 
```

Download all files (thousands, might take some time):
```
./download_ipccs.py -i IPCC_index.xml -d
```

Unzip all bundles:
```
$ cd data
$ for i in $(ls *.ipcc); do unzip $i -d $i-dir; done
```

Convert all `plist` files:
```
for i in $(find . | grep plist); do plistutil -i $i -o $i.xml; done
```