import os
from PIL import Image, ImageDraw, ImageFont


def make_clean_pdf(filename: str, pages_lines: list):
    """
    Constructs a valid, standard multi-page or single-page PDF-1.4 
    with clean linear text streams.
    
    pages_lines: list of list of strings (each inner list is a page)
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    if pages_lines and isinstance(pages_lines[0], str):
        pages_lines = [pages_lines]

    total_pages = len(pages_lines)
    
    # We will build objects dynamically
    # 1 0 obj: Catalog
    # 2 0 obj: Pages parent
    # Font is at 4 0 obj
    page_obj_ids = []
    content_obj_ids = []
    
    curr_id = 5
    for i in range(total_pages):
        page_obj_ids.append(curr_id)
        content_obj_ids.append(curr_id + 1)
        curr_id += 2

    # Build PDF body
    objects = []
    
    # Catalog
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    
    # Pages Root
    kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    obj2 = f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {total_pages} >>\nendobj\n".encode("latin1")
    
    # Shared Font
    obj4 = b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    
    objects.extend([(1, obj1), (2, obj2), (4, obj4)])

    # Add Pages and Content streams
    for i in range(total_pages):
        p_id = page_obj_ids[i]
        c_id = content_obj_ids[i]
        lines = pages_lines[i]

        stream_content = "BT\n/F1 9.5 Tf\n45 745 Td\n14.5 TL\n"
        for line in lines:
            safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            stream_content += f"({safe_line}) ' \n"
        stream_content += "ET\n"
        stream_bytes = stream_content.encode("latin1")

        page_obj = f"{p_id} 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents {c_id} 0 R >>\nendobj\n".encode("latin1")
        content_obj = f"{c_id} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin1") + stream_bytes + b"\nendstream\nendobj\n"

        objects.append((p_id, page_obj))
        objects.append((c_id, content_obj))

    # Sort objects by ID
    objects.sort(key=lambda x: x[0])

    offsets = {}
    body = b"%PDF-1.4\n"
    for o_id, o_bytes in objects:
        offsets[o_id] = len(body)
        body += o_bytes

    max_id = max(offsets.keys())
    xref_offset = len(body)
    xref = f"xref\n0 {max_id + 1}\n0000000000 65535 f \n"
    for idx in range(1, max_id + 1):
        if idx in offsets:
            xref += f"{offsets[idx]:010d} 00000 n \n"
        else:
            xref += "0000000000 00000 f \n"

    trailer = f"trailer\n<< /Size {max_id + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF"

    with open(filename, "wb") as f:
        f.write(body + xref.encode("latin1") + trailer.encode("latin1"))


def make_encrypted_pdf(filename: str, lines: list, password: str = "befree123"):
    """
    Constructs an encrypted PDF-1.4 file using standard 40-bit RC4 encryption
    with password protection.
    """
    import hashlib
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    PADDING = bytes([
        0x28, 0xBF, 0x4E, 0x5E, 0x4E, 0x75, 0x8A, 0x41,
        0x64, 0x00, 0x4E, 0x56, 0xFF, 0xFA, 0x01, 0x08,
        0x2E, 0x2E, 0x00, 0xB6, 0xD0, 0x68, 0x3E, 0x80,
        0x2F, 0x0C, 0xA9, 0xFE, 0x64, 0x53, 0x69, 0x7A
    ])

    def rc4_cipher(key, data):
        S = list(range(256))
        j = 0
        out = bytearray(len(data))
        for i in range(256):
            j = (j + S[i] + key[i % len(key)]) % 256
            S[i], S[j] = S[j], S[i]
        i = j = 0
        for k in range(len(data)):
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out[k] = data[k] ^ S[(S[i] + S[j]) % 256]
        return bytes(out)

    def get_obj_key(base_key, obj_num, gen_num=0):
        k = base_key + obj_num.to_bytes(3, 'little') + gen_num.to_bytes(2, 'little')
        return hashlib.md5(k).digest()[:min(len(base_key)+5, 16)]

    pass_bytes = password.encode('latin1')
    padded_pass = (pass_bytes + PADDING)[:32]
    P_int = -44
    P_bytes = (P_int & 0xFFFFFFFF).to_bytes(4, byteorder='little', signed=False)
    doc_id = b'0123456789abcdef'

    om = hashlib.md5((pass_bytes + PADDING)[:32]).digest()[:5]
    O = rc4_cipher(om, padded_pass)

    m = hashlib.md5()
    m.update(padded_pass)
    m.update(O)
    m.update(P_bytes)
    m.update(doc_id)
    enc_key = m.digest()[:5]
    U = rc4_cipher(enc_key, PADDING)

    stream_content = "BT\n/F1 9.5 Tf\n45 745 Td\n14.5 TL\n"
    for line in lines:
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream_content += f"({safe_line}) ' \n"
    stream_content += "ET\n"
    stream_plain = stream_content.encode("latin1")
    stream_enc = rc4_cipher(get_obj_key(enc_key, 5, 0), stream_plain)

    body = b"%PDF-1.4\n"
    offsets = {}

    def add_obj(num, content):
        nonlocal body
        offsets[num] = len(body)
        body += f"{num} 0 obj\n".encode("latin1") + content + b"\nendobj\n"

    add_obj(1, b"<< /Type /Catalog /Pages 2 0 R >>")
    add_obj(2, b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    add_obj(3, b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>")
    add_obj(4, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    add_obj(5, f"<< /Length {len(stream_enc)} >>\nstream\n".encode("latin1") + stream_enc + b"\nendstream")

    o_hex = O.hex()
    u_hex = U.hex()
    id_hex = doc_id.hex()
    encrypt_dict = f"<< /Filter /Standard /V 1 /R 2 /O <{o_hex}> /U <{u_hex}> /P {P_int} >>".encode("latin1")
    add_obj(6, encrypt_dict)

    xref_pos = len(body)
    body += b"xref\n0 7\n0000000000 65535 f \n"
    for i in range(1, 7):
        body += f"{offsets[i]:010d} 00000 n \n".encode("latin1")

    body += f"trailer\n<< /Size 7 /Root 1 0 R /Encrypt 6 0 R /ID [<{id_hex}> <{id_hex}>] >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin1")

    with open(filename, "wb") as f:
        f.write(body)


def make_scanned_pdf(filename: str, header_lines: list, transaction_lines: list):
    """
    Constructs an authentic image-based/scanned PDF by rasterizing directly onto a PIL canvas.
    Renders high-legibility text using system TrueType fonts, perfectly readable by OCR models
    while containing ZERO embedded text stream.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 1200 x 1650 resolution for crisp OCR fidelity
    img = Image.new("RGB", (1200, 1650), color=(250, 249, 245))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 24)
        font_header = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 18)
        font_table_hdr = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 17)
        font_row = ImageFont.truetype("C:\\Windows\\Fonts\\cour.ttf", 16)  # Courier typewriter/fixed width
    except Exception:
        font_title = ImageFont.load_default()
        font_header = font_title
        font_table_hdr = font_title
        font_row = font_title

    # Bank Title & Header
    curr_y = 60
    if header_lines:
        draw.text((60, curr_y), header_lines[0], fill=(20, 20, 90), font=font_title)
        curr_y += 35

    for line in header_lines[1:]:
        draw.text((60, curr_y), line, fill=(40, 40, 40), font=font_header)
        curr_y += 28

    curr_y += 10
    draw.line([(60, curr_y), (1140, curr_y)], fill=(100, 100, 100), width=2)
    curr_y += 20

    # Table Header
    table_hdr = "Date        Description                              Debit        Credit       Balance"
    draw.text((60, curr_y), table_hdr, fill=(0, 0, 0), font=font_table_hdr)
    curr_y += 26
    draw.line([(60, curr_y), (1140, curr_y)], fill=(140, 140, 140), width=2)
    curr_y += 18

    # Transaction Rows
    for line in transaction_lines:
        draw.text((60, curr_y), line, fill=(30, 30, 30), font=font_row)
        curr_y += 22
        draw.line([(60, curr_y + 8), (1140, curr_y + 8)], fill=(225, 225, 225), width=1)
        curr_y += 26

    # Bank Stamp / Certified Copy Marker
    curr_y += 40
    draw.rectangle([(60, curr_y), (420, curr_y + 70)], outline=(180, 50, 50), width=2)
    draw.text((75, curr_y + 12), "ICICI BANK LIMITED - VERIFIED COPY", fill=(180, 50, 50), font=font_table_hdr)
    draw.text((75, curr_y + 38), "BRANCH OPERATIONS MANAGER • STAMPED", fill=(180, 50, 50), font=font_header)

    draw.text((60, 1550), "[SCANNED PHYSICAL DOCUMENT - AUDIT CERTIFIED TRUE COPY]", fill=(120, 120, 120), font=font_header)
    
    # Save as pure Image PDF
    img.save(filename, "PDF", resolution=150.0)


def generate_all_12_samples():
    print("Generating comprehensive 12-statement multi-bank test suite...")
    os.makedirs("sample_statements", exist_ok=True)

    # -------------------------------------------------------------
    # 1. HDFC Bank (Text-based, multi-line UPI narrations)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/01_hdfc_statement_text.pdf", [
        "HDFC BANK LIMITED",
        "Branch: Koramangala 4th Block, Bengaluru - 560034",
        "ACCOUNT STATEMENT",
        "Customer Name : MR. RAJESH SHARMA",
        "Account Number: 50100492817291",
        "IFSC Code     : HDFC0001234",
        "Statement Period: 01/10/2024 to 31/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE BROUGHT FORWARD                                        50000.00",
        "02/10/2024  UPI/428172901/ZOMATO RESTAURANT              450.00                    49550.00",
        "            BANGALORE IN REF 9028120",
        "05/10/2024  SALARY FOR OCT 2024 INFOSYS TECH                         85000.00     134550.00",
        "            ACH CR CORP PAYROLL SERVICES",
        "07/10/2024  BESCOM ELECTRICITY BILL PAYMENT             2340.00                   132210.00",
        "            BBPS BILLPAY ONL 881920",
        "10/10/2024  BLINKIT QUICK GROCERY ESSENTIALS            1120.00                   131090.00",
        "            ORDER 9928172 GURGAON",
        "12/10/2024  HPCL PETROL PUMP FUEL REFILL                2500.00                   128590.00",
        "            POS 402910 KORAMANGALA",
        "15/10/2024  NETFLIX MONTHLY SUBSCRIPTION                 649.00                   127941.00",
        "            MUSIC & STREAMING ENTERTAINMENT",
        "18/10/2024  ZERODHA BROKING LTD FUNDS TRANSFER         15000.00                   112941.00",
        "            UPI 40918293 EQUITY TRADING",
        "20/10/2024  BAJAJ FINANCE LIMITED AUTO EMI              8450.00                   104491.00",
        "            LOAN INSTALMENT ACH DEBIT",
        "22/10/2024  AMAZON INDIA PAYMENTS RETAIL                3499.00                   100992.00",
        "            ORDER 402-9182736-19283",
        "25/10/2024  APOLLO PHARMACY MEDICINES                    880.00                   100112.00",
        "            HEALTHCARE RETAIL STORE",
        "28/10/2024  CONSOLIDATED SMS ALERTS CHARGES               59.00                   100053.00",
        "            QUARTERLY FEE GST",
        "30/10/2024  AIRTEL BROADBAND FIBERNET BILL              1178.00                    98875.00",
        "            TELECOM RECHARGE BBPS",
        "31/10/2024  INTEREST CREDIT SAVINGS ACCOUNT                            625.00      99500.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 2. State Bank of India (SBI) (Text-based, Txn Date + Value Date)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/02_sbi_statement_text.pdf", [
        "STATE BANK OF INDIA",
        "Branch: Nariman Point, Mumbai - 400021",
        "IFS Code: SBIN0000300 | CIF No: 8819203912",
        "TRANSACTION STATEMENT",
        "Account Name : MS. PRIYA PATEL",
        "Account Number: 20491827361",
        "Statement Period: 01/10/2024 to 28/10/2024",
        "--------------------------------------------------------------------------------",
        "Txn Date    Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE                                                        35000.00",
        "03/10/2024  SWIGGY BANGALORE UPI 429102                  380.00                    34620.00",
        "06/10/2024  SALARY PAYMENT OCTOBER TCS LTD                           65000.00      99620.00",
        "09/10/2024  RELIANCE FRESH GROCERY STORE                1850.00                    97770.00",
        "14/10/2024  UBER RIDES MUMBAI COMMUTE                    420.00                    97350.00",
        "17/10/2024  JIO RECHARGE PREPAID MOBILE                  749.00                    96601.00",
        "21/10/2024  GROWW MUTUAL FUND SIP OCT                   5000.00                    91601.00",
        "24/10/2024  FLIPKART INTERNET ORDER                     2499.00                    89102.00",
        "28/10/2024  MINIMUM BALANCE CHARGES                      150.00                    88952.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 3. ICICI Bank (Scanned / Image PDF)
    # -------------------------------------------------------------
    make_scanned_pdf(
        "sample_statements/03_icici_statement_scanned.pdf",
        [
            "ICICI BANK LIMITED - STATEMENT OF TRANSACTIONS",
            "Branch: Bandra Kurla Complex, Mumbai - 400051",
            "Customer Name: MR. SUNIL VERMA",
            "Account Number: 001201928371 | IFSC: ICIC0000012",
            "Statement Period: 01/10/2024 to 20/10/2024"
        ],
        [
            "01/10/2024    OPENING BALANCE BROUGHT FORWARD                                   42000.00",
            "02/10/2024    UPI 402910 ZOMATO FOOD DELIVERY         420.00                    41580.00",
            "05/10/2024    SALARY CREDITED OCT 2024 TECH CORP                   70000.00     111580.00",
            "08/10/2024    ELECTRICITY BILL POWER CONSUMPTION      1850.00                   109730.00",
            "12/10/2024    BLINKIT GROCERIES ORDER BANGALORE       980.00                    108750.00",
            "15/10/2024    UBER RIDES TAXI CAB COMMUTE             350.00                    108400.00",
            "18/10/2024    AMAZON RETAIL ONLINE PURCHASE           2199.00                   106201.00",
            "20/10/2024    SMS SERVICE AND ALERT CHARGES           35.00                     106166.00"
        ]
    )

    # -------------------------------------------------------------
    # 4. Axis Bank (Text-based, Particulars + Amount Dr/Cr column)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/04_axis_statement_text.pdf", [
        "AXIS BANK LIMITED",
        "Branch: MG Road, Bengaluru - 560001",
        "Customer Name: MR. VIKRAM ADITYA",
        "Account Number: 914010048291028",
        "IFSC Code: UTIB0000014",
        "Statement Period: 01/10/2024 to 25/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Particulars                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE                                                        62000.00",
        "04/10/2024  PAYROLL DIRECT DEP WIPRO LIMITED                         92000.00     154000.00",
        "06/10/2024  SWIGGY FOOD ORDER GURGAON                    520.00                   153480.00",
        "10/10/2024  BESCOM POWER SUPPLY BILL                    3100.00                   150380.00",
        "14/10/2024  BIGBASKET SUPERMARKET ORDER                 2450.00                   147930.00",
        "18/10/2024  OLA CABS AIRPORT RIDE                        680.00                   147250.00",
        "22/10/2024  MYNTRA DESIGNS ONLINE CLOTHING              4200.00                   143050.00",
        "25/10/2024  HDFC HOME LOAN MONTHLY EMI                 18500.00                   124550.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 5. Kotak Mahindra Bank (Text-based, Investment & Wealth Focus)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/05_kotak_statement_text.pdf", [
        "KOTAK MAHINDRA BANK",
        "Branch: Connaught Place, New Delhi - 110001",
        "Account Holder Name: MRS. ANANYA SEN",
        "Account Number: 4810294819",
        "IFSC Code: KKBK0000182",
        "Statement Period: 01/10/2024 to 26/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE BROUGHT FORWARD                                        75000.00",
        "03/10/2024  MONTHLY SALARY CREDIT GOOGLE INDIA                      125000.00     200000.00",
        "06/10/2024  ZERODHA SECURITIES BROKING TRANSFER        25000.00                   175000.00",
        "09/10/2024  GROWW MUTUAL FUNDS SIP EQUITY              15000.00                   160000.00",
        "13/10/2024  STARBUCKS COFFEE CONNAUGHT PLACE             850.00                   159150.00",
        "17/10/2024  NATURES BASKET ORGANIC GROCERIES            3400.00                   155750.00",
        "20/10/2024  CRED CREDIT CARD BILL PAYMENT              14500.00                   141250.00",
        "23/10/2024  APPLE COM BILL ICLOUD STORAGE                219.00                   141031.00",
        "26/10/2024  INTEREST CREDIT SAVINGS ACCOUNT                           1150.00     142181.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 6. Bank of Baroda (Text-based, Public Sector Format)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/06_bank_of_baroda_text.pdf", [
        "BANK OF BARODA",
        "Branch: Alkapuri, Vadodara, Gujarat - 390007",
        "Customer Name : MR. DEEPAK JOSHI",
        "Account Number: 01928374619",
        "IFSC Code: BARB0ALKAPU",
        "Statement Period: 01/10/2024 to 24/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Narration / Particulars                       Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  B/F OPENING BALANCE                                                    28000.00",
        "04/10/2024  MONTHLY PENSION WAGES CREDIT                             48000.00      76000.00",
        "07/10/2024  ELECTRICITY BILL UGVCL PAYMENT              1420.00                    74580.00",
        "11/10/2024  MEDPLUS PHARMACY MEDICINES                   640.00                    73940.00",
        "15/10/2024  LOCAL KIRANA PROVISION STORE                2100.00                    71840.00",
        "19/10/2024  HPCL PETROL PUMP HIGHWAY DIESEL             1200.00                    70640.00",
        "24/10/2024  CHEQUE RETURN PENALTY FEE                    250.00                    70390.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 7. Punjab National Bank (Scanned / Image PDF)
    # -------------------------------------------------------------
    make_scanned_pdf(
        "sample_statements/07_pnb_statement_scanned.pdf",
        [
            "PUNJAB NATIONAL BANK - ACCOUNT STATEMENT",
            "Branch: Sector 17, Chandigarh - 160017",
            "Customer Name: MR. AMANPREET SINGH",
            "Account Number: 1928000192837 | IFSC: PUNB0019200",
            "Statement Period: 01/10/2024 to 22/10/2024"
        ],
        [
            "01/10/2024    OPENING BALANCE                                                   31000.00",
            "03/10/2024    MCDONALDS FAST FOOD MEAL                390.00                    30610.00",
            "05/10/2024    SALARY CREDIT PUNJAB STATE GOVT                      52000.00     82610.00",
            "09/10/2024    DOMINOS PIZZA CHANDIGARH                540.00                    82070.00",
            "14/10/2024    POWER BILL PSPCL ELECTRICITY            1950.00                   80120.00",
            "18/10/2024    DMART SUPERMARKET GROCERIES             3200.00                   76920.00",
            "22/10/2024    ANNUAL DEBIT CARD MAINTENANCE FEE       177.00                    76743.00"
        ]
    )

    # -------------------------------------------------------------
    # 8. Canara Bank (Text-based, Standard Format)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/08_canara_bank_text.pdf", [
        "CANARA BANK",
        "Branch: Town Hall, Bengaluru - 560002",
        "Account Name : MR. KARTHIK SUBRAMANIAM",
        "Account Number: 102918273645",
        "IFSC Code: CNRB0001029",
        "Statement Period: 01/10/2024 to 27/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE                                                        44000.00",
        "05/10/2024  SALARY NEFT CR INFOTECH LTD                              58000.00     102000.00",
        "08/10/2024  ZOMATO RESTAURANT ORDER                      320.00                   101680.00",
        "12/10/2024  COUNTRY DELIGHT MILK DELIVERY               1450.00                   100230.00",
        "16/10/2024  RAPIDO BIKE TAXI COMMUTE                     110.00                   100120.00",
        "20/10/2024  AMAZON PAY INDIA ONLINE                     1890.00                    98230.00",
        "23/10/2024  ACT FIBERNET MONTHLY BROADBAND              1050.00                    97180.00",
        "27/10/2024  MUTUAL FUND SIP DEBIT CAMSONLINE            4000.00                    93180.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 9. IndusInd Bank (Text-based, High-frequency Consumer/UPI)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/09_indusind_statement_text.pdf", [
        "INDUSIND BANK LIMITED",
        "Branch: Cyber City, Gurugram, Haryana - 122002",
        "Account Holder: MS. SANYA MEHTA",
        "Account Number: 159201928371",
        "IFSC Code: INDB0000592",
        "Statement Period: 01/10/2024 to 29/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE BROUGHT FORWARD                                        55000.00",
        "02/10/2024  SWIGGY GOURMET MEAL                          780.00                    54220.00",
        "05/10/2024  MONTHLY SALARY ACCRUAL CONSULTING                       110000.00     164220.00",
        "07/10/2024  ZEPTO 10 MINUTE DELIVERY                     450.00                   163770.00",
        "10/10/2024  UBER PREMIER DELHI NCR                       890.00                   162880.00",
        "14/10/2024  CHAAYOS SNACKS TEA                           240.00                   162640.00",
        "18/10/2024  NYKAA BEAUTY STORE E-RETAIL                 2890.00                   159750.00",
        "22/10/2024  PVR CINEMAS MULTIPLEX TICKETS               1100.00                   158650.00",
        "26/10/2024  DECATHLON SPORTS CLOTHING                   3499.00                   155151.00",
        "29/10/2024  DISNEY HOTSTAR ANNUAL SUBSCRIPTION          1499.00                   153652.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 10. Multi-Page Statement (2 Pages, tests repeated headers)
    # -------------------------------------------------------------
    page1 = [
        "HDFC BANK LIMITED - MULTI-PAGE ACCOUNT STATEMENT",
        "Branch: South Extension, New Delhi - 110049",
        "Customer Name : MR. ARUN VERMA",
        "Account Number: 50100882910293",
        "IFSC Code     : HDFC0000401",
        "Statement Period: 01/10/2024 to 31/10/2024 (Page 1 of 2)",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE BROUGHT FORWARD                                        80000.00",
        "03/10/2024  ZOMATO RESTAURANT DINING                     650.00                    79350.00",
        "05/10/2024  SALARY FOR OCT 2024 GOOGLE CORP                         135000.00     214350.00",
        "08/10/2024  BESCOM POWER SUPPLY BILL                    2850.00                   211500.00",
        "12/10/2024  BLINKIT GROCERY DELIVERY                     920.00                   210580.00",
        "15/10/2024  HPCL FUEL FILL HIGHWAY                      2000.00                   208580.00",
        "--------------------------------------------------------------------------------",
        "[CONTINUED ON PAGE 2 ...]"
    ]
    page2 = [
        "HDFC BANK LIMITED - STATEMENT OF ACCOUNT (PAGE 2 OF 2)",
        "Account Number: 50100882910293 | IFSC: HDFC0000401",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "18/10/2024  ZERODHA BROKING TRADING FUNDS              20000.00                   188580.00",
        "22/10/2024  BAJAJ FINANCE LIMITED AUTO EMI              9500.00                   179080.00",
        "25/10/2024  AMAZON ONLINE RETAIL STORE                  4500.00                   174580.00",
        "28/10/2024  APOLLO PHARMACY HEALTHCARE                   850.00                   173730.00",
        "31/10/2024  INTEREST CREDIT SAVINGS ACCOUNT                           1250.00     174980.00",
        "--------------------------------------------------------------------------------",
        "* END OF STATEMENT - GENERATED BY HDFC BANK LTD *"
    ]
    make_clean_pdf("sample_statements/10_multipage_statement_text.pdf", [page1, page2])

    # -------------------------------------------------------------
    # 11. Corporate Payroll / Business Statement
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/11_corporate_business_statement.pdf", [
        "ICICI BANK CURRENT ACCOUNT STATEMENT",
        "Branch: BKC Treasury, Mumbai - 400051",
        "Customer Name: TECHNOVATE SOLUTIONS PRIVATE LIMITED",
        "Account Number: 000405019283",
        "IFSC Code: ICIC0000004",
        "Account Type: Current Account",
        "Statement Period: 01/10/2024 to 30/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE BROUGHT FORWARD                                       450000.00",
        "04/10/2024  CLIENT INVOICE PAYMENT RECEIVED TCS                     380000.00     830000.00",
        "05/10/2024  BULK PAYROLL SALARY DISBURSEMENT          240000.00                   590000.00",
        "10/10/2024  GST TAX PAYMENT GOVERNMENT OF INDIA        45000.00                   545000.00",
        "15/10/2024  OFFICE BROADBAND TATA COMMUNICATIONS        8500.00                   536500.00",
        "20/10/2024  AWS CLOUD SERVICES SERVER HOSTING          32000.00                   504500.00",
        "25/10/2024  OFFICE LEASE RENT PAYMENT DLF              65000.00                   439500.00",
        "30/10/2024  ANNUAL CURRENT ACCOUNT MAINTENANCE          2500.00                   437000.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 12. Statement with Math Discrepancy (Tests Validator)
    # -------------------------------------------------------------
    make_clean_pdf("sample_statements/12_discrepancy_audit_statement.pdf", [
        "STATE BANK OF INDIA - AUDIT TEST STATEMENT",
        "Branch: Parliament Street, New Delhi - 110001",
        "Account Name : MR. SURESH MENON",
        "Account Number: 30192837461",
        "IFSC Code: SBIN0000691",
        "Statement Period: 01/10/2024 to 20/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE                                                        50000.00",
        "05/10/2024  SALARY PAYMENT OCTOBER TCS LTD                           60000.00     110000.00",
        "10/10/2024  SWIGGY FOOD ORDER GURGAON                    500.00                   109500.00",
        "15/10/2024  SIMULATED OCR DISCREPANCY AMOUNT            2000.00                    99500.00",
        "18/10/2024  AIRTEL MOBILE POSTPAID RECHARGE              799.00                    98701.00",
        "--------------------------------------------------------------------------------"
    ])

    # -------------------------------------------------------------
    # 13. Encrypted Statement (Password: befree123)
    # -------------------------------------------------------------
    make_encrypted_pdf("sample_statements/13_password_protected_statement.pdf", [
        "HDFC BANK - ENCRYPTED CLIENT STATEMENT",
        "Branch: Connaught Place, New Delhi - 110001",
        "Customer Name: MR. VIKRAM MALHOTRA",
        "Account Number: 50100492817263",
        "IFSC Code: HDFC0000003",
        "Account Type: Premium Savings Account",
        "Statement Period: 01/10/2024 to 28/10/2024",
        "--------------------------------------------------------------------------------",
        "Date        Description                                   Debit       Credit       Balance",
        "--------------------------------------------------------------------------------",
        "01/10/2024  OPENING BALANCE BROUGHT FORWARD                                       125000.00",
        "05/10/2024  SALARY CREDIT FROM GOOGLE INDIA                         195000.00     320000.00",
        "08/10/2024  STARBUCKS COFFEE CONNAUGHT PLACE             650.00                   319350.00",
        "12/10/2024  AMAZON INDIA SHOPPING ELECTRONICS           4500.00                   314850.00",
        "15/10/2024  TDS DEDUCTION ON FIXED DEPOSIT              1200.00                   313650.00",
        "20/10/2024  MUTUAL FUND SIP KFINTECH HDFC TOP 100      15000.00                   298650.00",
        "28/10/2024  UBER RIDE TRAVEL TO AIRPORT                  820.00                   297830.00",
        "--------------------------------------------------------------------------------"
    ], password="befree123")

    print("All 13 Statements successfully generated in sample_statements/ folder!")


if __name__ == "__main__":
    generate_all_12_samples()
