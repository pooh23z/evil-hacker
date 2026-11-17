#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 Cambridge One Universal Answer Extractor
รองรับทุกประเภทข้อสอบ: พิมพ์ข้อความ (Text Entry), เรียงประโยค (Word Order), และเลือกตอบ (Multiple Choice)
"""

import subprocess
import json
import re

JS_CODE = """
(function() {
  const frame = document.querySelectorAll('iframe')[1];
  if (!frame || !frame.contentWindow || !frame.contentWindow.ajaxData) {
    return JSON.stringify({ error: "กรุณาเปิดหน้าแบบฝึกหัดใน Safari ค้างไว้ก่อนครับ" });
  }

  const win = frame.contentWindow;
  const ajax = win.ajaxData;
  const results = [];

  for (let file in ajax) {
    if (file.endsWith('.xml') && file !== 'LearningObjectInfo.xml') {
      const xml = ajax[file];
      
      // ดึงโจทย์หรือข้อความนำ
      const pMatch = xml.match(/<div [^>]*class=[\"']contentblock[\"'][^>]*>.*?<p[^>]*>(.*?)<\\/p>/i) || xml.match(/<p[^>]*>(.*?)<\\/p>/i);
      let qText = pMatch ? pMatch[1].replace(/<[^>]+>/g, '').trim() : file;

      // 1. ตรวจสอบแบบเรียงประโยค (Gap Match / Word Order)
      const gapRegex = /<gapText[^>]+identifier=[\"']([^\"']+)[\"'][^>]*>(.*?)<\\/gapText>/g;
      let gm;
      const gapMap = {};
      while ((gm = gapRegex.exec(xml)) !== null) {
        gapMap[gm[1]] = gm[2].replace(/<[^>]+>/g, '').trim();
      }

      // 2. ดึง responseDeclaration ทั้งหมด (รองรับทั้งแบบพิมพ์และแบบกา)
      const respRegex = /<responseDeclaration[^>]+identifier=[\"']([^\"']+)[\"'][^>]*>([\\s\\S]*?)<\\/responseDeclaration>/g;
      let rm;
      const allResponses = [];

      while ((rm = respRegex.exec(xml)) !== null) {
        const respId = rm[1];
        const respBody = rm[2];

        // หาค่า <value>
        const valRegex = /<value>(.*?)<\\/value>/g;
        let vm;
        const vals = [];
        while ((vm = valRegex.exec(respBody)) !== null) {
          vals.push(vm[1].trim());
        }

        // หา mapping (คำที่ยอมรับเพิ่ม เช่น have not / haven't)
        const mapRegex = /<mapEntry[^>]+mapKey=[\"']([^\"']+)[\"']/g;
        let mm;
        const altVals = [];
        while ((mm = mapRegex.exec(respBody)) !== null) {
          if (!vals.includes(mm[1])) altVals.push(mm[1]);
        }

        allResponses.push({ id: respId, vals: vals, alts: altVals });
      }

      let typeStr = "ข้อสอบ";
      let answerDisplay = "";

      // กรณีที่ 1: เป็นแบบเรียงคำ (Gap Match / Word Order)
      if (Object.keys(gapMap).length > 0 && allResponses.length > 0) {
        typeStr = "เรียงประโยค (Word Order)";
        const orderedWords = [];
        for (let r of allResponses) {
          for (let v of r.vals) {
            const parts = v.split(' ');
            if (gapMap[parts[0]]) orderedWords.push(gapMap[parts[0]]);
          }
        }
        answerDisplay = orderedWords.join(' ➔ ');
      }
      // กรณีที่ 2: เป็นแบบพิมพ์ข้อความลงในช่องว่าง (Text Entry)
      else if (xml.includes('textEntryInteraction') || xml.includes('baseType="string"')) {
        typeStr = "พิมพ์คำตอบลงช่องว่าง (Text Entry)";
        const blanks = [];
        allResponses.forEach((r, idx) => {
          let str = `ช่องที่ ${idx + 1}: พิมพ์คำว่า "${r.vals.join(' หรือ ')}"`;
          if (r.alts.length > 0) {
            str += ` (ยอมรับคำว่า: ${r.alts.join(', ')})`;
          }
          blanks.push(str);
        });
        answerDisplay = blanks.join('\\n      ');
      }
      // กรณีที่ 3: ปรนัย / เลือกตอบ (Multiple Choice)
      else if (allResponses.length > 0) {
        typeStr = "เลือกตอบ (Multiple Choice)";
        const choices = [];
        allResponses.forEach(r => {
          choices.push(r.vals.join(', '));
        });
        answerDisplay = choices.join('; ');
      }

      if (answerDisplay) {
        results.push({
          file: file,
          type: typeStr,
          question: qText,
          answer: answerDisplay
        });
      }
    }
  }

  return JSON.stringify({
    title: document.title,
    count: results.length,
    items: results
  });
})()
"""

with open('/tmp/dump.js', 'w', encoding='utf-8') as f:
    f.write(JS_CODE)

scpt = '''
tell application "Safari"
  set jsCode to read POSIX file "/tmp/dump.js" as «class utf8»
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t) contains "cambridgeone.org" then
        return do JavaScript jsCode in t
      end if
    end repeat
  end repeat
  return "TAB_NOT_FOUND"
end tell
'''

try:
    out = subprocess.check_output(['osascript'], input=scpt.encode('utf-8')).decode('utf-8').strip()
    data = json.loads(out)
    if "error" in data:
      print(f"[-] {data['error']}")
    else:
      print("=" * 70)
      print(f"📖 ชุดแบบฝึกหัด: {data.get('title')}")
      print(f"🎯 ดึงเฉลยสำเร็จทั้งหมด: {data.get('count')} ข้อ")
      print("=" * 70)
      for i, item in enumerate(data.get('items', []), 1):
        print(f"\n📌 ข้อที่ {i} [{item['type']}]:")
        print(f"   โจทย์: {item['question']}")
        print(f"   👉 คำตอบ:\n      {item['answer']}")
      print("\n" + "=" * 70)
except Exception as e:
    print(f"[-] เกิดข้อผิดพลาด: {e}")
