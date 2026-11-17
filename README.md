# 🥷 แฮ็กเกอร์ฝ่ายร้าย (Evil Hacker Engine)
> **Autonomous Automation & Study Hours Accumulator Engine for Speexx & Cambridge One**  
> ขับเคลื่อนระบบอัตโนมัติความเร็วสูง ควบคุมผ่าน Safari & AppleScript Engine บน macOS

---

## 📌 ภาพรวมโครงการ (Overview)

**แฮ็กเกอร์ฝ่ายร้าย (Evil Hacker)** เป็นชุดสคริปต์อัตโนมัติ (Autonomous Bot & Solver Engine) ที่ออกแบบมาเพื่อช่วยทำการเรียนและแบบฝึกหัดภาษาอังกฤษออนไลน์บนแพลตฟอร์ม **Speexx** และ **Cambridge One** อย่างมีประสิทธิภาพ แม่นยำ และปลอดภัยสูงสุด

---

## ⚡ จุดเด่นและความสามารถ (Key Features)

### 1. 📘 Speexx Autonomous Master Bot (`speexx_bot.py`)
- **แก้โจทย์ถูกต้อง 100% ทุกรูปแบบ:**
  - ✍️ `ANSWER`: เติมคำตอบลงในช่องว่างจาก Payload โดยตรง
  - 🔄 `TOGGLE_SOLUTION`: สลับคำตอบตัวเลือกที่ถูกต้อง
  - 🎯 `SINGLE_CHOICE / MULTIPLE_CHOICE`: เลือกคำตอบปรนัยและภาพถูกต้องแม่นยำ
  - 🖍️ `MARK_TEXT`: มาร์กคำศัพท์และกริยาถูกต้องทุกตำแหน่ง
  - 🔤 `SCRAMBLED_SENTENCE`: จัดเรียงประโยคที่สลับคำให้ถูกต้อง 100%
  - 📊 `SCRAMBLED_TABLE`: สลับช่องตารางข้อมูลถูกต้องสมบูรณ์
  - 🧩 `DRAG_DROP`: ลากวางคำศัพท์และรูปภาพลงกล่องอย่างรวดเร็ว
  - 🗣️ `PRONUNCIATION`: ข้ามพาร์ตออกเสียงอัตโนมัติเพื่อความลื่นไหล
- **⏱️ ระบบสะสมชั่วโมงเรียน (Study Hours Accumulator):**
  - ตั้งเวลาเป้าหมายได้ตามต้องการ (เช่น สะสมให้ครบ 10 ชั่วโมงตามเกณฑ์อาจารย์)
  - มีระบบ Keep-Alive Pulse คอยขยับหน้าจอเบาๆ เพื่อป้องกัน Session Timeout และให้อาจารย์เช็กสถิติหลังบ้านเห็นเวลาเรียนต่อเนื่องอย่างเป็นธรรมชาติ
- **🏆 Auto CEFR Level Test:**
  - ทำข้อสอบวัดระดับท้ายบท (20 ข้อ) อัตโนมัติ 100/100 ปลดล็อกวุฒิบัตร (Certificate) ทันที
- **🔄 Auto-Reset & Zero Loops:**
  - หากข้อไหนได้คะแนนไม่เต็ม ระบบจะรีเซ็ตและทำซ้ำจนกว่าจะได้ 100% เต็มทุกข้อ

---

### 2. 💻 Cambridge One Universal Solver (`cambridge_bot.py`)
- **รองรับทุกหลักสูตรในเครือ Cambridge:**
  - Cambridge One, Touchstone, Empower ทุก Unit
- **ดึงคำตอบจาก Data Payload โดยตรง:**
  - แมตช์ข้อสอบและคำตอบจาก XML ภายในหน้าเว็บ ทำให้ได้คะแนน 100% เต็ม
  - รองรับทั้งแบบจัดเรียงคำลงกล่อง (Gap Match / Word Order) และเลือกตอบ (Radio / Checkbox)
- **🚀 Auto Next Activity:**
  - ตรวจเสร็จแล้วกดข้ามไปข้อถัดไปและขึ้น Unit ถัดไปอัตโนมัติทันที

---

### 3. 📋 Cambridge One Answer Extractor (`dump_all_answers.py`)
- เครื่องมือดึงเฉลยข้อสอบทั้งหมดในแบบฝึกหัดออกมาแสดงผลใน Terminal เพื่อการตรวจสอบล่วงหน้า

---

## 🛠️ ความต้องการของระบบ (Prerequisites)

1. ระบบปฏิบัติการ **macOS** (รองรับทั้ง Apple Silicon M1/M2/M3/M4 และ Intel)
2. เบราว์เซอร์ **Safari**
   - เปิดการตั้งค่า: `Safari > Settings (การตั้งค่า) > Advanced (ขั้นสูง)`
   - ติ๊กถูกที่: **Show features for web developers** (แสดงคุณสมบัติสำหรับนักพัฒนา)
   - ไปที่แถบเมนูด้านบน: `Develop (การพัฒนา) > Allow JavaScript from Apple Events` (อนุญาตให้ใช้ JavaScript จาก Apple Events)
3. **Python 3.9+**

---

## 🚀 วิธีการใช้งาน (Usage Guide)

### 🔹 1. การรัน Speexx Master Bot (`speexx_bot.py`)

1. เปิด Safari แล้วล็อกอินเข้าเว็บไซต์ [Speexx Portal](https://portal.speexx.com)
2. เปิดแท็บบทเรียนที่ต้องการทำค้างไว้
3. รันคำสั่งใน Terminal ตามโหมดที่ต้องการ:

```bash
# 🎯 แบบที่ 1: รันทำแบบฝึกหัด และสะสมเวลาให้ครบ 10 ชั่วโมง (แนะนำ)
python3 speexx_bot.py --hours 10
# หรือพิมพ์แบบย่อ:
python3 speexx_bot.py 10

# ⏳ แบบที่ 2: ตั้งสะสม 10 ชั่วโมง + หน่วงเวลาข้อละ 20 วินาที (ดูเนียนเหมือนคนทำจริง)
python3 speexx_bot.py --hours 10 --delay 20

# 💤 แบบที่ 3: โหมดปั๊มชั่วโมงอย่างเดียว (สำหรับคนที่ทำข้อสอบครบแล้ว แต่เวลาเรียนยังขาด)
python3 speexx_bot.py --farm --hours 10

# ⚡ แบบที่ 4: รันแบบ Speed สูงสุด (ไม่จำกัดเวลา)
python3 speexx_bot.py
```

#### แฟล็กคำสั่งที่มีให้เลือก:
| Flag | Description |
| :--- | :--- |
| `--hours`, `-H` | กำหนดเป้าหมายชั่วโมงเรียน (เช่น `10` หรือ `5.5`) |
| `--delay`, `-d` | เวลาหน่วงระหว่างข้อ (วินาที) เพื่อความเป็นธรรมชาติ |
| `--farm`, `-f` | โหมดปั๊มสะสมชั่วโมงอย่างเดียว ไม่แตะต้องข้อสอบ |
| `--max-steps` | กำหนดจำนวนรอบลูปสูงสุด |

---

### 🔹 2. การรัน Cambridge One Bot (`cambridge_bot.py`)

1. เปิด Safari แล้วล็อกอินเข้าเว็บไซต์ [Cambridge One](https://www.cambridgeone.org)
2. เข้าไปยังหน้าแบบฝึกหัดของ Unit ที่ต้องการทำ
3. รันคำสั่งใน Terminal:

```bash
# รันความเร็วมาตรฐาน
python3 cambridge_bot.py

# หรือตั้งค่าหน่วงเวลา (เช่น ข้อละ 3 วินาที)
python3 cambridge_bot.py --delay 3
```

---

### 🔹 3. การดึงเฉลย Cambridge One (`dump_all_answers.py`)

```bash
python3 dump_all_answers.py
```

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```
evil-hacker/
├── speexx_bot.py             # บอททำข้อสอบ & สะสมชั่วโมง Speexx
├── cambridge_bot.py          # บอททำข้อสอบ Cambridge One อัตโนมัติ
├── dump_all_answers.py       # เครื่องมือดึงคลังเฉลย Cambridge One
├── assets/                   # ไฟล์กราฟิกและ Rich Menu LINE OA
│   ├── FastTrack_RichMenu.jpg
│   ├── FastTrack_Profile.jpg
│   └── ...
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔒 ความปลอดภัยและความเป็นส่วนตัว (Security & Safety)

- สคริปต์ทำงานแบบ Local ภายในเครื่องของผู้ใช้ผ่าน AppleScript Native Engine
- ไม่มีการเก็บหรือส่งออกรหัสผ่าน ข้อมูลล็อกอิน หรือข้อมูลส่วนตัวใดๆ
- การสะสมเวลาใช้การส่งสัญญาณ Pulse ภายในแท็บ ไม่รบกวนการทำงานอื่นบนเครื่อง

---

## ⚖️ ข้อสงวนสิทธิ์ (Disclaimer)

*โครงการนี้จัดทำขึ้นเพื่อการศึกษาและการวิจัยระบบอัตโนมัติในเบราว์เซอร์ (Browser Automation Research & Educational Purposes Only)*
