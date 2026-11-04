import os

def create_clean_drawio():
    xml_content = """<mxfile host="app.diagrams.net" modified="2026-11-04T23:25:00.000Z" agent="Befree Architecture" version="24.0.0" type="device">
  <diagram id="befree-arch-flow" name="Befree Architecture Flow">
    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1780" pageHeight="1020" background="#F8FAFC" math="0" shadow="1">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- TOP TITLE BANNER -->
        <mxCell id="title_banner" value="&lt;b style='font-size:20px;color:#0F172A;'&gt;befree. | Enterprise Bank Statement Processing &amp;amp; Classification Platform&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:12px;color:#64748B;'&gt;Autonomous Multi-Bank Ingestion, Non-LLM Hybrid Classification, Forensic Audit &amp;amp; Enterprise Export Pipeline&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;arcSize=6;align=center;verticalAlign=middle;" vertex="1" parent="1">
          <mxGeometry x="40" y="20" width="1700" height="66" as="geometry" />
        </mxCell>

        <!-- ================= LAYER 1: INGESTION ================= -->
        <mxCell id="group_ingestion" value="1. INGESTION &amp; SECURITY LAYER" style="swimlane;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;fontStyle=1;fontSize=12;fontColor=#1E40AF;startSize=30;rounded=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="40" y="105" width="310" height="890" as="geometry" />
        </mxCell>

        <mxCell id="input_pdf" value="&lt;b&gt;📄 Bank Statement (PDF)&lt;/b&gt;&lt;br&gt;Multi-Bank PDFs (Digital / Scanned)&lt;br&gt;&lt;i style='font-size:9.5px;color:#64748B;'&gt;HDFC, SBI, ICICI, Axis, Kotak, BoB, etc.&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=11;fontColor:#0F172A;" vertex="1" parent="group_ingestion">
          <mxGeometry x="20" y="55" width="270" height="68" as="geometry" />
        </mxCell>

        <mxCell id="pwd_check" value="&lt;b&gt;🔒 Password Decryption Engine&lt;/b&gt;&lt;br&gt;In-Memory Decryption (Zero Disk Footprint)&lt;br&gt;&lt;span style='font-size:9.5px;color:#059669;'&gt;• Handles Encrypted PDFs (e.g. befree123)&lt;/span&gt;&lt;br&gt;&lt;i style='font-size:9px;color:#64748B;'&gt;Zero Temporary File Leaks&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=11;fontColor:#0F172A;" vertex="1" parent="group_ingestion">
          <mxGeometry x="20" y="150" width="270" height="74" as="geometry" />
        </mxCell>

        <mxCell id="detector" value="&lt;b style='font-size:10px;color:#1E40AF;'&gt;src/detector.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#0052CC;font-size:12px;'&gt;PDFTypeDetector&lt;/b&gt;&lt;br&gt;&amp;bull; Glyph Stream Density Analysis&lt;br&gt;&lt;b style='font-size:9.5px;color:#1D4ED8;'&gt;Evaluates Char Density per Page&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=#3B82F6;shadow=1;fontSize=11;fontColor:#1E3A8A;" vertex="1" parent="group_ingestion">
          <mxGeometry x="20" y="250" width="270" height="84" as="geometry" />
        </mxCell>

        <mxCell id="route_decision" value="&lt;b&gt;Chars &amp;ge; 50?&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:9px;color:#854D0E;'&gt;(Per Page)&lt;/span&gt;" style="rhombus;whiteSpace=wrap;html=1;fillColor=#FEF08A;strokeColor=#CA8A04;fontStyle=1;fontSize=11;fontColor:#854D0E;" vertex="1" parent="group_ingestion">
          <mxGeometry x="75" y="365" width="160" height="64" as="geometry" />
        </mxCell>

        <mxCell id="text_stream_card" value="&lt;b&gt;Vector Stream&lt;/b&gt;&lt;br&gt;Digital Font Layer&lt;br&gt;&lt;b style='font-size:9px;color:#166534;'&gt;&amp;lt; 100ms Latency&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;fontSize=10.5;fontColor:#14532D;" vertex="1" parent="group_ingestion">
          <mxGeometry x="20" y="475" width="125" height="66" as="geometry" />
        </mxCell>

        <mxCell id="ocr_stream_card" value="&lt;b&gt;Raster Image&lt;/b&gt;&lt;br&gt;Scanned Bitmap&lt;br&gt;&lt;b style='font-size:9px;color:#9A3412;'&gt;Computer Vision&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFEDD5;strokeColor=#EA580C;fontSize=10.5;fontColor:#7C2D12;" vertex="1" parent="group_ingestion">
          <mxGeometry x="165" y="475" width="125" height="66" as="geometry" />
        </mxCell>

        <!-- ================= LAYER 2: EXTRACTION ================= -->
        <mxCell id="group_extraction" value="2. DUAL EXTRACTION &amp; STITCHING" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F0FDF4;strokeColor=#22C55E;fontStyle=1;fontSize=12;fontColor=#166534;startSize=30;rounded=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="390" y="105" width="310" height="890" as="geometry" />
        </mxCell>

        <mxCell id="meta_parser" value="&lt;b style='font-size:10px;color:#0369A1;'&gt;src/extractor/metadata_parser.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#0F172A;font-size:12px;'&gt;MetadataParser&lt;/b&gt;&lt;br&gt;&amp;bull; Name, Account Number, IFSC Code&lt;br&gt;&amp;bull; Bank Identifier &amp;amp; Statement Period" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0F9FF;strokeColor=#0284C7;shadow=1;fontSize=10.5;fontColor:#0F172A;" vertex="1" parent="group_extraction">
          <mxGeometry x="20" y="55" width="270" height="74" as="geometry" />
        </mxCell>

        <mxCell id="text_ext" value="&lt;b style='font-size:10px;color:#15803D;'&gt;src/extractor/text_extractor.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#0F172A;font-size:12px;'&gt;TextBasedExtractor&lt;/b&gt;&lt;br&gt;&amp;bull; Dynamic Column Synonym Grid&lt;br&gt;&amp;bull; Layout-Agnostic Coordinate Grid&lt;br&gt;&lt;b style='color:#166534;font-size:9.5px;'&gt;Powered by pdfplumber&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=10.5;fontColor:#0F172A;" vertex="1" parent="group_extraction">
          <mxGeometry x="20" y="155" width="240" height="90" as="geometry" />
        </mxCell>

        <mxCell id="ocr_ext" value="&lt;b style='font-size:10px;color:#C2410C;'&gt;src/extractor/ocr_extractor.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#0F172A;font-size:12px;'&gt;OCRExtractor (EasyOCR)&lt;/b&gt;&lt;br&gt;&amp;bull; CRAFT Deep Neural Network&lt;br&gt;&amp;bull; Bounding Box Cluster (&amp;Delta;y &amp;le; 8px)&lt;br&gt;&lt;b style='color:#166534;font-size:9.5px;'&gt;&amp;check; Zero External C++ Binaries&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=10.5;fontColor:#0F172A;" vertex="1" parent="group_extraction">
          <mxGeometry x="20" y="275" width="240" height="98" as="geometry" />
        </mxCell>

        <mxCell id="stitcher" value="&lt;b style='font-size:10px;color:#166534;'&gt;src/extractor/row_stitcher.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#064E3B;font-size:12px;'&gt;RowStitcher (State Machine)&lt;/b&gt;&lt;br&gt;&amp;bull; Merges Wrapped Multi-Line Remarks&lt;br&gt;&amp;bull; Anchors: Date Token + Trailing Balance&lt;br&gt;&amp;bull; Currency Cleaning: &amp;quot;&amp;#8377;1,25,000&amp;quot; &amp;rarr; 125000" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;shadow=1;fontSize=10.5;fontColor:#064E3B;" vertex="1" parent="group_extraction">
          <mxGeometry x="20" y="415" width="270" height="110" as="geometry" />
        </mxCell>

        <mxCell id="normalizer" value="&lt;b style='font-size:10px;color:#1D4ED8;'&gt;src/extractor/entity_normalizer.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#1E3A8A;font-size:12px;'&gt;EntityNormalizer&lt;/b&gt;&lt;br&gt;&amp;bull; Clean Counterparty / Vendor Name&lt;br&gt;&amp;bull; Payment Channel (UPI, NEFT, POS)&lt;br&gt;&amp;bull; Reference UTR / Transaction ID" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#2563EB;shadow=1;fontSize=10.5;fontColor:#1E3A8A;" vertex="1" parent="group_extraction">
          <mxGeometry x="20" y="565" width="270" height="98" as="geometry" />
        </mxCell>

        <!-- ================= LAYER 3: CLASSIFICATION ================= -->
        <mxCell id="group_classification" value="3. NON-LLM CLASSIFICATION ENGINE" style="swimlane;whiteSpace=wrap;html=1;fillColor=#FFFBEB;strokeColor=#F59E0B;fontStyle=1;fontSize=12;fontColor=#B45309;startSize=30;rounded=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="740" y="105" width="310" height="890" as="geometry" />
        </mxCell>

        <mxCell id="hybrid_hub" value="&lt;b style='font-size:10px;color:#92400E;'&gt;src/classifier/hybrid_classifier.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#78350F;font-size:12px;'&gt;HybridTransactionClassifier&lt;/b&gt;&lt;br&gt;Two-Tier Priority Arbitrator (Zero-LLM)&lt;br&gt;&lt;b style='color:#B45309;font-size:9px;'&gt;Sub-2ms Latency | Zero Cloud API Cost&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#D97706;shadow=1;fontSize=10.5;fontColor:#78350F;" vertex="1" parent="group_classification">
          <mxGeometry x="20" y="55" width="270" height="82" as="geometry" />
        </mxCell>

        <mxCell id="tier1_rules" value="&lt;b&gt;TIER 1: DOMAIN RULES ENGINE&lt;/b&gt;&lt;br&gt;&lt;b style='color:#475569;font-size:10px;'&gt;src/classifier/rules_engine.py&lt;/b&gt;&lt;br&gt;&amp;bull; 100+ Compiled Regex Signatures&lt;br&gt;&amp;bull; UPI, NEFT, IMPS, RTGS, Payroll&lt;br&gt;&amp;bull; Food, Groceries, EMI, Utilities, Tax&lt;br&gt;&lt;b style='color:#166534;font-size:9.5px;'&gt;Precision: 99.8% | Conf: 0.95 - 0.99&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=10.5;fontColor:#0F172A;" vertex="1" parent="group_classification">
          <mxGeometry x="20" y="165" width="270" height="115" as="geometry" />
        </mxCell>

        <mxCell id="rule_match_dec" value="&lt;b&gt;Rule Match?&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:9px;color:#854D0E;'&gt;(Anchor Regex)&lt;/span&gt;" style="rhombus;whiteSpace=wrap;html=1;fillColor=#FEF08A;strokeColor=#CA8A04;fontStyle=1;fontSize=11;fontColor:#854D0E;" vertex="1" parent="group_classification">
          <mxGeometry x="75" y="310" width="160" height="60" as="geometry" />
        </mxCell>

        <mxCell id="tier2_ml" value="&lt;b&gt;TIER 2: SCIKIT-LEARN ML MODEL&lt;/b&gt;&lt;br&gt;&lt;b style='color:#475569;font-size:10px;'&gt;src/classifier/ml_engine.py&lt;/b&gt;&lt;br&gt;&amp;bull; Sublinear TF-IDF (1-2 N-grams)&lt;br&gt;&amp;bull; Multinomial Logistic Regression&lt;br&gt;&amp;bull; Latency: &amp;lt; 2ms per transaction&lt;br&gt;&lt;b style='color:#166534;font-size:10px;'&gt;&amp;check; Verified Test Accuracy: 98.14%&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=10.5;fontColor:#0F172A;" vertex="1" parent="group_classification">
          <mxGeometry x="20" y="405" width="270" height="115" as="geometry" />
        </mxCell>

        <mxCell id="prob_scoring" value="&lt;b&gt;Probability Calibration Gate&lt;/b&gt;&lt;br&gt;Prob &amp;ge; 0.40 &amp;rarr; Assign Top Category&lt;br&gt;Prob &amp;lt; 0.40 &amp;rarr; Others / Misc Fallback" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#F59E0B;fontSize=10.5;fontColor:#78350F;" vertex="1" parent="group_classification">
          <mxGeometry x="20" y="545" width="270" height="74" as="geometry" />
        </mxCell>

        <mxCell id="classified_stream" value="&lt;b&gt;&amp;check; Unified Classified Ledger Feed&lt;/b&gt;&lt;br&gt;Category + Calibrated Confidence Score&lt;br&gt;&lt;b style='color:#047857;font-size:9.5px;'&gt;Origin Tier Tag (Rule vs Scikit-Learn)&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#059669;fontSize=10.5;fontColor:#064E3B;shadow=1;" vertex="1" parent="group_classification">
          <mxGeometry x="20" y="645" width="270" height="74" as="geometry" />
        </mxCell>

        <!-- ================= LAYER 4: VALIDATION & AUDIT ================= -->
        <mxCell id="group_validation" value="4. VALIDATION &amp; FORENSIC AUDIT" style="swimlane;whiteSpace=wrap;html=1;fillColor=#FEF2F2;strokeColor=#EF4444;fontStyle=1;fontSize=12;fontColor=#991B1B;startSize=30;rounded=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="1090" y="105" width="310" height="890" as="geometry" />
        </mxCell>

        <mxCell id="reconciler" value="&lt;b style='font-size:10px;color:#991B1B;'&gt;src/validator/balance_reconciler.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#7F1D1D;font-size:12px;'&gt;BalanceReconciler&lt;/b&gt;&lt;br&gt;&lt;b style='color:#0F172A;font-size:11.5px;'&gt;Bal[i] = Bal[i-1] - Dr[i] + Cr[i]&lt;/b&gt;&lt;br&gt;&amp;bull; Mathematical Precision: &amp;plusmn;0.05&lt;br&gt;&amp;bull; Inverted Dr/Cr Column Detector&lt;br&gt;&lt;b style='color:#991B1B;font-size:10px;'&gt;Integrity Score &amp;amp; Discrepancy Flags&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEE2E2;strokeColor=#DC2626;shadow=1;fontSize=10.5;fontColor:#7F1D1D;" vertex="1" parent="group_validation">
          <mxGeometry x="20" y="55" width="270" height="120" as="geometry" />
        </mxCell>

        <mxCell id="anomaly_detector" value="&lt;b style='font-size:10px;color:#B91C1C;'&gt;src/validator/anomaly_detector.py&lt;/b&gt;&lt;br&gt;&lt;b style='color:#0F172A;font-size:12px;'&gt;ForensicAnomalyDetector&lt;/b&gt;&lt;br&gt;&amp;bull; Duplicate Payments: Double Swipes&lt;br&gt;&amp;bull; Statistical Outliers: Spikes &amp;gt; 2.5&amp;sigma;&lt;br&gt;&amp;bull; AML Structuring Check (&amp;lt; &amp;#8377;50k)&lt;br&gt;&amp;bull; Statutory Tax: TDS / GST / Challan 280&lt;br&gt;&lt;b style='color:#DC2626;font-size:11px;'&gt;Risk Profile: CLEAN / MEDIUM / HIGH&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;shadow=1;fontSize=10.5;fontColor:#0F172A;" vertex="1" parent="group_validation">
          <mxGeometry x="20" y="205" width="270" height="145" as="geometry" />
        </mxCell>

        <mxCell id="hitl_override" value="&lt;b&gt;HUMAN-IN-THE-LOOP (HITL)&lt;/b&gt;&lt;br&gt;&lt;b style='color:#1E3A8A;font-size:12px;'&gt;Interactive Override Editor&lt;/b&gt;&lt;br&gt;&amp;bull; Accountant Manual Re-Classification&lt;br&gt;&amp;bull; Dynamic Ledger &amp;amp; KPI Recalculation&lt;br&gt;&lt;b style='font-size:9px;color:#0052CC;'&gt;Custom Rule Learning Engine&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;shadow=1;fontSize=10.5;fontColor:#1E3A8A;" vertex="1" parent="group_validation">
          <mxGeometry x="20" y="380" width="270" height="98" as="geometry" />
        </mxCell>

        <mxCell id="audited_dataset" value="&lt;b&gt;&amp;check; Fully Audited Financial Dataset&lt;/b&gt;&lt;br&gt;Reconciled &amp;bull; Fraud Audited &amp;bull; Tax Flagged&lt;br&gt;&lt;b style='color:#166534;font-size:9.5px;'&gt;Downstream Multi-Format Export Ready&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;fontSize=10.5;fontColor:#14532D;shadow=1;" vertex="1" parent="group_validation">
          <mxGeometry x="20" y="510" width="270" height="74" as="geometry" />
        </mxCell>

        <!-- ================= LAYER 5: EXPORTS ================= -->
        <mxCell id="group_export" value="5. ENTERPRISE EXPORT &amp; UI PORTAL" style="swimlane;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#CBD5E1;fontStyle=1;fontSize=12;fontColor=#334155;startSize=30;rounded=1;arcSize=6;" vertex="1" parent="1">
          <mxGeometry x="1440" y="105" width="300" height="890" as="geometry" />
        </mxCell>

        <mxCell id="exp_excel" value="&lt;b&gt;📊 Multi-Tab Excel (.xlsx)&lt;/b&gt;&lt;br&gt;&amp;bull; Sheet 1: Financial Health &amp;amp; KPIs&lt;br&gt;&amp;bull; Sheet 2: Classified Ledger&lt;br&gt;&amp;bull; Sheet 3: Forensic Audit &amp;amp; Risk" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCFCE7;strokeColor=#16A34A;fontSize=11;fontColor:#14532D;shadow=1;" vertex="1" parent="group_export">
          <mxGeometry x="20" y="55" width="260" height="84" as="geometry" />
        </mxCell>

        <mxCell id="exp_csv" value="&lt;b&gt;📄 Clean Tabular CSV (.csv)&lt;/b&gt;&lt;br&gt;Normalized Delimited Accounting Feed&lt;br&gt;&lt;i style='font-size:9.5px;color:#64748B;'&gt;Includes Clean Counterparty &amp;amp; UTR Ref&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#CBD5E1;fontSize=11;fontColor:#0F172A;shadow=1;" vertex="1" parent="group_export">
          <mxGeometry x="20" y="155" width="260" height="70" as="geometry" />
        </mxCell>

        <mxCell id="exp_tally" value="&lt;b&gt;🧾 Tally Prime XML Vouchers (.xml)&lt;/b&gt;&lt;br&gt;&amp;bull; Native &amp;lt;TALLYMESSAGE&amp;gt; format&lt;br&gt;&amp;bull; Payment &amp;amp; Receipt Ledger Vouchers&lt;br&gt;&lt;b style='color:#B45309;font-size:9.5px;'&gt;Direct Import via Gateway of Tally&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEF3C7;strokeColor=#D97706;fontSize=11;fontColor:#78350F;shadow=1;" vertex="1" parent="group_export">
          <mxGeometry x="20" y="245" width="260" height="92" as="geometry" />
        </mxCell>

        <mxCell id="exp_qb" value="&lt;b&gt;💼 QuickBooks / Xero CSV (.csv)&lt;/b&gt;&lt;br&gt;&amp;bull; Universal 4-Column Bank Feed&lt;br&gt;&amp;bull; Date, Payee, Description, Amount&lt;br&gt;&lt;span style='font-size:9px;color:#0052CC;'&gt;Direct Cloud Feeds Integration&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=#2563EB;fontSize=11;fontColor:#1E3A8A;shadow=1;" vertex="1" parent="group_export">
          <mxGeometry x="20" y="355" width="260" height="78" as="geometry" />
        </mxCell>

        <mxCell id="ui_portal" value="&lt;b&gt;🖥️ Streamlit Enterprise Portal&lt;/b&gt;&lt;br&gt;&amp;bull; Real-time Financial KPIs &amp;amp; Donut Chart&lt;br&gt;&amp;bull; Keyword Search &amp;amp; Audit Status Filters&lt;br&gt;&lt;b style='color:#7E22CE;font-size:9.5px;'&gt;&amp;bull; 13-Bank Live Batch Evaluation Hub&lt;/b&gt;&lt;br&gt;&lt;i style='font-size:9px;color:#581C87;'&gt;Light Theme | Befree Executive Standard&lt;/i&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E8FF;strokeColor=#9333EA;fontSize=11;fontColor:#581C87;shadow=1;" vertex="1" parent="group_export">
          <mxGeometry x="20" y="450" width="260" height="102" as="geometry" />
        </mxCell>

        <!-- ================= COLLISION-FREE CONNECTOR CHANNELS ================= -->
        <!-- Lane 1 Internal -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0052CC;strokeWidth=2;" edge="1" parent="1" source="input_pdf" target="pwd_check">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0052CC;strokeWidth=2;" edge="1" parent="1" source="pwd_check" target="detector">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0052CC;strokeWidth=2;" edge="1" parent="1" source="detector" target="route_decision">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e4" value="YES" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;fontColor=#16A34A;fontStyle=1;" edge="1" parent="1" source="route_decision" target="text_stream_card">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e5" value="NO" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;fontColor=#EA580C;fontStyle=1;" edge="1" parent="1" source="route_decision" target="ocr_stream_card">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Lane 1 to Lane 2 via Gutter 1-2 -->
        <mxCell id="e6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;" edge="1" parent="1" source="text_stream_card" target="text_ext">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="122" y="675" />
              <mxPoint x="365" y="675" />
              <mxPoint x="365" y="305" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;" edge="1" parent="1" source="ocr_stream_card" target="ocr_ext">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="267" y="660" />
              <mxPoint x="378" y="660" />
              <mxPoint x="378" y="430" />
            </Array>
          </mxGeometry>
        </mxCell>

        <!-- Lane 2 Internal (Text Extractor cleanly bypasses OCRExtractor on the right side) -->
        <mxCell id="e8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;" edge="1" parent="1" source="text_ext" target="stitcher">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="665" y="305" />
              <mxPoint x="665" y="500" />
              <mxPoint x="615" y="500" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e9" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#EA580C;strokeWidth=2;" edge="1" parent="1" source="ocr_ext" target="stitcher">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e10" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;" edge="1" parent="1" source="stitcher" target="normalizer">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Lane 2 to Lane 3 via Gutter 2-3 -->
        <mxCell id="e11" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0052CC;strokeWidth=2;" edge="1" parent="1" source="normalizer" target="hybrid_hub">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="680" y="719" />
              <mxPoint x="720" y="719" />
              <mxPoint x="720" y="201" />
            </Array>
          </mxGeometry>
        </mxCell>

        <!-- Lane 3 Internal -->
        <mxCell id="e12" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;" edge="1" parent="1" source="hybrid_hub" target="tier1_rules">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e13" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;" edge="1" parent="1" source="tier1_rules" target="rule_match_dec">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e14" value="NO (Fallback)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#B45309;strokeWidth=2;fontColor=#B45309;fontStyle=1;" edge="1" parent="1" source="rule_match_dec" target="tier2_ml">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <!-- Rule Match YES bypasses ML model down dedicated right channel into classified_stream -->
        <mxCell id="e15" value="YES (Rule Match)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;fontColor=#16A34A;fontStyle=1;" edge="1" parent="1" source="rule_match_dec" target="classified_stream">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1020" y="445" />
              <mxPoint x="1020" y="787" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e16" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;" edge="1" parent="1" source="tier2_ml" target="prob_scoring">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e17" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;" edge="1" parent="1" source="prob_scoring" target="classified_stream">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Lane 3 to Lane 4 via Gutter 3-4 -->
        <mxCell id="e18" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;" edge="1" parent="1" source="classified_stream" target="reconciler">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1030" y="787" />
              <mxPoint x="1070" y="787" />
              <mxPoint x="1070" y="220" />
            </Array>
          </mxGeometry>
        </mxCell>

        <!-- Lane 4 Internal Clean Waterfall -->
        <mxCell id="e19" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DC2626;strokeWidth=2;" edge="1" parent="1" source="reconciler" target="anomaly_detector">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e20" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#3B82F6;strokeWidth=2;" edge="1" parent="1" source="anomaly_detector" target="hitl_override">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="e21" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;" edge="1" parent="1" source="hitl_override" target="audited_dataset">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- Lane 4 to Lane 5 Clean Vertical Bus Fan-Out -->
        <mxCell id="e22" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#16A34A;strokeWidth=2;" edge="1" parent="1" source="audited_dataset" target="exp_excel">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1420" y="652" />
              <mxPoint x="1420" y="202" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e23" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#475569;strokeWidth=2;" edge="1" parent="1" source="audited_dataset" target="exp_csv">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1420" y="652" />
              <mxPoint x="1420" y="295" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e24" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#D97706;strokeWidth=2;" edge="1" parent="1" source="audited_dataset" target="exp_tally">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1420" y="652" />
              <mxPoint x="1420" y="396" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e25" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#0052CC;strokeWidth=2;" edge="1" parent="1" source="audited_dataset" target="exp_qb">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1420" y="652" />
              <mxPoint x="1420" y="499" />
            </Array>
          </mxGeometry>
        </mxCell>
        <mxCell id="e26" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#7C3AED;strokeWidth=2;" edge="1" parent="1" source="audited_dataset" target="ui_portal">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="1420" y="652" />
              <mxPoint x="1420" y="606" />
            </Array>
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    with open("architecture_diagram.drawio", "w", encoding="utf-8") as f:
        f.write(xml_content.strip())
    print("Regenerated clean architecture_diagram.drawio successfully!")

if __name__ == "__main__":
    create_clean_drawio()
