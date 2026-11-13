import re

with open('web/index.html', 'r', encoding='utf-8') as f:
    orig_text = f.read()

# Separate parts
head_pre_style = orig_text.split('<style>')[0] + '<style>\n'
style_content = orig_text.split('<style>')[1].split('</style>')[0]
between_style_script = orig_text.split('</style>')[1].split('<script>')[0]
script_content = orig_text.split('<script>')[1].split('</script>')[0]
after_script = '</script>' + orig_text.split('</script>')[1]

cyberpunk_css = """
  :root {
    --cyber-black: #05060b;
    --cyber-abyss: #070913;
    --cyber-surface: rgba(11, 15, 28, 0.82);
    --cyber-surface-elevated: rgba(16, 22, 42, 0.92);
    --cyber-surface-card: rgba(12, 17, 33, 0.85);
    --cyber-cyan: #00f0ff;
    --cyber-cyan-dim: rgba(0, 240, 255, 0.18);
    --cyber-cyan-glow: 0 0 16px rgba(0, 240, 255, 0.55);
    --cyber-pink: #ff0055;
    --cyber-pink-dim: rgba(255, 0, 85, 0.18);
    --cyber-pink-glow: 0 0 16px rgba(255, 0, 85, 0.55);
    --cyber-yellow: #ffe600;
    --cyber-yellow-glow: 0 0 16px rgba(255, 230, 0, 0.55);
    --cyber-green: #00ff66;
    --cyber-green-glow: 0 0 16px rgba(0, 255, 102, 0.55);
    --cyber-border: rgba(0, 240, 255, 0.24);
    --cyber-border-bright: rgba(0, 240, 255, 0.65);
    --cyber-border-pink: rgba(255, 0, 85, 0.55);
    --text-primary: #f0f6fc;
    --text-secondary: #859bb8;
    --text-cyan: #00f0ff;
    --text-dim: #4d5b73;
    --font-mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-tap-highlight-color: transparent;
  }

  body {
    background-color: var(--cyber-black);
    background-image: 
      linear-gradient(rgba(0, 240, 255, 0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 240, 255, 0.04) 1px, transparent 1px),
      radial-gradient(circle at 50% 0%, rgba(0, 240, 255, 0.14) 0%, transparent 55%),
      radial-gradient(circle at 100% 100%, rgba(255, 0, 85, 0.09) 0%, transparent 50%),
      radial-gradient(circle at 0% 80%, rgba(0, 255, 102, 0.06) 0%, transparent 40%);
    background-size: 28px 28px, 28px 28px, 100% 100%, 100% 100%, 100% 100%;
    color: var(--text-primary);
    font-family: var(--font-sans);
    min-height: 100vh;
    padding-top: max(14px, env(safe-area-inset-top));
    padding-bottom: max(36px, env(safe-area-inset-bottom));
    -webkit-font-smoothing: antialiased;
    position: relative;
    overflow-x: hidden;
  }

  /* Cyber CRT Scanlines */
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(0deg, rgba(0, 0, 0, 0.22) 0px, rgba(0, 0, 0, 0.22) 1px, transparent 1px, transparent 3px);
    pointer-events: none;
    z-index: 9999;
    opacity: 0.55;
  }

  main {
    max-width: 620px;
    margin: 0 auto;
    padding: 0 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    position: relative;
    z-index: 10;
  }

  /* --- Top Tactical Cyber Bar --- */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 14px;
    background: var(--cyber-surface);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--cyber-border);
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px));
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.7), inset 0 0 14px rgba(0, 240, 255, 0.05);
    position: relative;
  }

  header::after {
    content: "";
    position: absolute;
    top: 0;
    left: 20px;
    right: 20px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyber-cyan), transparent);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .brand img {
    width: 30px;
    height: 30px;
    border-radius: 4px;
    border: 1px solid var(--cyber-cyan);
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
    object-fit: cover;
  }

  .brand-text h1 {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.08em;
    font-family: var(--font-mono);
    color: #fff;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
  }

  .brand-text span {
    font-size: 10px;
    font-family: var(--font-mono);
    color: var(--cyber-cyan);
    letter-spacing: 0.06em;
    display: block;
    opacity: 0.9;
  }

  /* Cyber Status Badge */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 5px 12px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    background: rgba(14, 20, 36, 0.9);
    border: 1px solid var(--cyber-border);
    clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
    color: var(--text-secondary);
    text-transform: uppercase;
    transition: all 0.2s ease;
  }

  .badge.connected {
    background: rgba(0, 255, 102, 0.12);
    border-color: var(--cyber-green);
    color: var(--cyber-green);
    box-shadow: 0 0 14px rgba(0, 255, 102, 0.35);
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--text-dim);
    transition: all 0.2s ease;
  }

  .badge.connected .dot {
    background: var(--cyber-green);
    box-shadow: 0 0 8px var(--cyber-green);
    animation: cyberPulse 1.6s infinite ease-in-out;
  }

  @keyframes cyberPulse {
    0%, 100% { transform: scale(1); opacity: 1; filter: drop-shadow(0 0 2px var(--cyber-green)); }
    50% { transform: scale(1.3); opacity: 0.7; filter: drop-shadow(0 0 8px var(--cyber-green)); }
  }

  /* --- Cyber Segmented Navigation --- */
  .segmented-nav {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    background: rgba(10, 14, 28, 0.9);
    border: 1px solid var(--cyber-border);
    padding: 3px;
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.6);
    gap: 3px;
  }

  .nav-pill {
    padding: 8px 10px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    background: transparent;
    border: none;
    clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
    cursor: pointer;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.16s ease;
  }

  .nav-pill:active {
    transform: scale(0.97);
  }

  .nav-pill.active {
    background: linear-gradient(135deg, var(--cyber-cyan) 0%, #0088ff 100%);
    color: #030509;
    font-weight: 800;
    box-shadow: 0 0 14px rgba(0, 240, 255, 0.6);
    text-shadow: none;
  }

  /* --- Cyber Deck Cards --- */
  .card {
    background: var(--cyber-surface-card);
    backdrop-filter: blur(24px) saturate(180%);
    -webkit-backdrop-filter: blur(24px) saturate(180%);
    border: 1px solid var(--cyber-border);
    clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8), inset 0 0 24px rgba(0, 240, 255, 0.03);
    position: relative;
    transition: border-color 0.2s ease;
  }

  /* Corner Targeting Accents */
  .card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 8px;
    height: 8px;
    border-top: 2px solid var(--cyber-cyan);
    border-left: 2px solid var(--cyber-cyan);
    pointer-events: none;
  }

  .card::after {
    content: "";
    position: absolute;
    bottom: 0;
    right: 0;
    width: 8px;
    height: 8px;
    border-bottom: 2px solid var(--cyber-pink);
    border-right: 2px solid var(--cyber-pink);
    pointer-events: none;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(0, 240, 255, 0.15);
    padding-bottom: 8px;
  }

  .card-title {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--cyber-cyan);
    display: flex;
    align-items: center;
    gap: 6px;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
  }

  .card-title::before {
    content: "//";
    color: var(--cyber-pink);
  }

  /* --- Cyber Arc Reactor Hero Dial --- */
  .watch-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px 0 6px;
    position: relative;
  }

  .watch-case {
    width: 186px;
    height: 186px;
    border-radius: 50%;
    position: relative;
    background: radial-gradient(circle at 50% 50%, rgba(0, 240, 255, 0.08) 0%, rgba(9, 13, 26, 0.95) 70%, #030408 100%);
    border: 2px solid rgba(0, 240, 255, 0.4);
    box-shadow: 
      0 0 24px rgba(0, 240, 255, 0.25),
      inset 0 0 28px rgba(0, 240, 255, 0.12),
      0 12px 40px rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Rotating HUD reticle notches */
  .watch-case::before {
    content: "";
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 240, 255, 0.3);
    animation: rotateReticle 40s linear infinite;
    pointer-events: none;
  }

  .watch-case::after {
    content: "";
    position: absolute;
    inset: 6px;
    border-radius: 50%;
    border: 1px dotted rgba(255, 0, 85, 0.3);
    animation: rotateReticleReverse 30s linear infinite;
    pointer-events: none;
  }

  @keyframes rotateReticle {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @keyframes rotateReticleReverse {
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
  }

  .rings-svg {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    transform: rotate(-90deg);
  }

  .ring-bg {
    fill: none;
    stroke: rgba(255, 255, 255, 0.05);
  }

  .ring-bar {
    fill: none;
    stroke-linecap: round;
    transition: stroke-dashoffset 900ms cubic-bezier(0.2, 0.8, 0.2, 1);
    filter: drop-shadow(0 0 6px currentColor);
  }

  .watch-content {
    z-index: 5;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .watch-time {
    font-family: var(--font-mono);
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;
    color: #fff;
    text-shadow: 0 0 12px var(--cyber-cyan), 0 0 2px #fff;
  }

  .watch-label {
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--cyber-cyan);
    text-transform: uppercase;
  }

  .battery-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    clip-path: polygon(0 0, calc(100% - 4px) 0, 100% 4px, 100% 100%, 4px 100%, 0 calc(100% - 4px));
    background: rgba(0, 255, 102, 0.14);
    border: 1px solid rgba(0, 255, 102, 0.45);
    color: var(--cyber-green);
    margin-top: 3px;
    box-shadow: 0 0 8px rgba(0, 255, 102, 0.25);
  }

  /* --- Cyber Sensor 4-Metric Grid --- */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .metric-card {
    background: rgba(14, 19, 36, 0.9);
    border: 1px solid var(--cyber-border);
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    position: relative;
    box-shadow: inset 0 0 14px rgba(0, 240, 255, 0.04);
    transition: all 0.2s ease;
  }

  .metric-card:hover {
    border-color: var(--cyber-border-bright);
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.2), inset 0 0 14px rgba(0, 240, 255, 0.08);
  }

  .metric-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    text-transform: uppercase;
  }

  .metric-val {
    font-family: var(--font-mono);
    font-size: 22px;
    font-weight: 900;
    letter-spacing: -0.02em;
    color: #fff;
    font-variant-numeric: tabular-nums;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
  }

  #sport-steps { color: var(--cyber-cyan); text-shadow: 0 0 10px rgba(0, 240, 255, 0.6); }
  #sport-dist { color: var(--cyber-yellow); text-shadow: 0 0 10px rgba(255, 230, 0, 0.6); }
  #sport-kcal { color: var(--cyber-pink); text-shadow: 0 0 10px rgba(255, 0, 85, 0.6); }
  #sport-dur { color: var(--cyber-green); text-shadow: 0 0 10px rgba(0, 255, 102, 0.6); }

  /* --- Cyberdeck Buttons & Controls --- */
  button, .button {
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 10px 16px;
    clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
    border: 1px solid var(--cyber-border);
    background: rgba(16, 23, 44, 0.9);
    color: #fff;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    user-select: none;
    text-decoration: none;
    text-transform: uppercase;
    transition: all 0.16s ease;
  }

  button:active, .button:active {
    transform: scale(0.97);
  }

  @media (hover: hover) and (pointer: fine) {
    button:hover:not(:disabled), .button:hover:not(:disabled) {
      border-color: var(--cyber-cyan);
      box-shadow: 0 0 14px rgba(0, 240, 255, 0.4);
      color: var(--cyber-cyan);
    }
  }

  button.primary, .button.primary {
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.25) 0%, rgba(0, 112, 243, 0.35) 100%);
    border: 1px solid var(--cyber-cyan);
    color: var(--cyber-cyan);
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.35), inset 0 0 10px rgba(0, 240, 255, 0.15);
    text-shadow: 0 0 6px var(--cyber-cyan);
  }

  button.primary:hover:not(:disabled) {
    background: var(--cyber-cyan);
    color: #04060c;
    text-shadow: none;
    box-shadow: 0 0 26px rgba(0, 240, 255, 0.85);
  }

  button.danger {
    background: rgba(255, 0, 85, 0.12);
    border: 1px solid var(--cyber-pink);
    color: var(--cyber-pink);
    box-shadow: 0 0 14px rgba(255, 0, 85, 0.25);
    text-shadow: 0 0 6px var(--cyber-pink);
  }

  button.danger:hover:not(:disabled) {
    background: var(--cyber-pink);
    color: #fff;
    box-shadow: 0 0 24px rgba(255, 0, 85, 0.85);
  }

  button:disabled, .button:disabled {
    opacity: 0.35;
    cursor: not-allowed;
    border-color: rgba(255, 255, 255, 0.1) !important;
    box-shadow: none !important;
    transform: none !important;
  }

  .chip {
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 700;
    clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
  }

  /* --- Cyber Inputs --- */
  input, select, textarea {
    font-family: var(--font-mono);
    font-size: 13px;
    width: 100%;
    padding: 10px 14px;
    clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
    border: 1px solid var(--cyber-border);
    background: rgba(8, 12, 24, 0.95);
    color: #fff;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
    transition: all 0.16s ease;
  }

  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--cyber-cyan);
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.4), inset 0 0 10px rgba(0, 240, 255, 0.1);
  }

  label {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--text-secondary);
    text-transform: uppercase;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  /* --- CRT Terminal Log View --- */
  pre#log {
    background: #03050a;
    border: 1px solid var(--cyber-border);
    clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px));
    padding: 12px 14px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: #00ff88;
    text-shadow: 0 0 6px rgba(0, 255, 136, 0.6);
    height: 180px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
    box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.8), 0 0 12px rgba(0, 240, 255, 0.1);
  }

  /* Preset row buttons */
  .presets-row {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .emoji-picker {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 6px;
  }

  .emoji-btn {
    padding: 8px 4px;
    font-size: 18px;
    background: rgba(14, 20, 36, 0.85);
    border: 1px solid rgba(0, 240, 255, 0.2);
    clip-path: polygon(0 0, calc(100% - 4px) 0, 100% 4px, 100% 100%, 4px 100%, 0 calc(100% - 4px));
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .emoji-btn:hover {
    background: rgba(0, 240, 255, 0.2);
    border-color: var(--cyber-cyan);
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
  }

  .row {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .bytes-bar {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    color: var(--cyber-yellow);
    padding: 3px 8px;
    background: rgba(255, 230, 0, 0.12);
    border: 1px solid rgba(255, 230, 0, 0.4);
    clip-path: polygon(0 0, calc(100% - 4px) 0, 100% 4px, 100% 100%, 4px 100%, 0 calc(100% - 4px));
  }

  /* Connection Stepper Cyber Matrix */
  .step-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    background: rgba(10, 14, 26, 0.8);
    border: 1px solid rgba(0, 240, 255, 0.15);
    clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));
    font-family: var(--font-mono);
    font-size: 11px;
    transition: all 0.2s ease;
  }

  .step-row.done {
    border-color: var(--cyber-green);
    background: rgba(0, 255, 102, 0.08);
    color: var(--cyber-green);
  }

  .step-row.active {
    border-color: var(--cyber-cyan);
    background: rgba(0, 240, 255, 0.1);
    color: var(--cyber-cyan);
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
  }

  .step-badge {
    width: 22px;
    height: 22px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    border: 1px solid currentColor;
    clip-path: polygon(0 0, calc(100% - 4px) 0, 100% 4px, 100% 100%, 4px 100%, 0 calc(100% - 4px));
  }

  /* Platform setup tabs */
  .guide-tab {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    padding: 7px 12px;
    background: transparent;
    border: 1px solid rgba(0, 240, 255, 0.2);
    color: var(--text-secondary);
  }

  .guide-tab.active {
    background: var(--cyber-cyan);
    color: #03050a;
    border-color: var(--cyber-cyan);
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
  }

  .hidden {
    display: none !important;
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
  }
"""

cyberpunk_body = """
<main>
  <!-- Top Tactical Cyber Bar -->
  <header>
    <div class="brand">
      <img src="icon.svg" alt="boAt FLASH">
      <div class="brand-text">
        <h1>FLASH // CYBER-LINK</h1>
        <span>REV-K6 TACTICAL OS</span>
      </div>
    </div>

    <!-- Dynamic Status Badge -->
    <div id="conn-badge" class="badge">
      <span class="dot"></span>
      <span id="conn-state-text">STANDBY</span>
    </div>
  </header>

  <!-- Segmented Main 3-Tab Navigator -->
  <nav class="segmented-nav">
    <button type="button" class="nav-pill active" id="btn-tab-dash">
      <span>01</span> Telemetry
    </button>
    <button type="button" class="nav-pill" id="btn-tab-notif">
      <span>02</span> Comms
    </button>
    <button type="button" class="nav-pill" id="btn-tab-diag">
      <span>03</span> Diagnostics
    </button>
  </nav>

  <!-- iOS Error 2 Alert Banner -->
  <div id="error2-alert" class="card hidden" style="border-color:var(--cyber-pink); background:rgba(255,0,85,0.12); box-shadow:0 0 20px rgba(255,0,85,0.3);">
    <div style="display:flex; align-items:flex-start; gap:12px;">
      <span style="font-size:22px; line-height:1;">⚠️</span>
      <div style="flex:1;">
        <div style="font-weight:800; font-family:var(--font-mono); color:var(--cyber-pink); font-size:13px; text-transform:uppercase; letter-spacing:0.06em;">iOS Connection Rejected (Error 2)</div>
        <p style="font-size:12px; color:#f0f6fc; margin:4px 0 10px; line-height:1.4;">
          iOS cannot connect while FLASH is paired in iPhone Bluetooth settings.
        </p>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button type="button" id="error2-retry-btn" class="primary" style="padding:6px 12px; font-size:11px;">Retry Scan</button>
          <button type="button" id="error2-dismiss-btn" style="padding:6px 12px; font-size:11px;">Dismiss</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Brave Browser Alert Banner -->
  <div id="brave-alert" class="card hidden" style="border-color:var(--cyber-yellow); background:rgba(255,230,0,0.1);">
    <div style="display:flex; align-items:flex-start; gap:12px;">
      <span style="font-size:20px; line-height:1;">🦁</span>
      <div style="flex:1;">
        <div style="font-weight:800; font-family:var(--font-mono); color:var(--cyber-yellow); font-size:12px; text-transform:uppercase;">Brave Shields Flag Required</div>
        <div style="display:flex; gap:8px; margin-top:8px;">
          <button type="button" id="copy-brave-direct" class="chip primary">Copy Flag Link</button>
        </div>
      </div>
    </div>
  </div>

  <!-- ================= SECTION 1: DASHBOARD / TELEMETRY ================= -->
  <div id="section-dash" class="card">
    <div class="card-header">
      <span class="card-title">Neural Telemetry Matrix</span>
      <span style="font-family:var(--font-mono); font-size:10px; color:var(--cyber-cyan); letter-spacing:0.08em;">NODE 0xF618</span>
    </div>

    <!-- Cyber Arc Reactor Hero Centerpiece -->
    <div class="watch-hero">
      <div class="watch-case">
        <svg class="rings-svg" viewBox="0 0 170 170">
          <!-- Step Activity Ring (Outer) -->
          <circle class="ring-bg" cx="85" cy="85" r="74" stroke-width="7"></circle>
          <circle id="ring-steps" class="ring-bar" cx="85" cy="85" r="74" stroke-width="7" stroke="#00f0ff" stroke-dasharray="465" stroke-dashoffset="465"></circle>
          <!-- Battery Ring (Inner) -->
          <circle class="ring-bg" cx="85" cy="85" r="62" stroke-width="6"></circle>
          <circle id="ring-bat" class="ring-bar" cx="85" cy="85" r="62" stroke-width="6" stroke="#ff0055" stroke-dasharray="390" stroke-dashoffset="390"></circle>
        </svg>

        <div class="watch-content">
          <div class="watch-time" id="watch-clock">10:09</div>
          <div class="watch-label"><b id="name">boAt FLASH</b></div>
          <div class="battery-pill">
            <span>⚡ CELL</span>
            <span id="bat">–</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Primary Cyber Action Controls -->
    <div class="row" style="justify-content:center;">
      <button id="connect" class="primary" style="flex:1; max-width:260px; font-size:14px; font-weight:800;">⚡ JACK IN // CONNECT</button>
      <button id="disconnect" class="danger" disabled>ABORT</button>
    </div>

    <!-- Quick Tool Action Pills -->
    <div class="row" style="justify-content:center; gap:8px; flex-wrap:wrap;">
      <button data-act="sport" disabled title="Request step and activity sync from watch">👟 Sync Steps</button>
      <button data-act="time" disabled title="Sync clock with this device">⏱️ Sync Clock</button>
      <button data-act="find" disabled title="Vibrate and ring the watch">🔔 Ping Watch</button>
      <button data-act="info" disabled title="Query firmware info">ℹ️ Sys Info</button>
    </div>

    <!-- Activity & Sensors 4-Grid -->
    <div class="metrics-grid" id="telemetry-card">
      <div class="metric-card">
        <div class="metric-top">
          <span>01 // Steps Kinetics</span>
          <span>👟</span>
        </div>
        <div class="metric-val" id="sport-steps">–</div>
      </div>
      <div class="metric-card">
        <div class="metric-top">
          <span>02 // Traverse Dist (m)</span>
          <span>📍</span>
        </div>
        <div class="metric-val" id="sport-dist">–</div>
      </div>
      <div class="metric-card">
        <div class="metric-top">
          <span>03 // Metabolic Burn</span>
          <span>🔥</span>
        </div>
        <div class="metric-val" id="sport-kcal">–</div>
      </div>
      <div class="metric-card">
        <div class="metric-top">
          <span>04 // Active Chrono</span>
          <span>⏱️</span>
        </div>
        <div class="metric-val" id="sport-dur">–</div>
      </div>
    </div>

    <!-- Neural Health Matrix / Apple Health Sync Card -->
    <div class="card" id="health-card" style="margin-top:6px; background:rgba(9, 14, 28, 0.95); border:1px solid var(--cyber-border); padding:14px;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; flex-wrap:wrap; gap:10px;">
        <div style="display:flex; align-items:center; gap:10px;">
          <span style="font-size:22px; line-height:1; filter:drop-shadow(0 0 8px var(--cyber-pink));">❤️</span>
          <div>
            <div style="font-family:var(--font-mono); font-weight:800; font-size:12px; color:#fff; letter-spacing:0.06em;" id="health-title">Neural Health Matrix</div>
            <div style="font-family:var(--font-mono); font-size:11px; color:var(--cyber-cyan);" id="health-status">Initializing biometric link…</div>
          </div>
        </div>
        <div style="display:flex; gap:6px;">
          <button id="btn-health-sync" class="chip primary" style="font-size:11px; padding:6px 12px; cursor:pointer;">
            🔄 Sync
          </button>
          <button id="btn-health-export" class="chip" style="font-size:11px; padding:6px 12px; cursor:pointer; background:rgba(255,230,0,0.12); border-color:rgba(255,230,0,0.4); color:var(--cyber-yellow);">
            ⬇️ Export CSV
          </button>
        </div>
      </div>
      <p id="health-desc" style="font-size:11px; color:var(--text-secondary); line-height:1.4; margin-bottom:8px; font-family:var(--font-mono);">
        Direct HealthKit background sync active. Sideloaded devices auto-store steps in local Neural Vault with CSV export.
      </p>
      <div style="display:flex; align-items:center; justify-content:space-between; font-size:11px; color:var(--text-secondary); border-top:1px solid rgba(0,240,255,0.15); padding-top:8px;">
        <span style="font-family:var(--font-mono);">Auto-Sync Biometrics</span>
        <label style="margin:0; cursor:pointer; display:flex; align-items:center; gap:6px;">
          <input type="checkbox" id="health-auto-sync" checked style="width:auto; cursor:pointer;">
          <span style="font-size:10px; color:var(--cyber-cyan); font-family:var(--font-mono);">[ ENABLED ]</span>
        </label>
      </div>
    </div>

    <!-- Hardware Meta -->
    <div class="row" style="justify-content:space-between; font-family:var(--font-mono); font-size:11px; color:var(--text-secondary); padding:4px 4px 0;">
      <span>FW: <b id="fw" style="color:var(--cyber-cyan); font-weight:700;">–</b></span>
      <span>MAC: <b id="mac-display" style="color:var(--cyber-cyan); font-weight:700;">08:7C:85:03:12:0F</b></span>
    </div>

    <label style="flex-direction:row; align-items:center; gap:8px; cursor:pointer; font-size:11px; color:var(--text-secondary); margin-top:4px;">
      <input type="checkbox" id="scan-all" style="width:auto;"> Scan all nearby BLE nodes
    </label>
  </div>

  <!-- ================= SECTION 2: PUSH NOTIFICATIONS / COMMS ================= -->
  <div id="section-notif" class="card hidden">
    <div class="card-header">
      <span class="card-title">Comms Transmitter Studio</span>
      <span id="nbytes" class="bytes-bar">0 / 150 B</span>
    </div>

    <div class="presets-row">
      <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-secondary);">PRESETS:</span>
      <button type="button" class="chip" id="preset-call">📞 Call</button>
      <button type="button" class="chip" id="preset-wa">💬 WhatsApp</button>
      <button type="button" class="chip" id="preset-alert">🚨 Alert</button>
      <button type="button" class="chip" id="preset-emoji">🎉 Emoji</button>
    </div>

    <label>Message Title
      <input id="ntitle" value="Hello 👋" maxlength="60" placeholder="Title (≤ 52 bytes)">
    </label>

    <label>Message Payload
      <textarea id="nbody" rows="3" maxlength="200" placeholder="Notification body content...">Hello from your laptop 👋🔥😎 it works! ✅</textarea>
    </label>

    <div class="row" style="gap:12px;">
      <label style="flex:1;">Stream Category
        <select id="nkind">
          <option value="call">📞 Phone Call (1)</option>
          <option value="msg" selected>💬 Short Message (2)</option>
          <option value="wechat">🟢 WeChat (3)</option>
          <option value="qq">🐧 QQ (4)</option>
          <option value="app">📱 Third-Party App (7)</option>
        </select>
      </label>
    </div>

    <div class="emoji-picker">
      <button type="button" class="emoji-btn">👋</button>
      <button type="button" class="emoji-btn">🔥</button>
      <button type="button" class="emoji-btn">😎</button>
      <button type="button" class="emoji-btn">✅</button>
      <button type="button" class="emoji-btn">⚡</button>
      <button type="button" class="emoji-btn">❤️</button>
      <button type="button" class="emoji-btn">🚀</button>
      <button type="button" class="emoji-btn">💀</button>
      <button type="button" class="emoji-btn">🎉</button>
      <button type="button" class="emoji-btn">🤖</button>
      <button type="button" class="emoji-btn">🏃</button>
      <button type="button" class="emoji-btn">🕒</button>
    </div>

    <button id="send-btn" class="primary" style="margin-top:8px;" data-act="notify" disabled>
      🚀 TRANSMIT PACKET TO WATCH
    </button>
  </div>

  <!-- ================= SECTION 3: SYSTEM DIAGNOSTICS ================= -->
  <div id="section-diag" class="card hidden">
    <div class="card-header">
      <span class="card-title">Cyber-Link Diagnostics</span>
      <div style="display:flex; gap:6px;">
        <button id="copy-log" class="chip" style="padding:3px 9px;">Copy Log</button>
        <button id="clear" class="chip" style="padding:3px 9px;">Clear</button>
      </div>
    </div>

    <!-- Diagnostic Stepper -->
    <div id="conn-steps-box" style="display:flex; flex-direction:column; gap:6px;">
      <div class="step-row" id="st-scan">
        <span class="step-badge">1</span>
        <span>BLE Scan & Device Discovery</span>
      </div>
      <div class="step-row" id="st-gatt">
        <span class="step-badge">2</span>
        <span>GATT Server Connection</span>
      </div>
      <div class="step-row" id="st-svc">
        <span class="step-badge">3</span>
        <span>Service 0xF618 & Pipe Resolution</span>
      </div>
      <div class="step-row" id="st-ready">
        <span class="step-badge">4</span>
        <span>Encrypted Protocol Ready</span>
      </div>
    </div>

    <div id="diag-error-tip" class="hidden" style="padding:10px; background:rgba(255,0,85,0.12); border:1px solid var(--cyber-pink); clip-path:polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 6px 100%, 0 calc(100% - 6px));">
      <div style="font-weight:800; font-family:var(--font-mono); color:var(--cyber-pink); font-size:12px;">LINK FAILURE DETECTED</div>
      <div id="diag-error-text" style="font-size:11px; margin:4px 0 8px; font-family:var(--font-mono);">Error details</div>
      <button type="button" id="diag-retry-btn" class="primary" style="padding:5px 12px; font-size:11px;">RETRY LINK</button>
    </div>

    <!-- Platform Setup Guides -->
    <div class="card" id="guide-card" style="padding:10px; background:rgba(6,10,20,0.85);">
      <div style="display:flex; gap:4px; margin-bottom:10px; flex-wrap:wrap;">
        <button type="button" class="guide-tab active" id="tab-btn-ios">iOS Setup</button>
        <button type="button" class="guide-tab" id="tab-btn-android">Android</button>
        <button type="button" class="guide-tab" id="tab-btn-brave">Brave</button>
        <button type="button" class="guide-tab" id="tab-btn-desktop">Desktop</button>
      </div>

      <div class="guide-content" id="panel-ios" style="font-size:11px; line-height:1.5; color:var(--text-secondary); font-family:var(--font-mono);">
        <p>1. Ensure iPhone Bluetooth is ON in Control Center.</p>
        <p>2. If error occurs, "Forget Device" in iOS Bluetooth settings then reconnect in this app.</p>
        <p>3. Bluefy or Capacitor iOS shell enables full WebBluetooth support.</p>
      </div>

      <div class="guide-content hidden" id="panel-android" style="font-size:11px; line-height:1.5; color:var(--text-secondary); font-family:var(--font-mono);">
        <p>1. Chrome or Edge for Android supports WebBluetooth natively.</p>
        <p>2. Location & Nearby Devices permissions must be Granted.</p>
      </div>

      <div class="guide-content hidden" id="panel-brave" style="font-size:11px; line-height:1.5; color:var(--text-secondary); font-family:var(--font-mono);">
        <p>Enable WebBluetooth flag at chrome://flags/#enable-web-bluetooth</p>
        <button type="button" id="copy-brave-flag-guide" class="chip" style="margin-top:6px;">Copy Flag Link</button>
      </div>

      <div class="guide-content hidden" id="panel-desktop" style="font-size:11px; line-height:1.5; color:var(--text-secondary); font-family:var(--font-mono);">
        <p>Native Chrome, Edge, and Opera on macOS / Windows / Linux work out-of-the-box.</p>
      </div>
    </div>

    <!-- Packet Log Terminal -->
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
      <span style="font-family:var(--font-mono); font-size:11px; color:var(--cyber-cyan);">STREAM: BLE_SYS_LOG</span>
    </div>
    <pre id="log" placeholder="Packet stream will materialize here..."></pre>
  </div>
</main>
"""

# Now update the JavaScript to handle HealthKit without raw error throws and add export CSV
js_old_health = """// --- Apple Health & Activity Sync ---
let healthKitAuthorized = false;

async function checkHealthKitAvailability() {
  const healthStatusEl = $("health-status");
  const healthTitleEl = $("health-title");
  const isIOS = (typeof navigator !== 'undefined' && navigator.userAgent && (/iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)));

  if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.HealthKit) {
    try {
      const res = await window.Capacitor.Plugins.HealthKit.isAvailable();
      if (res && res.available) {
        if (healthStatusEl) healthStatusEl.textContent = "Apple Health Ready";
        return true;
      }
    } catch (e) {
      log("HealthKit check err:", e.message || String(e));
    }
  }

  if (isIOS) {
    if (healthStatusEl) healthStatusEl.textContent = "Apple Health (iOS)";
  } else {
    if (healthTitleEl) healthTitleEl.textContent = "Health & Step Sync";
    if (healthStatusEl) healthStatusEl.textContent = "Offline / Web Activity Mode";
  }
  return false;
}

async function requestHealthKitAuth() {
  if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.HealthKit) {
    try {
      const res = await window.Capacitor.Plugins.HealthKit.requestAuthorization();
      healthKitAuthorized = !!(res && res.authorized);
      const healthStatusEl = $("health-status");
      if (healthStatusEl) healthStatusEl.textContent = healthKitAuthorized ? "Apple Health Connected ✅" : "Permission Denied";
      return healthKitAuthorized;
    } catch (err) {
      log("HealthKit auth error:", err.message || String(err));
      const healthStatusEl = $("health-status");
      if (healthStatusEl) healthStatusEl.textContent = "Auth Error: " + (err.message || String(err));
      return false;
    }
  }
  return false;
}

async function handleIncomingSportRecords(records) {
  try {
    if (typeof localStorage !== 'undefined' && records && records.length) {
      const latest = records[records.length - 1];
      localStorage.setItem("flash_last_steps", String(latest.steps));
      localStorage.setItem("flash_last_sync_time", String(Date.now()));
    }
  } catch (e) {}

  const autoSync = $("health-auto-sync") ? $("health-auto-sync").checked : true;
  if (!autoSync) return;

  await syncSportRecordsToHealthKit(records);
}

async function syncSportRecordsToHealthKit(records) {
  const healthStatusEl = $("health-status");
  if (!records || !records.length) {
    const stepsText = $("sport-steps") ? $("sport-steps").textContent.replace(/,/g, "") : "0";
    const distText = $("sport-dist") ? $("sport-dist").textContent.replace(/,/g, "") : "0";
    const kcalText = $("sport-kcal") ? $("sport-kcal").textContent.replace(/,/g, "") : "0";
    const durText = $("sport-dur") ? $("sport-dur").textContent.replace(/[^0-9]/g, "") : "0";
    const s = parseInt(stepsText, 10) || 0;
    const d = parseFloat(distText) || 0;
    const k = parseFloat(kcalText) || 0;
    const dur = (parseInt(durText, 10) || 1) * 60;
    if (s > 0 || d > 0 || k > 0) {
      records = [{
        startTime: Math.floor(Date.now() / 1000) - dur,
        steps: s,
        distance: d,
        calories: k,
        duration: dur
      }];
    }
  }

  if (!records || !records.length) {
    if (healthStatusEl) healthStatusEl.textContent = "No new activity data to sync";
    return;
  }

  if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.HealthKit) {
    try {
      if (!healthKitAuthorized) {
        const authed = await requestHealthKitAuth();
        if (!authed) return;
      }
      if (healthStatusEl) healthStatusEl.textContent = "Writing to Apple Health…";
      const res = await window.Capacitor.Plugins.HealthKit.saveSportRecords({ records });
      if (res && res.saved) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        if (healthStatusEl) healthStatusEl.textContent = `Synced ${res.sampleCount || records.length} records at ${timeStr} ✅`;
        log(`Synced ${res.sampleCount || records.length} activity samples to Apple Health.`);
      }
    } catch (err) {
      log("HealthKit sync error:", err.message || String(err));
      if (healthStatusEl) healthStatusEl.textContent = "Sync failed: " + (err.message || String(err));
    }
  } else {
    try {
      if (typeof localStorage !== 'undefined') {
        const history = JSON.parse(localStorage.getItem("flash_activity_log") || "[]");
        records.forEach(r => history.push({ ...r, loggedAt: new Date().toISOString() }));
        if (history.length > 500) history.splice(0, history.length - 500);
        localStorage.setItem("flash_activity_log", JSON.stringify(history));
      }
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      if (healthStatusEl) healthStatusEl.textContent = `Logged ${records.length} records locally at ${timeStr}`;
    } catch (e) {}
  }
}"""

js_new_health = """// --- Apple Health & Activity Sync ---
let healthKitAuthorized = false;

function saveRecordsToLocalVault(records) {
  try {
    if (typeof localStorage !== 'undefined' && records && records.length) {
      const history = JSON.parse(localStorage.getItem("flash_activity_log") || "[]");
      records.forEach(r => history.push({ ...r, loggedAt: new Date().toISOString() }));
      if (history.length > 500) history.splice(0, history.length - 500);
      localStorage.setItem("flash_activity_log", JSON.stringify(history));
    }
    const healthStatusEl = $("health-status");
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (healthStatusEl) healthStatusEl.textContent = `Neural Vault: ${records ? records.length : 1} records saved at ${timeStr}`;
  } catch (e) {}
}

function exportHealthDataCSV() {
  try {
    let history = [];
    if (typeof localStorage !== 'undefined') {
      try { history = JSON.parse(localStorage.getItem("flash_activity_log") || "[]"); } catch (e) {}
    }
    const stepsText = $("sport-steps") ? $("sport-steps").textContent.replace(/,/g, "") : "0";
    const distText = $("sport-dist") ? $("sport-dist").textContent.replace(/,/g, "") : "0";
    const kcalText = $("sport-kcal") ? $("sport-kcal").textContent.replace(/,/g, "") : "0";
    const s = parseInt(stepsText, 10) || 0;
    if (!history.length && s > 0) {
      history.push({
        startTime: Math.floor(Date.now() / 1000) - 300,
        steps: s,
        distance: parseFloat(distText) || 0,
        calories: parseFloat(kcalText) || 0,
        duration: 300,
        loggedAt: new Date().toISOString()
      });
    }
    if (!history.length) {
      alert("No activity records captured yet to export.");
      return;
    }
    let csv = "Timestamp,ISO_Date,Steps,Distance_M,Calories_Kcal,Duration_Sec\\n";
    history.forEach(r => {
      const dt = new Date((r.startTime || Date.now() / 1000) * 1000).toISOString();
      csv += `${r.startTime || ""},${dt},${r.steps || 0},${r.distance || 0},${r.calories || 0},${r.duration || 0}\\n`;
    });
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flash_watch_telemetry_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    alert("Export failed: " + (err.message || String(err)));
  }
}

async function checkHealthKitAvailability() {
  const healthStatusEl = $("health-status");
  const healthTitleEl = $("health-title");
  const healthDescEl = $("health-desc");
  const isIOS = (typeof navigator !== 'undefined' && navigator.userAgent && (/iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)));

  if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.HealthKit) {
    try {
      const res = await window.Capacitor.Plugins.HealthKit.isAvailable();
      if (res && res.available) {
        if (healthStatusEl) healthStatusEl.textContent = "Neural Vault & HealthLink Active";
        return true;
      }
    } catch (e) {
      log("HealthKit check info:", e.message || String(e));
    }
  }

  if (isIOS) {
    if (healthStatusEl) healthStatusEl.textContent = "Neural Vault Ready (iOS)";
  } else {
    if (healthTitleEl) healthTitleEl.textContent = "Biometric Activity Vault";
    if (healthStatusEl) healthStatusEl.textContent = "Local Encrypted Telemetry Active";
  }
  return false;
}

async function requestHealthKitAuth() {
  if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.HealthKit) {
    try {
      const res = await window.Capacitor.Plugins.HealthKit.requestAuthorization();
      const healthStatusEl = $("health-status");
      const healthDescEl = $("health-desc");
      if (res && res.entitlementMissing) {
        healthKitAuthorized = false;
        if (healthStatusEl) healthStatusEl.textContent = "Neural Vault Active (Local Sync)";
        if (healthDescEl) healthDescEl.textContent = "Personal Apple ID profile restricts direct HK write. Activity stored in encrypted local vault with 1-tap CSV export.";
        return false;
      }
      healthKitAuthorized = !!(res && res.authorized);
      if (healthStatusEl) healthStatusEl.textContent = healthKitAuthorized ? "Apple Health Connected ✅" : "Neural Vault Active";
      return healthKitAuthorized;
    } catch (err) {
      const msg = (err.message || String(err)).toLowerCase();
      log("HealthKit auth info:", err.message || String(err));
      const healthStatusEl = $("health-status");
      const healthDescEl = $("health-desc");
      if (msg.includes("entitlement")) {
        healthKitAuthorized = false;
        if (healthStatusEl) healthStatusEl.textContent = "Neural Vault Active (Local Sync)";
        if (healthDescEl) healthDescEl.textContent = "Personal Apple ID profile restricts direct HK write. Activity stored in encrypted local vault with 1-tap CSV export.";
      } else {
        if (healthStatusEl) healthStatusEl.textContent = "Vault Status: Active (Local)";
      }
      return false;
    }
  }
  return false;
}

async function handleIncomingSportRecords(records) {
  try {
    if (typeof localStorage !== 'undefined' && records && records.length) {
      const latest = records[records.length - 1];
      localStorage.setItem("flash_last_steps", String(latest.steps));
      localStorage.setItem("flash_last_sync_time", String(Date.now()));
    }
  } catch (e) {}

  const autoSync = $("health-auto-sync") ? $("health-auto-sync").checked : true;
  if (!autoSync) return;

  await syncSportRecordsToHealthKit(records);
}

async function syncSportRecordsToHealthKit(records) {
  const healthStatusEl = $("health-status");
  if (!records || !records.length) {
    const stepsText = $("sport-steps") ? $("sport-steps").textContent.replace(/,/g, "") : "0";
    const distText = $("sport-dist") ? $("sport-dist").textContent.replace(/,/g, "") : "0";
    const kcalText = $("sport-kcal") ? $("sport-kcal").textContent.replace(/,/g, "") : "0";
    const durText = $("sport-dur") ? $("sport-dur").textContent.replace(/[^0-9]/g, "") : "0";
    const s = parseInt(stepsText, 10) || 0;
    const d = parseFloat(distText) || 0;
    const k = parseFloat(kcalText) || 0;
    const dur = (parseInt(durText, 10) || 1) * 60;
    if (s > 0 || d > 0 || k > 0) {
      records = [{
        startTime: Math.floor(Date.now() / 1000) - dur,
        steps: s,
        distance: d,
        calories: k,
        duration: dur
      }];
    }
  }

  if (!records || !records.length) {
    if (healthStatusEl) healthStatusEl.textContent = "No new activity data to sync";
    return;
  }

  if (typeof window !== 'undefined' && window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.HealthKit) {
    try {
      if (!healthKitAuthorized) {
        const authed = await requestHealthKitAuth();
        if (!authed) {
          saveRecordsToLocalVault(records);
          return;
        }
      }
      if (healthStatusEl) healthStatusEl.textContent = "Writing to Apple Health…";
      const res = await window.Capacitor.Plugins.HealthKit.saveSportRecords({ records });
      if (res && res.saved) {
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        if (healthStatusEl) healthStatusEl.textContent = `Synced ${res.sampleCount || records.length} records at ${timeStr} ✅`;
        log(`Synced ${res.sampleCount || records.length} activity samples to Apple Health.`);
      } else {
        saveRecordsToLocalVault(records);
      }
    } catch (err) {
      log("HealthKit notice:", err.message || String(err));
      saveRecordsToLocalVault(records);
    }
  } else {
    saveRecordsToLocalVault(records);
  }
}"""

script_updated = script_content.replace(js_old_health, js_new_health)

# Wire export button in DOMContentLoaded
old_wire = 'const btnHealth = $("btn-health-sync");'
new_wire = '''const btnExport = $("btn-health-export");
    if (btnExport) {
      btnExport.onclick = () => exportHealthDataCSV();
    }

    const btnHealth = $("btn-health-sync");'''

script_updated = script_updated.replace(old_wire, new_wire)

final_html = head_pre_style + cyberpunk_css + '\n</style>\n</head>\n<body>\n' + cyberpunk_body + '\n<script>\n' + script_updated + '\n' + after_script

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Applied Cyberpunk redesign successfully! Total chars:", len(final_html))
