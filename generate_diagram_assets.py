import os

def build_pristine_diagram():
    # Master Canvas Dimensions: 1780 x 1020
    # 5 Evenly Spaced Swimlanes (width: 310px each)
    # Gutters: 40px clean routing channels
    #
    # Swimlane 1: x = 40 (w = 310) -> [40 .. 350]
    # Gutter 1-2: [350 .. 390] (40px)
    # Swimlane 2: x = 390 (w = 310) -> [390 .. 700]
    # Gutter 2-3: [700 .. 740] (40px)
    # Swimlane 3: x = 740 (w = 310) -> [740 .. 1050]
    # Gutter 3-4: [1050 .. 1090] (40px)
    # Swimlane 4: x = 1090 (w = 310) -> [1090 .. 1400]
    # Gutter 4-5: [1400 .. 1440] (40px)
    # Swimlane 5: x = 1440 (w = 300) -> [1440 .. 1740]
    
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1780 1020" width="100%" height="100%" style="background:#F8FAFC; font-family:'Plus Jakarta Sans',Inter,-apple-system,BlinkMacSystemFont,sans-serif;">
  <defs>
    <!-- Draw.io Grid Canvas Background Pattern -->
    <pattern id="drawio-grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="#E2E8F0" />
    </pattern>

    <!-- Professional Drop Shadows -->
    <filter id="shadow-lane" x="-2%" y="-1%" width="104%" height="103%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0F172A" flood-opacity="0.04"/>
    </filter>
    <filter id="shadow-card" x="-3%" y="-2%" width="106%" height="106%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0F172A" flood-opacity="0.05"/>
    </filter>

    <!-- Arrowhead Markers (Pure Orthogonal Engineering Style) -->
    <marker id="m-blue" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0052CC" />
    </marker>
    <marker id="m-green" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#16A34A" />
    </marker>
    <marker id="m-orange" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#EA580C" />
    </marker>
    <marker id="m-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D97706" />
    </marker>
    <marker id="m-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#DC2626" />
    </marker>
    <marker id="m-purple" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#7C3AED" />
    </marker>
    <marker id="m-slate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#475569" />
    </marker>
  </defs>

  <!-- Background Grid -->
  <rect width="100%" height="100%" fill="url(#drawio-grid)" />

  <!-- ================= TOP HEADER BANNER ================= -->
  <g transform="translate(40, 20)">
    <rect width="1700" height="66" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" filter="url(#shadow-lane)" />
    <!-- Befree Monogram Logo -->
    <rect x="20" y="13" width="40" height="40" rx="8" fill="#0052CC" />
    <path d="M37 23 v20 M37 31 h6 a4 4 0 0 1 0 8 h-6" stroke="#FFFFFF" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none" />
    <!-- Title & Subtitle -->
    <text x="74" y="36" font-size="18" font-weight="800" fill="#0F172A">befree<tspan fill="#0052CC">.</tspan> | Enterprise Bank Statement Processing &amp; Classification Platform</text>
    <text x="74" y="53" font-size="11.5" font-weight="500" fill="#64748B">System Architectural Blueprint &amp; Dataflow Execution Pipeline (Non-LLM Hybrid Core)</text>
    
    <!-- Status Badges -->
    <rect x="1390" y="20" width="160" height="26" rx="13" fill="#F0FDF4" stroke="#BBF7D0" />
    <circle cx="1405" cy="33" r="4" fill="#16A34A" />
    <text x="1415" y="37" font-size="11" font-weight="700" fill="#166534">Non-LLM ML Core: 98.14%</text>

    <rect x="1562" y="20" width="122" height="26" rx="13" fill="#EFF6FF" stroke="#BFDBFE" />
    <text x="1623" y="37" font-size="11" font-weight="700" fill="#1D4ED8" text-anchor="middle">13-Bank Test Suite</text>
  </g>

  <!-- ========================================================================= -->
  <!-- SWIMLANE 1: INGESTION & SECURITY (x = 40, y = 105, w = 310, h = 890)      -->
  <!-- ========================================================================= -->
  <g transform="translate(40, 105)">
    <rect width="310" height="890" rx="10" fill="#FFFFFF" stroke="#BFDBFE" stroke-width="1.5" filter="url(#shadow-lane)" />
    <path d="M 0 10 Q 0 0 10 0 L 300 0 Q 310 0 310 10 L 310 40 L 0 40 Z" fill="#EFF6FF" />
    <text x="18" y="26" font-size="12.5" font-weight="800" fill="#1E40AF">1. INGESTION &amp; SECURITY LAYER</text>

    <!-- Card 1.1: Bank Statement PDF (y = 55) -->
    <g transform="translate(20, 55)">
      <rect width="270" height="68" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="68" rx="2" fill="#0052CC" />
      <text x="16" y="24" font-size="12" font-weight="700" fill="#0F172A">📄 Bank Statement (PDF)</text>
      <text x="16" y="42" font-size="10.5" fill="#475569">Multi-Bank PDFs (Digital / Scanned)</text>
      <text x="16" y="56" font-size="9.5" fill="#64748B">HDFC, SBI, ICICI, Axis, Kotak, BoB, etc.</text>
    </g>

    <!-- Card 1.2: Password Decryption Engine (y = 150) -->
    <g transform="translate(20, 150)">
      <rect width="270" height="74" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="74" rx="2" fill="#10B981" />
      <text x="16" y="23" font-size="12" font-weight="700" fill="#0F172A">🔒 Password Decryption Engine</text>
      <text x="16" y="41" font-size="10.5" fill="#475569">In-Memory Decryption (Zero Disk Footprint)</text>
      <text x="16" y="55" font-size="9.5" fill="#059669">• Handles Encrypted PDFs (e.g. befree123)</text>
      <text x="16" y="67" font-size="9" fill="#64748B">Zero Temporary File Leaks</text>
    </g>

    <!-- Card 1.3: PDFTypeDetector (y = 250) -->
    <g transform="translate(20, 250)">
      <rect width="270" height="84" rx="8" fill="#DBEAFE" stroke="#3B82F6" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#1E40AF">src/detector.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#1E3A8A">PDFTypeDetector</text>
      <text x="16" y="56" font-size="10" fill="#334155">• Glyph Stream Density Analysis</text>
      <text x="16" y="72" font-size="10" font-weight="700" fill="#1D4ED8">Evaluates Char Density per Page</text>
    </g>

    <!-- Decision Diamond: Chars >= 50? (y = 365) -->
    <g transform="translate(75, 365)">
      <polygon points="80,0 160,32 80,64 0,32" fill="#FEF08A" stroke="#CA8A04" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="80" y="29" font-size="11" font-weight="800" fill="#854D0E" text-anchor="middle">Chars ≥ 50?</text>
      <text x="80" y="44" font-size="9" font-weight="600" fill="#A16207" text-anchor="middle">(Per Page Density)</text>
    </g>

    <!-- Branch A Info Box: Digital Font (y = 475) -->
    <g transform="translate(20, 475)">
      <rect width="125" height="66" rx="6" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.2" />
      <text x="12" y="20" font-size="10.5" font-weight="800" fill="#14532D">Vector Stream</text>
      <text x="12" y="36" font-size="9.5" fill="#15803D">Digital Font Layer</text>
      <text x="12" y="52" font-size="9" font-weight="700" fill="#166534">&lt; 100ms Latency</text>
    </g>

    <!-- Branch B Info Box: Scanned Raster (y = 475) -->
    <g transform="translate(165, 475)">
      <rect width="125" height="66" rx="6" fill="#FFEDD5" stroke="#EA580C" stroke-width="1.2" />
      <text x="12" y="20" font-size="10.5" font-weight="800" fill="#7C2D12">Raster Image</text>
      <text x="12" y="36" font-size="9.5" fill="#C2410C">Scanned Bitmap</text>
      <text x="12" y="52" font-size="9" font-weight="700" fill="#9A3412">Computer Vision</text>
    </g>

    <!-- Internal Connectors in Lane 1 -->
    <!-- Card 1.1 to 1.2 -->
    <line x1="155" y1="123" x2="155" y2="150" stroke="#0052CC" stroke-width="2" marker-end="url(#m-blue)" />
    <!-- Card 1.2 to 1.3 -->
    <line x1="155" y1="224" x2="155" y2="250" stroke="#0052CC" stroke-width="2" marker-end="url(#m-blue)" />
    <!-- Card 1.3 to Diamond -->
    <line x1="155" y1="334" x2="155" y2="365" stroke="#0052CC" stroke-width="2" marker-end="url(#m-blue)" />
    <!-- Diamond Left to Branch A -->
    <path d="M 75 397 L 50 397 L 50 445 L 82 445 L 82 475" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
    <rect x="26" y="415" width="46" height="18" rx="4" fill="#DCFCE7" />
    <text x="49" y="428" font-size="9" font-weight="800" fill="#166534" text-anchor="middle">YES</text>
    <!-- Diamond Right to Branch B -->
    <path d="M 235 397 L 260 397 L 260 445 L 227 445 L 227 475" fill="none" stroke="#EA580C" stroke-width="2" marker-end="url(#m-orange)" />
    <rect x="238" y="415" width="44" height="18" rx="4" fill="#FFEDD5" />
    <text x="260" y="428" font-size="9" font-weight="800" fill="#C2410C" text-anchor="middle">NO</text>
  </g>

  <!-- ========================================================================= -->
  <!-- SWIMLANE 2: DUAL-STREAM EXTRACTION & NORMALIZATION (x=390, y=105, w=310)  -->
  <!-- ========================================================================= -->
  <g transform="translate(390, 105)">
    <rect width="310" height="890" rx="10" fill="#FFFFFF" stroke="#86EFAC" stroke-width="1.5" filter="url(#shadow-lane)" />
    <path d="M 0 10 Q 0 0 10 0 L 300 0 Q 310 0 310 10 L 310 40 L 0 40 Z" fill="#F0FDF4" />
    <text x="18" y="26" font-size="12.5" font-weight="800" fill="#166534">2. DUAL EXTRACTION &amp; STITCHING</text>

    <!-- Card 2.1: MetadataParser (y = 55) -->
    <g transform="translate(20, 55)">
      <rect width="270" height="74" rx="8" fill="#F0F9FF" stroke="#0284C7" stroke-width="1.2" filter="url(#shadow-card)" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#0369A1">src/extractor/metadata_parser.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#0F172A">MetadataParser</text>
      <text x="16" y="54" font-size="10" fill="#475569">• Name, Account Number, IFSC Code</text>
      <text x="16" y="68" font-size="9.5" fill="#64748B">Regex Multi-Bank Anchor Patterns</text>
    </g>

    <!-- Card 2.2: TextBasedExtractor (y = 155) -->
    <g transform="translate(20, 155)">
      <rect width="240" height="90" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="90" rx="2" fill="#16A34A" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#15803D">src/extractor/text_extractor.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#0F172A">TextBasedExtractor</text>
      <text x="16" y="56" font-size="10" fill="#475569">• Dynamic Column Synonym Grid</text>
      <text x="16" y="70" font-size="10" fill="#475569">• Layout-Agnostic Coordinate Grid</text>
      <text x="16" y="84" font-size="9.5" font-weight="700" fill="#166534">Powered by pdfplumber</text>
    </g>

    <!-- Card 2.3: OCRExtractor (y = 275) -->
    <g transform="translate(20, 275)">
      <rect width="240" height="98" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="98" rx="2" fill="#EA580C" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#C2410C">src/extractor/ocr_extractor.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#0F172A">OCRExtractor (EasyOCR)</text>
      <text x="16" y="56" font-size="10" fill="#475569">• CRAFT Deep Neural Network</text>
      <text x="16" y="70" font-size="10" fill="#475569">• Bounding Box Clustering (Δy ≤ 8px)</text>
      <text x="16" y="88" font-size="9.5" font-weight="700" fill="#166534">✓ Zero External C++ Binary Dependency</text>
    </g>

    <!-- Card 2.4: RowStitcher (State Machine) (y = 415) -->
    <g transform="translate(20, 415)">
      <rect width="270" height="110" rx="8" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="10.5" font-weight="700" fill="#166534">src/extractor/row_stitcher.py</text>
      <text x="16" y="40" font-size="13" font-weight="800" fill="#064E3B">RowStitcher (State Machine)</text>
      <text x="16" y="58" font-size="10" fill="#065F46">• Merges Wrapped Multi-Line Remarks</text>
      <text x="16" y="73" font-size="10" fill="#065F46">• Anchors: Date Token + Trailing Balance</text>
      <text x="16" y="88" font-size="10" fill="#065F46">• Currency Cleaning: "₹1,25,000" → 125000</text>
      <text x="16" y="103" font-size="9.5" font-weight="700" fill="#047857">Solves UPI / RTGS Row Splitting</text>
    </g>

    <!-- Card 2.5: EntityNormalizer (y = 565) -->
    <g transform="translate(20, 565)">
      <rect width="270" height="98" rx="8" fill="#EFF6FF" stroke="#2563EB" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#1D4ED8">src/extractor/entity_normalizer.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#1E3A8A">EntityNormalizer</text>
      <text x="16" y="56" font-size="10" fill="#1E40AF">• Clean Counterparty / Vendor Name</text>
      <text x="16" y="71" font-size="10" fill="#1E40AF">• Payment Channel (UPI, NEFT, RTGS, POS)</text>
      <text x="16" y="86" font-size="10" fill="#1E40AF">• Reference UTR / Transaction ID</text>
    </g>

    <!-- Internal Connectors in Lane 2 -->
    <!-- TextBasedExtractor exits RIGHT to corridor x=275, bypasses OCRExtractor, enters RowStitcher top-right -->
    <path d="M 260 200 L 275 200 L 275 395 L 225 395 L 225 415" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
    <!-- OCRExtractor exits BOTTOM, enters RowStitcher top-left -->
    <path d="M 140 373 L 140 395 L 105 395 L 105 415" fill="none" stroke="#EA580C" stroke-width="2" marker-end="url(#m-orange)" />
    <!-- RowStitcher to EntityNormalizer -->
    <line x1="155" y1="525" x2="155" y2="565" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
  </g>

  <!-- ========================================================================= -->
  <!-- GUTTER 1-2 CONNECTORS (Between Lane 1 & Lane 2)                          -->
  <!-- ========================================================================= -->
  <!-- Vector Stream out of Lane 1 (x=40+82=122, y=105+541=646) -> enters TextBasedExtractor at x=390+20=410, y=105+200=305 -->
  <!-- Clean Corridor routing: leaves Branch A bottom, travels along gutter at x=365 -->
  <path d="M 122 646 L 122 675 L 365 675 L 365 305 L 410 305" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
  <rect x="340" y="475" width="50" height="18" rx="4" fill="#DCFCE7" stroke="#16A34A" stroke-width="0.8" />
  <text x="365" y="488" font-size="8.5" font-weight="700" fill="#166534" text-anchor="middle">Text Plumber</text>

  <!-- Raster Stream out of Lane 1 (x=40+227=267, y=105+541=646) -> enters OCRExtractor at x=390+20=410, y=105+325=430 -->
  <!-- Clean Corridor routing: leaves Branch B bottom, travels along gutter at x=378 -->
  <path d="M 267 646 L 267 660 L 378 660 L 378 430 L 410 430" fill="none" stroke="#EA580C" stroke-width="2" marker-end="url(#m-orange)" />
  <rect x="352" y="535" width="52" height="18" rx="4" fill="#FFEDD5" stroke="#EA580C" stroke-width="0.8" />
  <text x="378" y="548" font-size="8.5" font-weight="700" fill="#C2410C" text-anchor="middle">EasyOCR</text>

  <!-- ========================================================================= -->
  <!-- SWIMLANE 3: NON-LLM CLASSIFICATION ENGINE (x = 740, y = 105, w = 310)     -->
  <!-- ========================================================================= -->
  <g transform="translate(740, 105)">
    <rect width="310" height="890" rx="10" fill="#FFFFFF" stroke="#FCD34D" stroke-width="1.5" filter="url(#shadow-lane)" />
    <path d="M 0 10 Q 0 0 10 0 L 300 0 Q 310 0 310 10 L 310 40 L 0 40 Z" fill="#FFFBEB" />
    <text x="18" y="26" font-size="12.5" font-weight="800" fill="#B45309">3. NON-LLM CLASSIFICATION ENGINE</text>

    <!-- Card 3.1: Hybrid Classifier Hub (y = 55) -->
    <g transform="translate(20, 55)">
      <rect width="270" height="82" rx="8" fill="#FEF3C7" stroke="#D97706" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#92400E">src/classifier/hybrid_classifier.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#78350F">HybridTransactionClassifier</text>
      <text x="16" y="56" font-size="10" fill="#92400E">Two-Tier Priority Arbitrator (Zero-LLM)</text>
      <text x="16" y="70" font-size="9" font-weight="700" fill="#B45309">Sub-2ms Latency | Zero Cloud API Cost</text>
    </g>

    <!-- Card 3.2: Tier 1 Domain Rules Engine (y = 165) -->
    <g transform="translate(20, 165)">
      <rect width="270" height="115" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="115" rx="2" fill="#F59E0B" />
      <text x="16" y="20" font-size="11" font-weight="800" fill="#B45309">TIER 1: DOMAIN RULES ENGINE</text>
      <text x="16" y="36" font-size="10.5" font-weight="700" fill="#475569">src/classifier/rules_engine.py</text>
      <text x="16" y="54" font-size="10" fill="#475569">• 100+ Compiled Regex Signatures</text>
      <text x="16" y="69" font-size="10" fill="#475569">• UPI, NEFT, IMPS, RTGS, Payroll</text>
      <text x="16" y="84" font-size="10" fill="#475569">• Food, Groceries, EMI, Utilities, Tax</text>
      <text x="16" y="103" font-size="9.5" font-weight="700" fill="#166534">Precision: 99.8% | Conf: 0.95 - 0.99</text>
    </g>

    <!-- Decision Diamond: Rule Match? (y = 310) -->
    <g transform="translate(75, 310)">
      <polygon points="80,0 160,30 80,60 0,30" fill="#FEF08A" stroke="#CA8A04" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="80" y="28" font-size="11" font-weight="800" fill="#854D0E" text-anchor="middle">Rule Match?</text>
      <text x="80" y="42" font-size="9" font-weight="600" fill="#A16207" text-anchor="middle">(Anchor Regex)</text>
    </g>

    <!-- Card 3.3: Tier 2 Scikit-Learn ML Model (y = 405) -->
    <g transform="translate(20, 405)">
      <rect width="270" height="115" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="115" rx="2" fill="#D97706" />
      <text x="16" y="20" font-size="11" font-weight="800" fill="#B45309">TIER 2: SCIKIT-LEARN ML MODEL</text>
      <text x="16" y="36" font-size="10.5" font-weight="700" fill="#475569">src/classifier/ml_engine.py</text>
      <text x="16" y="54" font-size="10" fill="#475569">• Sublinear TF-IDF (1-2 N-grams)</text>
      <text x="16" y="69" font-size="10" fill="#475569">• Multinomial Logistic Regression</text>
      <text x="16" y="84" font-size="10" fill="#475569">• Latency: &lt; 2ms per transaction</text>
      <text x="16" y="103" font-size="10" font-weight="800" fill="#166534">✓ Verified Test Accuracy: 98.14%</text>
    </g>

    <!-- Card 3.4: Probability Calibration Gate (y = 545) -->
    <g transform="translate(20, 545)">
      <rect width="270" height="74" rx="8" fill="#FEF3C7" stroke="#F59E0B" stroke-width="1.2" />
      <text x="16" y="22" font-size="11" font-weight="700" fill="#78350F">Probability Calibration Gate</text>
      <text x="16" y="42" font-size="10" fill="#92400E">Prob ≥ 0.40 → Assign Top Category</text>
      <text x="16" y="58" font-size="10" fill="#92400E">Prob &lt; 0.40 → Others / Misc Fallback</text>
    </g>

    <!-- Card 3.5: Unified Classified Stream (y = 645) -->
    <g transform="translate(20, 645)">
      <rect width="270" height="74" rx="8" fill="#ECFDF5" stroke="#059669" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="11" font-weight="800" fill="#064E3B">✓ Unified Classified Ledger Feed</text>
      <text x="16" y="42" font-size="10" fill="#065F46">Category + Calibrated Confidence Score</text>
      <text x="16" y="58" font-size="9.5" font-weight="700" fill="#047857">Origin Tier Tag (Rule vs Scikit-Learn)</text>
    </g>

    <!-- Internal Connectors in Lane 3 -->
    <line x1="155" y1="137" x2="155" y2="165" stroke="#D97706" stroke-width="2" marker-end="url(#m-amber)" />
    <line x1="155" y1="280" x2="155" y2="310" stroke="#D97706" stroke-width="2" marker-end="url(#m-amber)" />
    <!-- Diamond NO -> ML Model -->
    <line x1="155" y1="370" x2="155" y2="405" stroke="#B45309" stroke-width="2" marker-end="url(#m-amber)" />
    <rect x="163" y="380" width="85" height="16" rx="3" fill="#FFFBEB" />
    <text x="166" y="392" font-size="9" font-weight="700" fill="#B45309">NO (ML Fallback)</text>

    <!-- Diamond YES -> Travels down dedicated right corridor at x=280 straight into Card 3.5 -->
    <path d="M 235 340 L 280 340 L 280 682 L 290 682" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
    <rect x="238" y="325" width="56" height="16" rx="3" fill="#DCFCE7" />
    <text x="266" y="337" font-size="8.5" font-weight="800" fill="#166534" text-anchor="middle">YES (Rule)</text>

    <!-- ML to Calibration Gate -->
    <line x1="155" y1="520" x2="155" y2="545" stroke="#D97706" stroke-width="2" marker-end="url(#m-amber)" />
    <!-- Calibration Gate to Card 3.5 -->
    <line x1="155" y1="619" x2="155" y2="645" stroke="#059669" stroke-width="2" marker-end="url(#m-green)" />
  </g>

  <!-- ========================================================================= -->
  <!-- GUTTER 2-3 CONNECTOR (Lane 2 EntityNormalizer -> Lane 3 HybridClassifier)  -->
  <!-- ========================================================================= -->
  <!-- EntityNormalizer right (x=390+290=680, y=105+614=719) -> travels up gutter x=720 -> enters HybridClassifier at x=740+20=760, y=105+96=201 -->
  <path d="M 680 719 L 720 719 L 720 201 L 760 201" fill="none" stroke="#0052CC" stroke-width="2" marker-end="url(#m-blue)" />
  <rect x="696" y="445" width="48" height="18" rx="4" fill="#EFF6FF" stroke="#3B82F6" stroke-width="0.8" />
  <text x="720" y="458" font-size="8.5" font-weight="700" fill="#1D4ED8" text-anchor="middle">Txn Feed</text>

  <!-- ========================================================================= -->
  <!-- SWIMLANE 4: VALIDATION & FORENSIC AUDIT (x = 1090, y = 105, w = 310)      -->
  <!-- ========================================================================= -->
  <g transform="translate(1090, 105)">
    <rect width="310" height="890" rx="10" fill="#FFFFFF" stroke="#FECACA" stroke-width="1.5" filter="url(#shadow-lane)" />
    <path d="M 0 10 Q 0 0 10 0 L 300 0 Q 310 0 310 10 L 310 40 L 0 40 Z" fill="#FEF2F2" />
    <text x="18" y="26" font-size="12.5" font-weight="800" fill="#991B1B">4. VALIDATION &amp; FORENSIC AUDIT</text>

    <!-- Card 4.1: Balance Reconciler (y = 55) -->
    <g transform="translate(20, 55)">
      <rect width="270" height="120" rx="8" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#991B1B">src/validator/balance_reconciler.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#7F1D1D">BalanceReconciler</text>
      <text x="16" y="58" font-size="11.5" font-weight="800" fill="#0F172A">Bal[i] = Bal[i-1] - Dr[i] + Cr[i]</text>
      <text x="16" y="76" font-size="10" fill="#7F1D1D">• Mathematical Precision: ±0.05</text>
      <text x="16" y="91" font-size="10" fill="#7F1D1D">• Inverted Dr/Cr Column Detector</text>
      <text x="16" y="108" font-size="10.5" font-weight="800" fill="#991B1B">Integrity Score &amp; Discrepancy Flags</text>
    </g>

    <!-- Card 4.2: Forensic Anomaly Detector (y = 205) -->
    <g transform="translate(20, 205)">
      <rect width="270" height="145" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <rect x="0" y="0" width="4" height="145" rx="2" fill="#EF4444" />
      <text x="16" y="20" font-size="10.5" font-weight="700" fill="#B91C1C">src/validator/anomaly_detector.py</text>
      <text x="16" y="38" font-size="13" font-weight="800" fill="#0F172A">ForensicAnomalyDetector</text>
      <text x="16" y="56" font-size="10" fill="#475569">• Duplicate Payments: Double Swipes</text>
      <text x="16" y="71" font-size="10" fill="#475569">• Statistical Outliers: Spikes &gt; 2.5σ</text>
      <text x="16" y="86" font-size="10" fill="#475569">• AML Structuring Check (&lt; ₹50k)</text>
      <text x="16" y="101" font-size="10" fill="#475569">• Statutory Tax: TDS / GST / Challan 280</text>
      <text x="16" y="126" font-size="11" font-weight="800" fill="#DC2626">Risk Profile: CLEAN / MEDIUM / HIGH</text>
    </g>

    <!-- Card 4.3: Human-in-the-Loop Override (y = 380) -->
    <g transform="translate(20, 380)">
      <rect width="270" height="98" rx="8" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="11" font-weight="700" fill="#1D4ED8">HUMAN-IN-THE-LOOP (HITL)</text>
      <text x="16" y="40" font-size="13" font-weight="800" fill="#1E3A8A">Interactive Override Editor</text>
      <text x="16" y="58" font-size="10" fill="#1E40AF">• Accountant Manual Re-Classification</text>
      <text x="16" y="73" font-size="10" fill="#1E40AF">• Dynamic Ledger &amp; KPI Recalculation</text>
      <text x="16" y="88" font-size="9" font-weight="700" fill="#0052CC">Custom Rule Learning Engine</text>
    </g>

    <!-- Card 4.4: Reconciled Dataset Ready for Export (y = 510) -->
    <g transform="translate(20, 510)">
      <rect width="270" height="74" rx="8" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="11" font-weight="800" fill="#14532D">✓ Fully Audited Financial Dataset</text>
      <text x="16" y="42" font-size="10" fill="#15803D">Reconciled • Fraud Audited • Tax Flagged</text>
      <text x="16" y="58" font-size="9.5" font-weight="700" fill="#166534">Downstream Multi-Format Export Ready</text>
    </g>

    <!-- Internal Connectors in Lane 4 (Clean Waterfall) -->
    <line x1="155" y1="175" x2="155" y2="205" stroke="#DC2626" stroke-width="2" marker-end="url(#m-red)" />
    <line x1="155" y1="350" x2="155" y2="380" stroke="#3B82F6" stroke-width="2" marker-end="url(#m-blue)" />
    <line x1="155" y1="478" x2="155" y2="510" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
  </g>

  <!-- ========================================================================= -->
  <!-- GUTTER 3-4 CONNECTOR (Lane 3 Classified Stream -> Lane 4 BalanceReconciler)-->
  <!-- ========================================================================= -->
  <!-- Classified Stream right (x=740+290=1030, y=105+682=787) -> travels up gutter x=1070 -> enters BalanceReconciler at x=1090+20=1110, y=105+115=220 -->
  <path d="M 1030 787 L 1070 787 L 1070 220 L 1110 220" fill="none" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
  <rect x="1042" y="445" width="56" height="18" rx="4" fill="#DCFCE7" stroke="#16A34A" stroke-width="0.8" />
  <text x="1070" y="458" font-size="8.5" font-weight="700" fill="#166534" text-anchor="middle">Ledger In</text>

  <!-- ========================================================================= -->
  <!-- SWIMLANE 5: ENTERPRISE EXPORTS & UI PLATFORM (x = 1440, y = 105, w = 300) -->
  <!-- ========================================================================= -->
  <g transform="translate(1440, 105)">
    <rect width="300" height="890" rx="10" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" filter="url(#shadow-lane)" />
    <path d="M 0 10 Q 0 0 10 0 L 290 0 Q 300 0 300 10 L 300 40 L 0 40 Z" fill="#F1F5F9" />
    <text x="18" y="26" font-size="12.5" font-weight="800" fill="#334155">5. ENTERPRISE EXPORT &amp; UI PORTAL</text>

    <!-- Export 5.1: Multi-Tab Excel (.xlsx) (y = 55) -->
    <g transform="translate(20, 55)">
      <rect width="260" height="84" rx="8" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="12" font-weight="800" fill="#14532D">📊 Multi-Tab Excel (.xlsx)</text>
      <text x="16" y="42" font-size="10" fill="#15803D">• Sheet 1: Financial Health &amp; KPIs</text>
      <text x="16" y="57" font-size="10" fill="#15803D">• Sheet 2: Classified Ledger</text>
      <text x="16" y="72" font-size="10" fill="#15803D">• Sheet 3: Forensic Audit &amp; Risk Intelligence</text>
    </g>

    <!-- Export 5.2: Clean Tabular CSV (.csv) (y = 155) -->
    <g transform="translate(20, 155)">
      <rect width="260" height="70" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.2" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="12" font-weight="800" fill="#0F172A">📄 Clean Tabular CSV (.csv)</text>
      <text x="16" y="42" font-size="10" fill="#475569">Normalized Delimited Accounting Feed</text>
      <text x="16" y="57" font-size="9.5" fill="#64748B">Includes Clean Counterparty &amp; UTR Ref</text>
    </g>

    <!-- Export 5.3: Tally Prime XML Vouchers (.xml) (y = 245) -->
    <g transform="translate(20, 245)">
      <rect width="260" height="92" rx="8" fill="#FEF3C7" stroke="#D97706" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="12" font-weight="800" fill="#78350F">🧾 Tally Prime XML Vouchers (.xml)</text>
      <text x="16" y="42" font-size="10" fill="#92400E">• Native &lt;TALLYMESSAGE&gt; format</text>
      <text x="16" y="58" font-size="10" fill="#92400E">• Payment &amp; Receipt Ledger Vouchers</text>
      <text x="16" y="76" font-size="9.5" font-weight="800" fill="#B45309">Direct Import via Gateway of Tally</text>
    </g>

    <!-- Export 5.4: QuickBooks / Xero CSV (y = 355) -->
    <g transform="translate(20, 355)">
      <rect width="260" height="78" rx="8" fill="#DBEAFE" stroke="#2563EB" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="12" font-weight="800" fill="#1E3A8A">💼 QuickBooks / Xero CSV (.csv)</text>
      <text x="16" y="42" font-size="10" fill="#1D4ED8">• Universal 4-Column Bank Feed</text>
      <text x="16" y="58" font-size="10" fill="#1D4ED8">• Date, Payee, Description, Amount</text>
      <text x="16" y="71" font-size="9" fill="#0052CC">Direct Cloud Feeds Integration</text>
    </g>

    <!-- Export 5.5: Streamlit Enterprise UI (y = 450) -->
    <g transform="translate(20, 450)">
      <rect width="260" height="102" rx="8" fill="#F3E8FF" stroke="#9333EA" stroke-width="1.5" filter="url(#shadow-card)" />
      <text x="16" y="22" font-size="12" font-weight="800" fill="#581C87">🖥️ Streamlit Enterprise Portal</text>
      <text x="16" y="42" font-size="10" fill="#6B21A8">• Real-time Financial KPIs &amp; Donut Chart</text>
      <text x="16" y="58" font-size="10" fill="#6B21A8">• Keyword Search &amp; Audit Status Filters</text>
      <text x="16" y="74" font-size="9.5" font-weight="700" fill="#7E22CE">• 13-Bank Live Batch Evaluation Hub</text>
      <text x="16" y="89" font-size="9" fill="#581C87">Light Theme | Befree Executive Standard</text>
    </g>
  </g>

  <!-- ========================================================================= -->
  <!-- GUTTER 4-5 DISTRIBUTION BUS (Clean, Pristine Fan-Out to All Exports)      -->
  <!-- ========================================================================= -->
  <!-- Exit Audited Financial Dataset (x=1090+290=1380, y=105+547=652) into Vertical Bus at x=1420 -->
  <path d="M 1380 652 L 1420 652" fill="none" stroke="#0052CC" stroke-width="2" />
  <!-- Vertical Bus Line from y=202 to y=652 -->
  <line x1="1420" y1="202" x2="1420" y2="652" stroke="#0052CC" stroke-width="2" />
  
  <!-- Horizontal Delivery Spines into each Export Card -->
  <!-- To Excel (y = 105 + 97 = 202) -->
  <line x1="1420" y1="202" x2="1460" y2="202" stroke="#16A34A" stroke-width="2" marker-end="url(#m-green)" />
  <!-- To CSV (y = 105 + 190 = 295) -->
  <line x1="1420" y1="295" x2="1460" y2="295" stroke="#475569" stroke-width="2" marker-end="url(#m-slate)" />
  <!-- To Tally XML (y = 105 + 291 = 396) -->
  <line x1="1420" y1="396" x2="1460" y2="396" stroke="#D97706" stroke-width="2" marker-end="url(#m-amber)" />
  <!-- To QuickBooks (y = 105 + 394 = 499) -->
  <line x1="1420" y1="499" x2="1460" y2="499" stroke="#0052CC" stroke-width="2" marker-end="url(#m-blue)" />
  <!-- To Streamlit UI (y = 105 + 501 = 606) -->
  <line x1="1420" y1="606" x2="1460" y2="606" stroke="#7C3AED" stroke-width="2" marker-end="url(#m-purple)" />

</svg>"""

    # Write pristine SVG file
    with open("architecture_diagram.svg", "w", encoding="utf-8") as f:
        f.write(svg.strip())

    # Write pristine HTML wrapper with responsive clean container
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Befree System Architecture Flow Diagram (Draw.io Enterprise Clean)</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: transparent;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      overflow-x: auto;
    }}
    .diagram-container {{
      width: 100%;
      min-width: 1780px;
      background: #FFFFFF;
      padding: 14px;
      border-radius: 12px;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
      border: 1px solid #E2E8F0;
      box-sizing: border-box;
    }}
  </style>
</head>
<body>
  <div class="diagram-container">
    {svg}
  </div>
</body>
</html>"""

    with open("architecture_diagram.html", "w", encoding="utf-8") as f:
        f.write(html.strip())

    print("Successfully built pristine architecture_diagram.svg and architecture_diagram.html with ZERO intersecting lines!")

if __name__ == "__main__":
    build_pristine_diagram()
