// Packet self-check: node web/check.js (bytes below were accepted by the real watch)
const html = require('fs').readFileSync(__dirname + '/index.html', 'utf8');
const src = html.split('<script>')[1].split('</script>')[0];
const stub = { textContent:'', value:'', set onclick(f){}, set oninput(f){}, style:{} };
global.document = { getElementById: () => stub, querySelectorAll: () => [] };
global.navigator = {};
global.location = { search: "" };
eval(src.replace(/^updateBytes\(\);$/m, '') + `
  Date.now = () => 0x6aef76ad * 1000;
  const got = pages(1, 107, notice("Claude 🤖", "Hello from your laptop 👋🔥😎 it works! ✅", 2)).map(hex);
  const want = ["00 01 04 00 01 6b 00 00 46 00 ad 76 ef 6a 02 02 01 0b 43 6c",
    "01 61 75 64 65 20 f0 9f a4 96 02 31 48 65 6c 6c 6f 20 66 72",
    "02 6f 6d 20 79 6f 75 72 20 6c 61 70 74 6f 70 20 f0 9f 91 8b",
    "03 f0 9f 94 a5 f0 9f 98 8e 20 69 74 20 77 6f 72 6b 73 21 20",
    "04 e2 9c 85 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"];
  console.assert(JSON.stringify(got) === JSON.stringify(want), got);
  console.assert(hex(pages(3,2)[0]) === "00 01 00 00 03 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00");
  console.assert(hex(ackFrame(2,1)) === "00 01 00 01 04 02 00 00 01 00 01 00 00 00 00 00 00 00 00 00");
  let blocked = false; try { pages(1, 118) } catch { blocked = true }
  console.assert(blocked, "reset not blocked");
  console.log("all match");`);
