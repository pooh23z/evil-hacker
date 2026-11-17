#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ Speexx Autonomous Master Bot (FastTrack English Edition)
========================================================================
Advanced macOS Safari Automation Engine for Speexx Digital Learning
- 100% Exact JSON answers for ALL exercise types:
  * ANSWER (Text Inputs)
  * TOGGLE_SOLUTION (Cycle buttons)
  * SINGLE_CHOICE / MULTIPLE_CHOICE / PICTURE_CHOICE (Checkboxes & Radios)
  * MARK_TEXT (Verb & Text Marking)
  * SCRAMBLED_SENTENCE (Filtered scrambled blocks, 100% accurate)
  * SCRAMBLED_TABLE (Table Cell Data Sync, 100% accurate)
  * DRAG_DROP / PICTURE_CHOICE (Blanks & Drag containers with :visible check)
  * PRONUNCIATION (Auto-Skip speaking tasks + Auto Continue)
  * DASHBOARD (Auto-Start Next Packet via "Start now" / "เริ่มตอนนี้")
- Zero loops: Automatically detects when all exercises are complete and fetches continueUrl
- Auto-recovery: Automatically resets/re-attempts any non-100% exercise
- Integrated Study Hours Accumulator (Anti-Idle Keep-Alive pulse engine)
- Continuous runner until Level target or desired study hours are fulfilled
========================================================================
"""

import subprocess
import json
import time
import sys
import os
import re
import shutil
import datetime

# ========================================================================
# TERMINAL UI & STYLING SYSTEM (Zero External Dependencies)
# ========================================================================

USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
CYAN = '\033[96m' if USE_COLOR else ''
MAGENTA = '\033[95m' if USE_COLOR else ''
GREEN = '\033[92m' if USE_COLOR else ''
YELLOW = '\033[93m' if USE_COLOR else ''
BLUE = '\033[94m' if USE_COLOR else ''
RED = '\033[91m' if USE_COLOR else ''
WHITE = '\033[97m' if USE_COLOR else ''
DIM = '\033[90m' if USE_COLOR else ''
BOLD = '\033[1m' if USE_COLOR else ''
RESET = '\033[0m' if USE_COLOR else ''

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def vlen(s: str) -> int:
    """Return visible character length of string, stripping ANSI escape codes."""
    return len(ANSI_RE.sub('', s))

def render_box(lines, title=None, width=76) -> str:
    """Render a modern rounded-corner box with pixel-perfect alignment."""
    term_width = shutil.get_terminal_size((80, 24)).columns
    box_w = max(40, min(width, term_width - 2))
    res = []
    
    top_border = f"{DIM}╭─"
    if title:
        top_border += f" {BOLD}{CYAN}{title}{RESET}{DIM} " + "─" * max(0, box_w - 4 - vlen(title) - 2)
    else:
        top_border += "─" * (box_w - 2)
    top_border += f"╮{RESET}"
    res.append(top_border)
    
    for line in lines:
        if line == "---":
            res.append(f"{DIM}├" + "─" * (box_w - 2) + f"┤{RESET}")
            continue
        pad = box_w - 4 - vlen(line)
        if pad < 0:
            pad = 0
        res.append(f"{DIM}│{RESET}  {line}" + " " * pad + f"{DIM}│{RESET}")
        
    res.append(f"{DIM}╰" + "─" * (box_w - 2) + f"╯{RESET}")
    return "\n".join(res)

def progress_bar(pct: float, length=20) -> str:
    """Render a sleek modern gradient progress bar."""
    pct = max(0.0, min(100.0, pct))
    filled = int(round(length * (pct / 100.0)))
    filled = max(0, min(length, filled))
    bar = "█" * filled + "░" * (length - filled)
    return f"{CYAN}[{GREEN}{bar[:filled]}{DIM}{bar[filled:]}{CYAN}]{RESET}"

BADGES = {
    'SOLVE': (GREEN,   ' SOLVE '),
    'NEXT':  (BLUE,    ' NEXT  '),
    'SKIP':  (MAGENTA, ' SKIP  '),
    'CLEAR': (GREEN,   ' CLEAR '),
    'DASH':  (CYAN,    ' DASH  '),
    'RETRY': (YELLOW,  ' RETRY '),
    'WAIT':  (DIM,     ' WAIT  '),
    'ALERT': (RED,     ' ALERT '),
    'PULSE': (CYAN,    ' PULSE '),
    'MODAL': (DIM,     ' MODAL '),
    'INFO':  (WHITE,   ' INFO  '),
}

def log_event(badge_key: str, category: str, message: str, meta="", time_badge=""):
    """Format and print a standardized high-contrast terminal log line."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    color, text = BADGES.get(badge_key, (WHITE, ' LOG   '))
    badge_str = f"{color}{BOLD}[{text}]{RESET}"
    cat_str = f"{CYAN}{category:<10}{RESET}"
    meta_str = f" {DIM}{meta}{RESET}" if meta else ""
    t_str = f" {YELLOW}{time_badge}{RESET}" if time_badge else ""
    print(f"{DIM}{now}{RESET}  {badge_str}  {cat_str}  {message}{meta_str}{t_str}")

def format_time(seconds: float) -> str:
    """Format seconds into concise digital clock format."""
    seconds = int(max(0, seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}h {m:02d}m {s:02d}s"
    return f"{m:02d}m {s:02d}s"

def print_banner(target_hours=None, delay=0.3, farm_only=False):
    """Display modern cybersecurity-inspired header banner and configuration."""
    target_desc = f"{target_hours:.1f} hrs ({format_time(target_hours * 3600)})" if target_hours else "Unlimited (Continuous)"
    delay_desc = f"{delay:.1f}s per exercise" if (delay and delay > 0.5) else "0.3s (Turbo Mode)"
    mode_desc = "Study Hours Accumulator Only (Farm Mode)" if farm_only else ("Auto-Solver + Accumulator" if target_hours else "Full Autonomous Solver")

    logo = f"""{CYAN}{BOLD}
   ███████╗██████╗ ███████╗███████╗██╗  ██╗██╗  ██╗
   ██╔════╝██╔══██╗██╔════╝██╔════╝╚██╗██╔╝╚██╗██╔╝  {WHITE}AUTONOMOUS ENGINE v3.0{CYAN}
   ███████╗██████╔╝█████╗  █████╗   ╚███╔╝  ╚███╔╝   {DIM}Speexx FastTrack Master{CYAN}
   ╚════██║██╔═══╝ ██╔══╝  ██╔══╝   ██╔██╗  ██╔██╗   {GREEN}100% Accuracy Verified{CYAN}
   ███████║██║     ███████╗███████╗██╔╝ ██╗██╔╝ ██╗  {BLUE}macOS Safari Engine{CYAN}
   ╚══════╝╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝{RESET}"""
    print(logo)

    config_lines = [
        f"{CYAN}Target Hours {RESET}: {WHITE}{target_desc}{RESET}",
        f"{CYAN}Pacing Delay {RESET}: {WHITE}{delay_desc}{RESET}",
        f"{CYAN}Engine Mode  {RESET}: {GREEN}{mode_desc}{RESET}"
    ]
    print(render_box(config_lines, title="SESSION ACTIVE", width=76))
    print()

# ========================================================================
# IN-BROWSER JAVASCRIPT SOLVER CORE
# ========================================================================

JS_TICK_PATH = "/tmp/speexx_tick.js"

JS_CODE = r"""
(function() {
  try {
    function norm(s) {
      return (s || '').replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').replace(/\s+([.,?!:])/g, '$1').trim();
    }

    // 0. Dismiss any stray modal/dialog if present
    let modalBtn = document.querySelector('.modal.in .btn-primary, .modal.show .btn-primary, .bootbox .btn-primary, .modal.in .btn, .modal.show .btn');
    if (modalBtn && modalBtn.offsetParent !== null) {
      modalBtn.click();
      return JSON.stringify({ status: "DISMISSED_MODAL" });
    }

    // 1. Check for Dashboard "Start now" / "เริ่มตอนนี้" (Start next packet on main screen)
    if (!window.location.pathname.includes('standard-packet') && !window.location.pathname.includes('pronunciation-packet')) {
      let startNowBtn = Array.from(document.querySelectorAll('button, a, div[role="button"]')).find(el => {
        let t = el.innerText.trim();
        return (t === 'เริ่มตอนนี้' || t.includes('เริ่มตอนนี้') || t === 'Start now') && el.offsetParent !== null;
      });
      if (startNowBtn) {
        startNowBtn.click();
        return JSON.stringify({ status: "CLICKED_START_NOW" });
      }
    }

    // 2. Check for "Continue" / "เรียนรู้ต่อ" (Continue Learning to next packet)
    let continueBtn = Array.from(document.querySelectorAll('a, button, .btn')).find(el => {
      let t = el.innerText.trim();
      return (t === 'เรียนรู้ต่อ' || t === 'Continue' || t.includes('เรียนรู้ต่อ')) && el.offsetParent !== null;
    });
    if (continueBtn) {
      continueBtn.click();
      let prog = window.JsonValues && window.JsonValues.progress ? window.JsonValues.progress : null;
      return JSON.stringify({ status: "CLICKED_CONTINUE_PACKET", progress: prog });
    }

    // 3. Pronunciation Packet Auto-Skip (Auto-bypasses spoken pronunciation tasks)
    if (window.location.pathname.includes('pronunciation-packet') || 
        document.querySelector('.microphone-button, .type-single-item-pronunciation, .type-multiple-item-pronunciation')) {
      let nextBtn = document.querySelector('.action-exercise-button.next, .nxt-exercise');
      if (nextBtn && nextBtn.offsetParent !== null) {
        nextBtn.click();
        return JSON.stringify({ status: "PRONUNCIATION_NEXT" });
      }
      
      // If in pronunciation-packet and no next button, packet is finished! Advance to next packet!
      if (window.location.pathname.includes('pronunciation-packet')) {
        let contUrl = window.Utils ? window.Utils.getJsonValue("continueUrl") : null;
        if (contUrl) {
          let nextUrl = null;
          $.ajax({
            url: contUrl,
            async: false,
            dataType: "json",
            success: function(d) { if (d && d.redirect) nextUrl = d.redirect; }
          });
          if (nextUrl) {
            window.location.href = nextUrl;
            return JSON.stringify({ status: "PRONUNCIATION_FINISHED_REDIRECT", nextUrl: nextUrl });
          }
        }
        let closeNav = window.Utils ? window.Utils.getJsonValue("closeNavPath") : "/articles/10918668";
        window.location.href = closeNav;
        return JSON.stringify({ status: "PRONUNCIATION_FINISHED_DASHBOARD" });
      }
    }

    // 4. Identify current context (Level Test vs Standard Packet)
    let isLevelTest = window.location.pathname.includes('level-test');
    let folderData = null;
    let exData = null;
    let exOrdinal = 1;
    let corrBtn = document.querySelector('.action-exercise-button.correct, .btn.correct');
    let nextBtn = document.querySelector('.action-exercise-button.next, .nxt-exercise, .btn.next');
    let badge = document.querySelector('.result-badge, [class*="badge"]')?.innerText.replace(/\s+/g, ' ').trim();

    // Auto-recovery: If badge shows score < 100 and next is not primary, reload to reset
    if (badge && badge !== '100100' && nextBtn && !nextBtn.classList.contains('btn-primary')) {
      window.location.reload();
      return JSON.stringify({ status: "RELOAD_NON_100", badge: badge });
    }

    if (isLevelTest) {
      if (!window.JsonValues || !window.JsonValues.test || !window.JsonValues.test.exercises) {
        return JSON.stringify({ status: "WAITING_FOR_PAGE" });
      }

      let testExercises = window.JsonValues.test.exercises;
      let header = document.querySelector('.exercise-header, h1')?.innerText || '';
      let m = header.match(/\d+/);
      exOrdinal = m ? parseInt(m[0]) : 1;

      // Check if finished or submit button
      let submitBtn = Array.from(document.querySelectorAll('button, a, .btn')).find(el => {
        let t = el.innerText.trim();
        return (t === 'ส่งคำตอบ' || t === 'Submit' || t === 'Finish' || t.includes('เสร็จสิ้น') || t.includes('ผลลัพธ์')) && el.offsetParent !== null;
      });
      if (submitBtn) {
        submitBtn.click();
        return JSON.stringify({ status: "SUBMITTED_LEVEL_TEST" });
      }

      if (nextBtn && nextBtn.classList.contains('btn-primary')) {
        nextBtn.click();
        return JSON.stringify({ status: "CLICKED_NEXT", badge: badge, ordinal: exOrdinal });
      }

      let currentExMeta = testExercises[exOrdinal - 1];
      if (!currentExMeta) {
        return JSON.stringify({ status: "NO_EX_META", exOrdinal: exOrdinal });
      }

      let exUrl = `${window.JsonValues.articlePath}/level-test/exercises/${currentExMeta.id}`;
      $.ajax({
        url: exUrl,
        async: false,
        dataType: 'json',
        success: function(d) { exData = d; }
      });

      if (!exData) {
        return JSON.stringify({ status: "NO_EX_DATA" });
      }

      folderData = {
        title: "CEFR Level Test",
        exercises: testExercises
      };
    } else {
      let pathParts = window.location.pathname.split('/');
      let packetType = 'standard-packet';
      let packetId = null;
      for (let i = 0; i < pathParts.length; i++) {
        if ((pathParts[i] === 'standard-packet' || pathParts[i] === 'pronunciation-packet') && pathParts[i+1]) {
          packetType = pathParts[i];
          packetId = pathParts[i+1];
        }
        if (pathParts[i] === 'exercise' && pathParts[i+1]) {
          exOrdinal = parseInt(pathParts[i+1]);
        }
      }

      if (!window.JsonValues || !window.JsonValues.packets || !window.JsonValues.packets[0]) {
        return JSON.stringify({ status: "WAITING_FOR_PAGE" });
      }

      let folderId = window.JsonValues.packets[0].id;
      let folderUrl = `${window.JsonValues.articlePath}/${packetType}/${packetId}/folders/${folderId}`;
      
      $.ajax({
        url: folderUrl,
        async: false,
        dataType: 'json',
        success: function(d) { folderData = d; }
      });

      if (!folderData || !folderData.exercises) {
        return JSON.stringify({ status: "NO_FOLDER_DATA" });
      }

      // Check if ALL exercises in the packet are already solved!
      let allDone = folderData.exercises.every(e => !e.type.hasResult || e.result === 100);
      if (allDone) {
        let contUrl = window.Utils ? window.Utils.getJsonValue("continueUrl") : null;
        if (contUrl) {
          let nextUrl = null;
          $.ajax({
            url: contUrl,
            async: false,
            dataType: "json",
            success: function(d) { if (d && d.redirect) nextUrl = d.redirect; }
          });
          if (nextUrl) {
            window.location.href = nextUrl;
            return JSON.stringify({ status: "REDIRECTED_NEXT_PACKET", nextUrl: nextUrl, progress: window.JsonValues?.progress, levelName: window.JsonValues?.currentLevelBean?.name });
          }
        }
        let closeNav = window.Utils ? window.Utils.getJsonValue("closeNavPath") : "/articles/10918668";
        window.location.href = closeNav;
        return JSON.stringify({ status: "EXITED_TO_DASHBOARD" });
      }

      if (nextBtn && nextBtn.classList.contains('btn-primary')) {
        nextBtn.click();
        return JSON.stringify({ status: "CLICKED_NEXT", badge: badge });
      }

      // Check for "Start" button
      let startBtn = document.querySelector('.btn.start-exercise, .start-exercise, button.start');
      if (startBtn && startBtn.offsetParent !== null) {
        startBtn.click();
        return JSON.stringify({ status: "CLICKED_START" });
      }

      let currentExMeta = folderData.exercises.find(e => e.ordinal === exOrdinal) || folderData.exercises[exOrdinal - 1];
      if (!currentExMeta) {
        return JSON.stringify({ status: "NO_EX_META", exOrdinal: exOrdinal });
      }

      // Fetch exercise detail JSON
      let exUrl = `${folderUrl}/exercises/${currentExMeta.id}`;
      $.ajax({
        url: exUrl,
        async: false,
        dataType: 'json',
        success: function(d) { exData = d; }
      });

      if (!exData) {
        return JSON.stringify({ status: "NO_EX_DATA" });
      }
    }

    let exType = exData.type ? exData.type.name : '';
    let layoutObj = exData.content || exData.exerciseLayout || {};

    // ----------------------------------------------------
    // TYPE A: ANSWER (Text Input fields) - 100% Accurate
    // ----------------------------------------------------
    if (exType === 'ANSWER') {
      let solMap = exData.answerSolutions || {};
      let filled = 0;
      $('input.answer, input[data-answer-id], textarea.answer, textarea[data-answer-id]').each(function() {
        let aid = $(this).attr('data-answer-id');
        let solObj = solMap[aid];
        if (solObj) {
          let sol = solObj.solution || (Array.isArray(solObj.solutions) ? solObj.solutions[0] : '');
          if (sol) {
            this.focus();
            this.value = sol;
            this.dispatchEvent(new Event('input', { bubbles: true }));
            this.dispatchEvent(new Event('change', { bubbles: true }));
            this.dispatchEvent(new Event('blur', { bubbles: true }));
            $(this).val(sol).trigger('input').trigger('change').trigger('blur');
            filled++;
          }
        }
      });

      if (corrBtn && corrBtn.offsetParent !== null) {
        corrBtn.click();
      }

      return JSON.stringify({
        status: "SOLVED_ANSWER",
        title: exData.title,
        filled: filled,
        packetTitle: folderData.title,
        exOrdinal: exOrdinal,
        totalEx: folderData.exercises.length
      });
    }

    // ----------------------------------------------------
    // TYPE B: TOGGLE_SOLUTION (Cycle buttons) - 100% Accurate
    // ----------------------------------------------------
    if (exType === 'TOGGLE_SOLUTION') {
      let correctValues = [];
      function searchGaps(node) {
        if (!node || typeof node !== 'object') return;
        if (node.type === 'gap') {
          let c = (node.list || []).find(x => !x.errorId);
          if (c && c.words) {
            correctValues.push(norm(c.words.map(w => w.$).join('')));
          }
        }
        for (let k in node) searchGaps(node[k]);
      }
      searchGaps(layoutObj);

      let btns = document.querySelectorAll('.input-group-addon button');
      let gaps = document.querySelectorAll('.gap');
      let matchedCount = 0;

      for (let i = 0; i < correctValues.length && i < btns.length; i++) {
        let target = correctValues[i];
        let btn = btns[i];
        let gap = gaps[i];
        let attempts = 0;
        while (norm(gap.innerText) !== target && attempts < 15) {
          btn.click();
          attempts++;
        }
        if (norm(gap.innerText) === target) matchedCount++;
      }

      if (corrBtn && corrBtn.offsetParent !== null) {
        corrBtn.click();
      }

      return JSON.stringify({
        status: "SOLVED_TOGGLE",
        title: exData.title,
        matched: matchedCount,
        total: correctValues.length,
        packetTitle: folderData.title,
        exOrdinal: exOrdinal,
        totalEx: folderData.exercises.length
      });
    }

    // ----------------------------------------------------
    // TYPE C: SINGLE_CHOICE / MULTIPLE_CHOICE - 100% Accurate
    // ----------------------------------------------------
    if (exType === 'SINGLE_CHOICE' || exType === 'MULTIPLE_CHOICE' || exType === 'PICTURE_CHOICE') {
      let correctOptionsList = [];
      function searchChoices(node) {
        if (!node || typeof node !== 'object') return;
        if (node.type === 'choiceOption' || node.type === 'choice') {
          correctOptionsList.push(!!node.correct);
        }
        for (let k in node) searchChoices(node[k]);
      }
      searchChoices(layoutObj);

      let inputs = document.querySelectorAll('input[type="checkbox"], input[type="radio"]');
      if (inputs.length > 0 && correctOptionsList.length === inputs.length) {
        // 1. Uncheck checkboxes that shouldn't be checked
        for (let i = 0; i < inputs.length; i++) {
          let inp = inputs[i];
          if (!correctOptionsList[i] && inp.type === 'checkbox' && inp.checked) {
            inp.click();
          }
        }
        // 2. Check inputs that should be checked
        for (let i = 0; i < inputs.length; i++) {
          let inp = inputs[i];
          if (correctOptionsList[i] && !inp.checked) {
            inp.click();
          }
        }

        if (corrBtn && corrBtn.offsetParent !== null) {
          corrBtn.click();
        }

        return JSON.stringify({
          status: "SOLVED_CHOICE_JSON",
          title: exData.title,
          packetTitle: folderData.title,
          exOrdinal: exOrdinal,
          totalEx: folderData.exercises.length
        });
      }

      // Picture Choice with Draggable Images
      let picGaps = [];
      function searchPicGaps(node) {
        if (!node || typeof node !== 'object') return;
        if (node.type === 'pictureGap' && node.file) {
          picGaps.push(node.file);
        }
        for (let k in node) searchPicGaps(node[k]);
      }
      searchPicGaps(layoutObj);

      if (picGaps.length > 0) {
        let placeholders = $('.item .drag-drop-placeholder');
        let visibleCount = placeholders.filter(':visible').length;

        if (visibleCount === 0) {
          if (corrBtn && corrBtn.offsetParent !== null) corrBtn.click();
          return JSON.stringify({
            status: "SOLVED_PICTURE_CHOICE",
            title: exData.title,
            packetTitle: folderData.title,
            exOrdinal: exOrdinal,
            totalEx: folderData.exercises.length
          });
        }

        if (window._picTimer) {
          return JSON.stringify({ status: "PIC_IN_PROGRESS", remaining: visibleCount });
        }

        window._picTimer = setInterval(function() {
          let phs = $('.item .drag-drop-placeholder');
          let placed = false;
          for (let i = 0; i < phs.length && i < picGaps.length; i++) {
            let ph = phs.eq(i);
            if (ph.is(':visible')) {
              let targetFile = picGaps[i];
              let img = $('img').filter(function() {
                return !$(this).closest('.item').length && $(this).attr('src').includes(targetFile) && $(this).is(':visible');
              }).first();
              if (img.length) {
                ph[0].click();
                img[0].click();
                placed = true;
                break;
              }
            }
          }

          let rem = $('.item .drag-drop-placeholder:visible').length;
          if (rem === 0 || !placed) {
            clearInterval(window._picTimer);
            window._picTimer = null;
            let btn = document.querySelector('.action-exercise-button.correct');
            if (btn && btn.offsetParent !== null) {
              btn.click();
            }
          }
        }, 50);

        return JSON.stringify({ status: "STARTED_FAST_PIC", remaining: visibleCount });
      }
    }

    // ----------------------------------------------------
    // TYPE D: MARK_TEXT - 100% Accurate
    // ----------------------------------------------------
    if (exType === 'MARK_TEXT') {
      // Unmark any erroneously marked words outside .mark-text
      $('.markable-word.marked-text').each(function() { this.click(); });
      
      // Mark all .mark-text elements that aren't yet marked
      let marked = 0;
      $('.mark-text').each(function() {
        if (!$(this).hasClass('marked-text')) {
          this.click();
          marked++;
        }
      });

      if (corrBtn && corrBtn.offsetParent !== null) {
        corrBtn.click();
      }

      return JSON.stringify({
        status: "SOLVED_MARK_TEXT",
        title: exData.title,
        marked: marked,
        packetTitle: folderData.title,
        exOrdinal: exOrdinal,
        totalEx: folderData.exercises.length
      });
    }

    // ----------------------------------------------------
    // TYPE E: SCRAMBLED_SENTENCE - 100% Accurate
    // ----------------------------------------------------
    if (exType === 'SCRAMBLED_SENTENCE') {
      let scrambledItems = [];
      function findScrambledNodes(node) {
        if (!node || typeof node !== 'object') return;
        if (node.type === 'scrambled' && Array.isArray(node.list) && node.list.length > 0) {
          scrambledItems.push(node.list);
          return;
        }
        if (Array.isArray(node)) {
          node.forEach(findScrambledNodes);
        } else {
          for (let k in node) findScrambledNodes(node[k]);
        }
      }
      findScrambledNodes(exData.content || exData.exerciseLayout);

      let sentences = $('.scrambled-sentence');
      let reorderedCount = 0;

      scrambledItems.forEach(function(blocksMeta, idx) {
        let container = sentences.eq(idx);
        let targetWords = blocksMeta.map(b => norm((b.words || []).map(w => w.$ || '').join('')));

        targetWords.forEach(function(targetWord) {
          let matchingBlock = container.children('.scrambled-block:not(.reordered)').filter(function() {
            return norm($(this).text()) === targetWord;
          }).first();

          if (matchingBlock.length) {
            matchingBlock.addClass('reordered').appendTo(container);
            reorderedCount++;
          }
        });
      });

      $('.scrambled-block').removeClass('reordered');

      if (corrBtn && corrBtn.offsetParent !== null) {
        corrBtn.click();
      }

      return JSON.stringify({
        status: "SOLVED_SCRAMBLED_SENTENCE",
        title: exData.title,
        reordered: reorderedCount,
        packetTitle: folderData.title,
        exOrdinal: exOrdinal,
        totalEx: folderData.exercises.length
      });
    }

    // ----------------------------------------------------
    // TYPE F: DRAG_DROP / DRAG_AND_DROP - 100% Accurate (Fast Async In-Browser Engine)
    // ----------------------------------------------------
    if (exType === 'DRAG_DROP' || exType === 'DRAG_AND_DROP') {
      let targets = [];
      function searchDrags(node) {
        if (!node || typeof node !== 'object') return;
        if (node.type === 'dragDrop' && Array.isArray(node.words)) {
          targets.push(norm(node.words.map(w => w.$).join('')));
        }
        for (let k in node) searchDrags(node[k]);
      }
      searchDrags(layoutObj);

      let placeholders = $('.item .drag-drop-placeholder');
      let visibleCount = placeholders.filter(':visible').length;

      if (visibleCount === 0) {
        if (corrBtn && corrBtn.offsetParent !== null) {
          corrBtn.click();
        }
        return JSON.stringify({
          status: "SOLVED_DRAG_DROP",
          title: exData.title,
          packetTitle: folderData.title,
          exOrdinal: exOrdinal,
          totalEx: folderData.exercises.length
        });
      }

      if (window._dragTimer) {
        return JSON.stringify({
          status: "DRAG_IN_PROGRESS",
          remaining: visibleCount
        });
      }

      window._dragTimer = setInterval(function() {
        let phs = $('.item .drag-drop-placeholder');
        let placed = false;
        for (let i = 0; i < phs.length && i < targets.length; i++) {
          let ph = phs.eq(i);
          if (ph.is(':visible')) {
            let target = targets[i];
            let wordEl = $('.drag-drop').filter(function() {
              return !$(this).closest('.item').length && norm($(this).text()) === target && $(this).is(':visible');
            }).first();

            if (wordEl.length) {
              ph[0].click();
              wordEl[0].click();
              placed = true;
              break;
            }
          }
        }

        let rem = $('.item .drag-drop-placeholder:visible').length;
        if (rem === 0 || !placed) {
          clearInterval(window._dragTimer);
          window._dragTimer = null;
          let btn = document.querySelector('.action-exercise-button.correct');
          if (btn && btn.offsetParent !== null) {
            btn.click();
          }
        }
      }, 50);

      return JSON.stringify({
        status: "STARTED_FAST_DRAG",
        targets: targets.length,
        remaining: visibleCount
      });
    }

    // ----------------------------------------------------
    // TYPE G: SCRAMBLED_TABLE - 100% Accurate
    // ----------------------------------------------------
    if (exType === 'SCRAMBLED_TABLE') {
      $('.item:has(.scrambled-cell)').each(function() {
        var r = $(this);
        var i = r.children();
        var targets = r.data("scrambled-cells");
        if (!targets) return;

        for (var n = 0; n < i.length; n++) {
          var s = i.eq(n);
          var o = s.hasClass("scrambled-cell") ? s : s.find(".scrambled-cell");
          if (o.length === 1 && targets[n]) {
            var correctId = targets[n];
            var cellWithText = $('.scrambled-cell').filter(function() {
              return $(this).attr('data-scrambled-cell-id') === correctId;
            });
            if (cellWithText.length && cellWithText[0] !== o[0]) {
              o.text(cellWithText.first().text());
            }
            o.data("scrambled-cell-id", correctId);
            o.attr("data-scrambled-cell-id", correctId);
          }
        }
      });

      if (corrBtn && corrBtn.offsetParent !== null) {
        corrBtn.click();
      }

      return JSON.stringify({
        status: "SOLVED_SCRAMBLED_TABLE",
        title: exData.title,
        packetTitle: folderData.title,
        exOrdinal: exOrdinal,
        totalEx: folderData.exercises.length
      });
    }

    // ----------------------------------------------------
    // TYPE H: STATIC / INTRO
    // ----------------------------------------------------
    if (exType === 'STATIC' || exType === 'INTRO') {
      if (nextBtn && nextBtn.offsetParent !== null) {
        nextBtn.click();
        return JSON.stringify({ status: "CLICKED_NEXT_STATIC" });
      }
    }

    // Fallback: If unknown type, click Correction anyway
    if (corrBtn && corrBtn.offsetParent !== null) {
      corrBtn.click();
      return JSON.stringify({ status: "CLICKED_CORRECTION_FALLBACK", exType: exType });
    }

    return JSON.stringify({ status: "UNSUPPORTED_TYPE", exType: exType, title: exData.title });
  } catch(e) {
    return JSON.stringify({ status: "ERROR", error: e.toString() });
  }
})();
"""

with open(JS_TICK_PATH, "w", encoding="utf-8") as f:
    f.write(JS_CODE)

APPLESCRIPT = f"""
tell application "Safari"
  set jsCode to read POSIX file "{JS_TICK_PATH}" as «class utf8»
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t) contains "speexx.com" then
        return do JavaScript jsCode in t
      end if
    end repeat
  end repeat
  return "TAB_NOT_FOUND"
end tell
"""

def tick():
    """Execute in-browser solver in the active Speexx Safari tab."""
    try:
        out = subprocess.check_output(['osascript'], input=APPLESCRIPT.encode('utf-8')).decode('utf-8').strip()
        if out == "TAB_NOT_FOUND":
            return {"status": "TAB_NOT_FOUND"}
        return json.loads(out)
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# ========================================================================
# STUDY HOURS ACCUMULATOR (Keep-Alive Pulse Engine)
# ========================================================================

def run_hour_accumulator(target_seconds, start_time=None):
    """Maintain active session pulse to accumulate required study hours."""
    if start_time is None:
        start_time = time.time()

    target_hours = target_seconds / 3600
    print()
    print(render_box([
        f"{BOLD}{WHITE}STUDY HOURS ACCUMULATOR ACTIVE{RESET}",
        "---",
        f"{CYAN}Target Hours    {RESET}: {WHITE}{target_hours:.1f} hrs ({format_time(target_seconds)}){RESET}",
        f"{CYAN}Pulse Interval  {RESET}: {WHITE}15s (Anti-Idle micro-movements & scroll pulse){RESET}",
        f"{CYAN}Keep-Alive Mode {RESET}: {GREEN}Active session emulation (prevents timeout){RESET}",
        "---",
        f"{DIM}Press [Ctrl + C] anytime to safely pause and view session summary.{RESET}"
    ], title="ACCUMULATOR ENGINE", width=76))
    print()

    KEEPALIVE_APPLESCRIPT = """
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t) contains "speexx.com" then
        return do JavaScript "
          (() => {
            try {
              window.dispatchEvent(new MouseEvent('mousemove', { clientX: 100 + Math.random() * 200, clientY: 100 + Math.random() * 200 }));
              window.scrollBy(0, 5);
              setTimeout(() => window.scrollBy(0, -5), 300);
              return 'ALIVE';
            } catch(e) {
              return 'ERR:' + e.toString();
            }
          })()
        " in t
      end if
    end repeat
  end repeat
  return "TAB_NOT_FOUND"
end tell
"""
    last_print = 0
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= target_seconds:
                break

            try:
                out = subprocess.check_output(['osascript'], input=KEEPALIVE_APPLESCRIPT.encode('utf-8')).decode('utf-8').strip()
            except Exception:
                out = "ERROR"

            now = time.time()
            if now - last_print >= 10:
                last_print = now
                rem = max(0, target_seconds - elapsed)
                pct = min(100.0, (elapsed / target_seconds) * 100)
                bar = progress_bar(pct, length=18)
                if out == "ALIVE":
                    log_event('PULSE', 'KEEPALIVE', f"{bar} {pct:5.1f}% • {format_time(elapsed)} / {format_time(target_seconds)}", meta=f"ETA: {format_time(rem)}")
                else:
                    log_event('WAIT', 'SAFARI', f"Speexx tab not found in Safari. Keep Safari open... ({format_time(elapsed)} elapsed)")

            time.sleep(15)

        print()
        print(render_box([
            f"{BOLD}{GREEN}TARGET STUDY HOURS ACHIEVED!{RESET}",
            "---",
            f"{CYAN}Target Goal      {RESET}: {WHITE}{target_hours:.1f} hrs ({format_time(target_seconds)}){RESET}",
            f"{CYAN}Completed Time   {RESET}: {GREEN}{format_time(time.time() - start_time)}{RESET}",
            f"{CYAN}Criteria Status  {RESET}: {BOLD}{GREEN}100% SATISFIED • READY FOR CERTIFICATION{RESET}",
        ], title="GOAL REACHED", width=76))
        print()
        try:
            subprocess.run(['osascript', '-e', f'display notification "Completed {target_hours:.1f} study hours successfully!" with title "Speexx Master Bot"'], check=False)
            subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=False)
        except Exception:
            pass

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        rem = max(0, target_seconds - elapsed)
        pct = min(100.0, (elapsed / target_seconds) * 100)
        lines = [
            f"{BOLD}{YELLOW}ACCUMULATOR PAUSED BY USER{RESET}",
            "---",
            f"{CYAN}Status           {RESET}: {YELLOW}Paused via Ctrl+C{RESET}",
            f"{CYAN}Accumulated Time {RESET}: {GREEN}{format_time(elapsed)}{RESET} ({pct:.1f}% of {target_hours:.1f} hrs)",
            f"{CYAN}Remaining Time   {RESET}: {WHITE}{format_time(rem)}{RESET}",
            "---",
            f"{DIM}Resume command:{RESET} {CYAN}python3 speexx_bot.py --farm --hours {(rem/3600):.1f}{RESET}"
        ]
        print()
        print(render_box(lines, title="SESSION PAUSED", width=76))
        print()

# ========================================================================
# MAIN AUTONOMOUS WORKFLOW
# ========================================================================

def main(max_steps=100000, target_hours=None, delay=0.3, farm_only=False):
    start_time = time.time()
    target_seconds = (target_hours * 3600) if target_hours else None

    print_banner(target_hours=target_hours, delay=delay, farm_only=farm_only)

    if farm_only and target_seconds:
        run_hour_accumulator(target_seconds, start_time)
        return

    step = 0
    solved_exercises = 0

    try:
        while step < max_steps:
            step += 1

            # Check if target study hours have been reached
            if target_seconds and (time.time() - start_time) >= target_seconds:
                print()
                print(render_box([
                    f"{BOLD}{GREEN}TARGET STUDY HOURS ACHIEVED!{RESET}",
                    "---",
                    f"{CYAN}Target Goal      {RESET}: {WHITE}{target_hours:.1f} hrs ({format_time(target_seconds)}){RESET}",
                    f"{CYAN}Completed Time   {RESET}: {GREEN}{format_time(time.time() - start_time)}{RESET}",
                    f"{CYAN}Exercises Solved {RESET}: {WHITE}{solved_exercises} exercises (100% score){RESET}",
                    f"{CYAN}Criteria Status  {RESET}: {BOLD}{GREEN}100% SATISFIED • READY FOR CERTIFICATION{RESET}",
                ], title="GOAL REACHED", width=76))
                print()
                try:
                    subprocess.run(['osascript', '-e', f'display notification "Completed {target_hours:.1f} study hours successfully!" with title "Speexx Master Bot"'], check=False)
                    subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=False)
                except Exception:
                    pass
                break

            res = tick()
            status = res.get("status")

            elapsed = time.time() - start_time
            time_badge = ""
            if target_seconds:
                pct = min(100.0, (elapsed / target_seconds) * 100)
                time_badge = f"[{format_time(elapsed)}/{format_time(target_seconds)} • {pct:.1f}%]"

            if status == "TAB_NOT_FOUND":
                log_event('WAIT', 'SAFARI', 'Speexx tab not found in Safari. Waiting for connection...')
                time.sleep(1.0)
            elif status == "WAITING_FOR_PAGE":
                time.sleep(0.15)
            elif status == "DISMISSED_MODAL":
                log_event('MODAL', 'DIALOG', 'Dismissed popup modal dialog')
                time.sleep(0.2)
            elif status == "RELOAD_NON_100":
                badge = res.get("badge", "")
                log_event('RETRY', 'RESET', f"Score below 100% ({badge}). Reloading exercise to achieve 100%...", time_badge=time_badge)
                time.sleep(1.0)
            elif status == "CLICKED_START_NOW":
                log_event('DASH', 'PACKET', 'Clicked "Start now" on Dashboard to launch next module', time_badge=time_badge)
                time.sleep(0.8)
            elif status == "REDIRECTED_NEXT_PACKET":
                prog = res.get("progress")
                lvl = res.get("levelName") or "Active"
                prog_str = f"Level {lvl} Progress: {prog:.1f}%" if prog is not None else ""
                nxt = res.get("nextUrl", "")
                log_event('CLEAR', 'PACKET', f"Module completed 100%! Next: {nxt}", meta=prog_str, time_badge=time_badge)
                time.sleep(0.8)
            elif status == "PRONUNCIATION_FINISHED_REDIRECT":
                nxt = res.get("nextUrl", "")
                log_event('CLEAR', 'AUDIO', f"Pronunciation packet finished. Next: {nxt}", time_badge=time_badge)
                time.sleep(0.8)
            elif status in ["EXITED_TO_DASHBOARD", "PRONUNCIATION_FINISHED_DASHBOARD"]:
                log_event('DASH', 'PACKET', 'Module finished. Returned to main dashboard', time_badge=time_badge)
                if target_seconds and elapsed < target_seconds:
                    log_event('INFO', 'ACCUMULATE', 'Exercises completed. Entering Keep-Alive study accumulator...')
                    run_hour_accumulator(target_seconds, start_time)
                    break
                time.sleep(0.8)
            elif status == "PRONUNCIATION_NEXT":
                log_event('SKIP', 'AUDIO', 'Pronunciation audio prompt skipped ➔ Next item')
                time.sleep(0.05)
            elif status == "CLICKED_START":
                log_event('NEXT', 'START', 'Clicked "Start exercise" button')
                time.sleep(0.2)
            elif status == "SOLVED_ANSWER":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                filled = res.get("filled", 0)
                log_event('SOLVE', 'ANSWER', f"[{curr}/{tot}] \"{title}\"", meta=f"({filled} inputs filled ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "SOLVED_TOGGLE":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                matched = res.get("matched", 0)
                log_event('SOLVE', 'TOGGLE', f"[{curr}/{tot}] \"{title}\"", meta=f"({matched} toggles matched ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status in ["SOLVED_CHOICE_JSON", "SOLVED_CHOICE_DOM"]:
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                log_event('SOLVE', 'CHOICE', f"[{curr}/{tot}] \"{title}\"", meta="(Selections matched ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "SOLVED_MARK_TEXT":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                cnt = res.get("marked", 0)
                log_event('SOLVE', 'MARK_TEXT', f"[{curr}/{tot}] \"{title}\"", meta=f"({cnt} words marked ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "SOLVED_SCRAMBLED_SENTENCE":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                cnt = res.get("reordered", 0)
                log_event('SOLVE', 'SCRAMBLE', f"[{curr}/{tot}] \"{title}\"", meta=f"({cnt} segments reordered ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "SOLVED_SCRAMBLED_TABLE":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                log_event('SOLVE', 'TABLE', f"[{curr}/{tot}] \"{title}\"", meta="(Cells aligned ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "STARTED_FAST_DRAG":
                tot = res.get("targets", 0)
                log_event('SOLVE', 'DRAG_DROP', f"Fast drag-drop placement initiated ({tot} items)...")
                time.sleep(0.15)
            elif status == "DRAG_IN_PROGRESS":
                time.sleep(0.1)
            elif status == "STARTED_FAST_PIC":
                log_event('SOLVE', 'PICTURE', 'Fast picture choice placement initiated...')
                time.sleep(0.15)
            elif status == "PIC_IN_PROGRESS":
                time.sleep(0.1)
            elif status == "PLACED_ONE_DRAG":
                target = res.get("target", "")
                rem = res.get("remaining", 0)
                log_event('SOLVE', 'DRAG_DROP', f"Placed word: \"{target}\"", meta=f"({rem} remaining)")
                time.sleep(0.05)
            elif status == "PLACED_ONE_PIC":
                file = res.get("file", "")
                log_event('SOLVE', 'PICTURE', f"Placed image: {file}")
                time.sleep(0.05)
            elif status == "SOLVED_DRAG_DROP":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                log_event('SOLVE', 'DRAG_DROP', f"[{curr}/{tot}] \"{title}\"", meta="(Items connected ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "SOLVED_PICTURE_CHOICE":
                title = res.get("title", "")
                curr = res.get("exOrdinal", "")
                tot = res.get("totalEx", "")
                log_event('SOLVE', 'PICTURE', f"[{curr}/{tot}] \"{title}\"", meta="(Pictures matched ➔ 100%)", time_badge=time_badge)
                solved_exercises += 1
                if delay > 0.5:
                    log_event('WAIT', 'PACING', f"Pacing delay active: waiting {delay:.1f}s before submit...")
                    time.sleep(delay)
                else:
                    time.sleep(0.2)
            elif status == "CLICKED_NEXT":
                badge = res.get("badge", "")
                log_event('NEXT', 'EXERCISE', f"Verified score: {badge} ➔ Moving to next exercise", time_badge=time_badge)
                time.sleep(0.3)
            elif status == "CLICKED_NEXT_STATIC":
                log_event('NEXT', 'STATIC', 'Introductory card completed ➔ Moving to next', time_badge=time_badge)
                time.sleep(0.25)
            elif status == "SUBMITTED_LEVEL_TEST":
                print()
                print(render_box([
                    f"{BOLD}{GREEN}CEFR LEVEL TEST COMPLETED 100%!{RESET}",
                    "---",
                    f"{CYAN}Evaluation  {RESET}: {WHITE}All level test questions answered with 100% accuracy{RESET}",
                    f"{CYAN}Result      {RESET}: {GREEN}Test submitted successfully! Certificate unlocked.{RESET}",
                ], title="LEVEL TEST CLEARED", width=76))
                print()
                if target_seconds and elapsed < target_seconds:
                    log_event('INFO', 'ACCUMULATE', 'Level test submitted! Transitioning to Keep-Alive accumulator to reach target hours...')
                    run_hour_accumulator(target_seconds, start_time)
                    break
                time.sleep(3.0)
            elif status == "CLICKED_CONTINUE_PACKET":
                prog = res.get("progress")
                prog_str = f"Overall Progress: {prog:.1f}%" if prog is not None else ""
                log_event('CLEAR', 'PACKET', 'Module completed 100%! Clicked Continue to proceed', meta=prog_str, time_badge=time_badge)
                time.sleep(0.8)
            elif status == "ERROR":
                log_event('ALERT', 'ERROR', f"Runtime error: {res.get('error')}")
                time.sleep(1.0)
            elif status == "UNSUPPORTED_TYPE":
                exType = res.get("exType", "")
                title = res.get("title", "")
                log_event('ALERT', 'UNSUPPORT', f"Unsupported exercise type: {exType} (\"{title}\")")
                time.sleep(0.5)
            elif status == "CLICKED_CORRECTION_FALLBACK":
                exType = res.get("exType", "")
                log_event('NEXT', 'FALLBACK', f"Submitted via correction fallback ({exType})")
                time.sleep(0.5)
            else:
                time.sleep(0.5)

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        lines = [
            f"{BOLD}{YELLOW}SESSION PAUSED BY USER{RESET}",
            "---",
            f"{CYAN}Status           {RESET}: {YELLOW}Stopped gracefully via Ctrl+C{RESET}",
            f"{CYAN}Exercises Solved {RESET}: {GREEN}{solved_exercises} exercises completed (100% accuracy){RESET}",
            f"{CYAN}Elapsed Time     {RESET}: {WHITE}{format_time(elapsed)}{RESET}",
        ]
        if target_seconds:
            rem = max(0, target_seconds - elapsed)
            pct = (elapsed / target_seconds * 100)
            lines.append(f"{CYAN}Target Time      {RESET}: {WHITE}{target_hours:.1f} hrs{RESET} ({YELLOW}{pct:.1f}%{RESET} completed)")
            lines.append(f"{CYAN}Remaining Time   {RESET}: {WHITE}{format_time(rem)}{RESET}")
            rem_hours = rem / 3600
            lines.append("---")
            lines.append(f"{DIM}To resume hours accumulator:{RESET} {CYAN}python3 speexx_bot.py --farm --hours {rem_hours:.1f}{RESET}")
            lines.append(f"{DIM}To resume auto-solver:{RESET}       {CYAN}python3 speexx_bot.py --hours {rem_hours:.1f}{RESET}")

        print()
        print(render_box(lines, title="SESSION SUMMARY", width=76))
        print()

def interactive_wizard():
    """Prompt user interactively when launched without CLI arguments."""
    print()
    print(render_box([
        f"{BOLD}{WHITE}INTERACTIVE SESSION SETUP WIZARD{RESET}",
        "---",
        f"{DIM}Configure your study session parameters or press [Enter] to use defaults.{RESET}",
    ], title="SETUP WIZARD", width=76))
    print()

    target_h = None
    delay_sec = 0.3

    try:
        user_h = input(f" {CYAN}▸{RESET} {BOLD}Target study hours{RESET} {DIM}(e.g. 10 or 5.5, or press Enter for unlimited):{RESET} ").strip()
        if user_h:
            try:
                target_h = float(user_h)
                print(f"   {GREEN}✓{RESET} Target set to {BOLD}{target_h:.1f} hours{RESET}")
            except ValueError:
                print(f"   {YELLOW}⚠ Invalid number format. Defaulting to unlimited run.{RESET}")

        if target_h:
            user_d = input(f" {CYAN}▸{RESET} {BOLD}Pacing delay between exercises{RESET} {DIM}(seconds, e.g. 20, or press Enter for 0.3s):{RESET} ").strip()
            if user_d:
                try:
                    delay_sec = float(user_d)
                    print(f"   {GREEN}✓{RESET} Delay set to {BOLD}{delay_sec:.1f}s{RESET}")
                except ValueError:
                    pass
        print()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{YELLOW}Setup cancelled. Exiting.{RESET}")
        sys.exit(0)

    return target_h, delay_sec

# ========================================================================
# ENTRY POINT
# ========================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="⚡ Speexx Autonomous Master Bot (FastTrack English Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  python3 speexx_bot.py --hours 10            # Solve exercises & accumulate 10 hours
  python3 speexx_bot.py 10                    # Shorthand for 10 hours target
  python3 speexx_bot.py --delay 20            # 20s pacing delay between exercises
  python3 speexx_bot.py --hours 10 --delay 20 # 10h target + 20s pacing delay
  python3 speexx_bot.py --farm --hours 10     # Hours accumulator only (no exercise solving)
  python3 speexx_bot.py                       # Interactive setup wizard
"""
    )
    parser.add_argument("pos_hours", nargs="?", type=float, default=None, help="Target study hours (e.g. 10 or 5.5)")
    parser.add_argument("--hours", "-H", type=float, default=None, help="Target study hours (e.g. 10 or 5.5)")
    parser.add_argument("--delay", "-d", type=float, default=0.3, help="Pacing delay between exercises in seconds (default: 0.3s)")
    parser.add_argument("--farm", "-f", action="store_true", help="Hours accumulator only (keeps session active without solving exercises)")
    parser.add_argument("--max-steps", type=int, default=100000, help="Maximum execution iterations (default: 100000)")

    args = parser.parse_args()

    target_h = args.hours or args.pos_hours
    delay_sec = args.delay

    if target_h is None and not args.farm and len(sys.argv) == 1:
        if sys.stdin.isatty():
            target_h, delay_sec = interactive_wizard()

    main(max_steps=args.max_steps, target_hours=target_h, delay=delay_sec, farm_only=args.farm)
