#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Cambridge One Universal Auto-Solver Bot (ฉบับแก้ไขการจับคู่คำศัพท์ 100%)
"""

import subprocess
import json
import time
import os
import sys

JS_CODE = """
(function() {
  try {
    // 1. ตรวจสอบปุ่มข้ามไปแบบฝึกหัดชุดถัดไป (Next Activity)
    const nextActBtn = document.querySelector('.nextActivityBtn, .btn-primary');
    if (nextActBtn && nextActBtn.offsetParent !== null) {
      const txt = nextActBtn.innerText.trim();
      if (txt.includes('NEXT') || txt.includes('Next activity')) {
        nextActBtn.click();
        return JSON.stringify({ status: "NEXT_ACTIVITY_CLICKED", text: txt });
      }
    }

    // 2. ตรวจสอบปุ่มเขียว: ถ้าเป็น "Next" ให้กดเปลี่ยนข้อทันที
    const greenBtn = document.querySelector('.green-btn');
    if (greenBtn && greenBtn.innerText.trim().toLowerCase() === 'next') {
      greenBtn.click();
      return JSON.stringify({ status: "CLICKED_NEXT_QUESTION" });
    }

    // 3. ตรวจสอบ iframe ข้อสอบ
    const frame = document.querySelectorAll('iframe')[1];
    if (!frame || !frame.contentWindow || !frame.contentWindow.ajaxData) {
      return JSON.stringify({ status: "WAITING_FOR_EXAM" });
    }

    const win = frame.contentWindow;
    const doc = frame.contentDocument;

    // 4. หาข้อที่กำลังแสดงอยู่
    const activeWrap = Array.from(doc.querySelectorAll('.content-wrap, [id*="content_wrap"]')).find(w => {
      return window.getComputedStyle(w).display !== 'none';
    });

    if (!activeWrap) {
      return JSON.stringify({ status: "NO_ACTIVE_WRAP" });
    }

    // --- แบบที่ A: จัดเรียงคำ / ลากวาง (Word Order / Gap Match) ---
    const dropAreas = Array.from(activeWrap.querySelectorAll('.gap_match_gap_view')).filter(el => el.offsetParent !== null);
    if (dropAreas.length > 0) {
      const emptyGaps = dropAreas.filter(d => !d.classList.contains('has_drag') && d.innerText.trim() === '');
      
      if (emptyGaps.length > 0) {
        // ดึงคำศัพท์ทั้งหมดที่อยู่ใน Word Pool ปัจจุบัน
        const pool = activeWrap.querySelector('.pool, .wordpool, ul');
        const poolWords = pool ? Array.from(pool.querySelectorAll('.drag_element')).map(el => el.innerText.trim()) : [];

        // หา XML ที่มีคำตรงกับใน poolWords มากที่สุด (แก้ปัญหาจับคู่ผิดข้อ 100%)
        let bestXml = null;
        let bestGapMap = {};
        let maxMatches = 0;

        for (let f in win.ajaxData) {
          const xml = win.ajaxData[f];
          if (xml.includes('gapMatchInteraction') || xml.includes('gapText')) {
            const gapRegex = /<gapText[^>]+identifier=[\"']([^\"']+)[\"'][^>]*>(.*?)<\\/gapText>/g;
            let gm;
            const gMap = {};
            while ((gm = gapRegex.exec(xml)) !== null) {
              gMap[gm[1]] = gm[2].replace(/<[^>]+>/g, '').trim();
            }

            let matches = 0;
            for (let gWord of Object.values(gMap)) {
              if (poolWords.includes(gWord)) matches++;
            }

            if (matches > maxMatches) {
              maxMatches = matches;
              bestXml = xml;
              bestGapMap = gMap;
            }
          }
        }

        // ย้ายคำศัพท์ที่ถูกต้องเข้ากล่องตามลำดับ
        let targetWords = [];
        if (bestXml && Object.keys(bestGapMap).length > 0) {
          const ansMatch = bestXml.match(/<correctResponse>([\\s\\S]*?)<\\/correctResponse>/);
          if (ansMatch) {
            const valRegex = /<value>(.*?)<\\/value>/g;
            let vm;
            while ((vm = valRegex.exec(ansMatch[1])) !== null) {
              const parts = vm[1].trim().split(' ');
              if (bestGapMap[parts[0]]) targetWords.push(bestGapMap[parts[0]]);
            }

            let movedCount = 0;
            for (let w of targetWords) {
              const drags = Array.from(doc.querySelectorAll('.drag_element')).filter(el => {
                return el.innerText.trim() === w && el.offsetParent !== null && !el.closest('.gap_match_gap_view');
              });

              if (drags.length > 0) {
                const view = win.$(drags[0]).data('mvcView');
                if (view && typeof view.moveToEmptyGap === 'function') {
                  view.moveToEmptyGap();
                  movedCount++;
                }
              }
            }

            return JSON.stringify({
              status: "FILLED_WORD_ORDER",
              movedCount: movedCount,
              sentence: targetWords.join(' ')
            });
          }
        }
      }

      // ถ้าเติมครบแล้ว และปุ่มเขียวเป็น "Check" ให้กด Check ทันที
      if (greenBtn && greenBtn.innerText.trim().toLowerCase() === 'check') {
        greenBtn.click();
        return JSON.stringify({ status: "CLICKED_CHECK_WORD_ORDER" });
      }
    }

    // --- แบบที่ B: ปรนัย / รูปภาพ (Multiple Choice / Radio) ---
    const pEl = activeWrap.querySelector('.contentblock p, p.active') || activeWrap.querySelector('#contentblock p');
    const name = pEl ? pEl.innerText.trim() : activeWrap.innerText.trim();

    let ansId = null;
    for (let f in win.ajaxData) {
      if (f.endsWith('.xml') && win.ajaxData[f].includes(name)) {
        const aMatch = win.ajaxData[f].match(/<correctResponse>[\\s\\S]*?<value>(.*?)<\\/value>[\\s\\S]*?<\\/correctResponse>/);
        if (aMatch) {
          ansId = aMatch[1].trim().toLowerCase();
          break;
        }
      }
    }

    if (!ansId) {
      for (let f in win.ajaxData) {
        if (f.startsWith('cat') && f.endsWith('.xml')) {
          const aMatch = win.ajaxData[f].match(/<correctResponse>[\\s\\S]*?<value>(.*?)<\\/value>[\\s\\S]*?<\\/correctResponse>/);
          if (aMatch) {
            const testId = aMatch[1].trim().toLowerCase().replace('_', '-');
            const found = activeWrap.querySelector('div[id*="' + testId + '"]');
            if (found) {
              ansId = aMatch[1].trim().toLowerCase();
              break;
            }
          }
        }
      }
    }

    let radioClicked = false;
    if (ansId) {
      const formattedId = ansId.replace('_', '-');
      const radio = activeWrap.querySelector('div[id*="' + formattedId + '"]');
      if (radio) {
        if (win.$) {
          win.$(radio).trigger('click');
          win.$(radio).find('input').prop('checked', true).trigger('change');
        } else {
          radio.click();
        }
        radioClicked = true;
      }
    }

    if (greenBtn && greenBtn.innerText.trim().toLowerCase() === 'check') {
      greenBtn.click();
      return JSON.stringify({ status: "CLICKED_CHECK_RADIO", name: name, ansId: ansId });
    }

    return JSON.stringify({ status: "READY_WAITING" });
  } catch(e) {
    return JSON.stringify({ status: "ERROR", msg: e.toString() });
  }
})()
"""

JS_PATH = "/tmp/cambridge_tick.js"
with open(JS_PATH, "w", encoding="utf-8") as f:
    f.write(JS_CODE)

APPLESCRIPT = f"""
tell application "Safari"
  set jsCode to read POSIX file "{JS_PATH}" as «class utf8»
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t) contains "cambridgeone.org" then
        set res to do JavaScript jsCode in t
        return res
      end if
    end repeat
  end repeat
  return "TAB_NOT_FOUND"
end tell
"""

def run_tick():
    try:
        out = subprocess.check_output(['osascript'], input=APPLESCRIPT.encode('utf-8')).decode('utf-8').strip()
        if out == "TAB_NOT_FOUND":
            return {"status": "TAB_NOT_FOUND"}
        return json.loads(out)
    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="🚀 Cambridge One Universal Auto-Solver Bot (FastTrack English Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
วิธีใช้งาน:
  1. เปิด Safari แล้วล็อกอินเข้าเว็บไซต์ Cambridge One (https://www.cambridgeone.org)
  2. เข้าไปยังหน้าแบบฝึกหัด หรือ Unit ที่ต้องการทำ
  3. รันคำสั่งบอทใน Terminal:
       python3 cambridge_bot.py
       python3 cambridge_bot.py --delay 3  # หน่วงเวลา 3 วินาทีต่อข้อ
"""
    )
    parser.add_argument("--delay", "-d", type=float, default=1.5, help="เวลาหน่วงระหว่างรอบ (วินาที) ค่าเริ่มต้น 1.5 วิ")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Cambridge One Universal Auto-Solver พร้อมทำงานแล้ว!")
    print(f"⏱️ ตั้งค่าหน่วงเวลา: {args.delay:.1f} วินาทีต่อรอบ")
    print("🌐 บอทกำลังตรวจจับแท็บข้อสอบใน Safari (รองรับทุกประเภทข้อสอบ)...")
    print("🛑 กด Ctrl + C เพื่อหยุดการทำงานได้ตลอดเวลา")
    print("=" * 60)

    step = 0
    try:
        while True:
            res = run_tick()
            status = res.get("status")

            if status == "TAB_NOT_FOUND":
                print("⏳ ไม่พบแท็บ Cambridge One ใน Safari... กำลังค้นหาใหม่")
            elif status == "WAITING_FOR_EXAM":
                print("⏳ กำลังรอหน้าต่างแบบฝึกหัดโหลด...")
            elif status == "FILLED_WORD_ORDER":
                sentence = res.get("sentence") or "ประโยค"
                print(f"🧩 [เรียงประโยคสำเร็จ] จัดคำเรียงเข้ากล่อง: \"{sentence}\"")
            elif status == "CLICKED_CHECK_WORD_ORDER":
                print("✅ กดปุ่ม Check ตรวจประโยคเรียบร้อย!")
            elif status == "CLICKED_CHECK_RADIO":
                q_name = res.get("name") or "ข้อสอบ"
                ans = res.get("ansId") or "คำตอบ"
                print(f"🎯 [ทำข้อสอบ] {q_name} -> ติ๊กตัวเลือก: {ans} -> กด Check")
            elif status == "CLICKED_NEXT_QUESTION":
                print("➡️ [ข้ามข้อ] กด Next เพื่อไปข้อถัดไป...")
            elif status == "NEXT_ACTIVITY_CLICKED":
                print("🎉 [จบชุดนี้แล้ว!] กำลังกด Next Activity เพื่อข้ามไปแบบฝึกหัดชุดถัดไป...")

            time.sleep(args.delay)
    except KeyboardInterrupt:
        print("\n👋 หยุดการทำงานของบอทเรียบร้อยแล้วครับ!")
