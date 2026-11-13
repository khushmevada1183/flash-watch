const fs = require('fs');
const path = require('path');

const targetFile = path.join(__dirname, '..', 'node_modules', '@capacitor-community', 'bluetooth-le', 'ios', 'Plugin', 'Conversion.swift');

if (!fs.existsSync(targetFile)) {
  console.log('[patch-plugin] Target file does not exist yet:', targetFile);
  process.exit(0);
}

let content = fs.readFileSync(targetFile, 'utf8');

const buggyFunction = `func stringToData(_ dataString: String) -> Data {
    let hexValues = dataString.split(separator: " ")
    var data = Data(capacity: hexValues.count)
    for hex in hexValues {
        data.append(UInt8(hex, radix: 16)!)
    }
    return data
}`;

const safeFunction = `func stringToData(_ dataString: String) -> Data {
    let clean = dataString.trimmingCharacters(in: .whitespacesAndNewlines)
    let hexValues: [Substring]
    if clean.contains(" ") {
        hexValues = clean.split(separator: " ")
    } else {
        var chunks = [Substring]()
        var start = clean.startIndex
        while start < clean.endIndex {
            let end = clean.index(start, offsetBy: 2, limitedBy: clean.endIndex) ?? clean.endIndex
            chunks.append(clean[start..<end])
            start = end
        }
        hexValues = chunks
    }
    var data = Data(capacity: hexValues.count)
    for hex in hexValues {
        if let byte = UInt8(hex, radix: 16) {
            data.append(byte)
        }
    }
    return data
}`;

if (content.includes(buggyFunction)) {
  content = content.replace(buggyFunction, safeFunction);
  fs.writeFileSync(targetFile, content, 'utf8');
  console.log('[patch-plugin] Successfully patched Conversion.swift for crash resilience!');
} else if (content.includes('trimmingCharacters')) {
  console.log('[patch-plugin] Conversion.swift is already patched.');
} else {
  console.warn('[patch-plugin] Could not locate exact buggy function in Conversion.swift to patch.');
}

// Ensure HealthKitPlugin is included in packageClassList if ios config exists
const iosConfigFile = path.join(__dirname, '..', 'ios', 'App', 'App', 'capacitor.config.json');
if (fs.existsSync(iosConfigFile)) {
  try {
    const config = JSON.parse(fs.readFileSync(iosConfigFile, 'utf8'));
    if (!Array.isArray(config.packageClassList)) {
      config.packageClassList = [];
    }
    if (!config.packageClassList.includes('HealthKitPlugin')) {
      config.packageClassList.push('HealthKitPlugin');
      fs.writeFileSync(iosConfigFile, JSON.stringify(config, null, '\t'), 'utf8');
      console.log('[patch-plugin] Registered HealthKitPlugin in ios/App/App/capacitor.config.json');
    }
  } catch (err) {
    console.warn('[patch-plugin] Could not update ios capacitor.config.json:', err.message);
  }
}
